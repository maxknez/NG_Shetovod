import discord
from discord.ext import commands
from discord import app_commands
import random
import settings
import database


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task_list_message_id = None

    async def send_startup_greeting(self):
        Greetings = ["Я жив!", "Привет, бандиты", "Снова в строю!", "Бот готов к работе!"]

        if settings.CHANNEL_ID:
            channel = self.bot.get_channel(settings.CHANNEL_ID)
            if channel:
                try:
                    await channel.send(random.choice(Greetings))
                    print(f"Отправлено приветствие в канал {channel.name} ({settings.CHANNEL_ID})")
                except discord.Forbidden:
                    print(f"Ошибка: Нет прав для отправки сообщения в канал {channel.name} ({settings.CHANNEL_ID})")
                except discord.HTTPException as e:
                    print(f"Ошибка при отправке приветствия: {e}")
            else:
                print(f"Канал с ID {settings.CHANNEL_ID} не найден для приветствия.")
        else:
            print("CHANNEL_ID не указан в settings.py, приветствие не будет отправлено.")

    async def get_or_create_task_list_message(self):
        """
        Ищет существующее сообщение со списком активных задач или создает новое.
        Сохраняет ID сообщения.
        """
        if not settings.CHANNEL_ID:
            print("CHANNEL_ID не указан, сообщение со списком задач не будет управляться.")
            return

        channel = self.bot.get_channel(settings.CHANNEL_ID)
        if not channel:
            print(f"Канал с ID {settings.CHANNEL_ID} не найден для управления списком задач.")
            return

        try:
            async for message in channel.history(limit=100):
                # Ищем сообщение, которое начинается с "📋 Актуальные задачи:"
                if message.author == self.bot.user and message.content.startswith("📋 Актуальные задачи:"):
                    self.task_list_message_id = message.id
                    print(f"Найденное сообщение со списком активных задач: {self.task_list_message_id}")
                    await self.update_active_tasks_message()  # Обновляем его сразу
                    return
        except discord.Forbidden:
            print(f"Ошибка: Нет прав для чтения истории сообщений в канале {channel.name} ({settings.CHANNEL_ID})")
            return
        except discord.HTTPException as e:
            print(f"Ошибка при поиске сообщения со списком активных задач: {e}")
            return

        try:
            sent_message = await channel.send("📋 Актуальные задачи: Загрузка...")
            self.task_list_message_id = sent_message.id
            print(f"Создано новое сообщение со списком активных задач: {self.task_list_message_id}")
            await self.update_active_tasks_message()  # Обновляем его сразу
        except discord.Forbidden:
            print(f"Ошибка: Нет прав для отправки сообщения в канал {channel.name} ({settings.CHANNEL_ID})")
        except discord.HTTPException as e:
            print(f"Ошибка при создании сообщения со списком активных задач: {e}")

    async def update_active_tasks_message(self):
        """Редактирует сообщение со списком активных задач (todo и assigned)."""
        if not self.task_list_message_id or not settings.CHANNEL_ID:
            return

        channel = self.bot.get_channel(settings.CHANNEL_ID)
        if not channel:
            print(f"Канал с ID {settings.CHANNEL_ID} не найден для обновления списка задач.")
            return

        try:
            message_to_edit = await channel.fetch_message(self.task_list_message_id)
            tasks = database.get_active_tasks()  # Получаем только активные задачи

            task_list_content = "📋 **Актуальные задачи:** 📋\n\n"
            if not tasks:
                task_list_content += "Список задач пуст."
            else:
                for key, text, author_id, assigned_to_id, status in tasks:
                    author_member = channel.guild.get_member(author_id)
                    author_name = author_member.display_name if author_member else f"ID: {author_id}"

                    status_emoji = ""
                    if status == 'todo':
                        status_emoji = "⚪"
                    elif status == 'assigned':
                        status_emoji = "🟠"

                    assigned_text = ""
                    if assigned_to_id:
                        assigned_member = channel.guild.get_member(assigned_to_id)
                        assigned_name = assigned_member.display_name if assigned_member else f"ID: {assigned_to_id}"
                        assigned_text = f" -> {assigned_name}"

                    task_list_content += f"{status_emoji} **`{key}`**: {text} (Автор: {author_name}{assigned_text})\n"

            if len(task_list_content) > 2000:
                task_list_content = task_list_content[:1950] + "\n...(список урезан)"

            await message_to_edit.edit(content=task_list_content)
            print("Сообщение со списком активных задач обновлено.")
        except discord.NotFound:
            print(
                f"Сообщение со списком активных задач с ID {self.task_list_message_id} не найдено. Попытка создать новое.")
            self.task_list_message_id = None
            await self.get_or_create_task_list_message()
        except discord.Forbidden:
            print(
                f"Ошибка: Нет прав для редактирования сообщения с ID {self.task_list_message_id} в канале {channel.name} ({settings.CHANNEL_ID})")
        except discord.HTTPException as e:
            print(f"Ошибка при обновлении сообщения со списком активных задач: {e}")

    @app_commands.command(name="ping", description="Проверяет задержку бота")
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Задержка: {latency_ms}ms")
        print(f"Команда /ping выполнена пользователем {interaction.user.display_name}. Задержка: {latency_ms}ms")


async def setup(bot):
    await bot.add_cog(Utils(bot))