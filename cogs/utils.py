import discord
from discord.ext import commands
from discord import app_commands
import random
import settings
import database  # Для получения списка задач


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task_list_message_id = None  # ID сообщения со списком задач

    async def send_startup_greeting(self):
        """Отправляет случайное приветствие в указанный канал при запуске."""
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
                print(f"Канал с ID {settings.CHANNEL_ID} не найден.")
        else:
            print("CHANNEL_ID не указан в settings.py, приветствие не будет отправлено.")

    async def get_or_create_task_list_message(self):
        """
        Ищет существующее сообщение со списком задач или создает новое.
        Сохраняет ID сообщения.
        """
        if not settings.CHANNEL_ID:
            print("CHANNEL_ID не указан, сообщение со списком задач не будет управляться.")
            return

        channel = self.bot.get_channel(settings.CHANNEL_ID)
        if not channel:
            print(f"Канал с ID {settings.CHANNEL_ID} не найден.")
            return

        # Попытка найти предыдущее сообщение со списком задач
        # Ищем в последних N сообщениях (например, 100)
        try:
            async for message in channel.history(limit=100):
                if message.author == self.bot.user and message.content.startswith("Актуальные задачи:"):
                    self.task_list_message_id = message.id
                    print(f"Найденное сообщение со списком задач: {self.task_list_message_id}")
                    await self.update_task_list_message()  # Обновляем его сразу
                    return
        except discord.Forbidden:
            print(f"Ошибка: Нет прав для чтения истории сообщений в канале {channel.name} ({settings.CHANNEL_ID})")
            return
        except discord.HTTPException as e:
            print(f"Ошибка при поиске сообщения со списком задач: {e}")
            return

        # Если сообщение не найдено, создаем новое
        try:
            sent_message = await channel.send("Актуальные задачи: Загрузка...")
            self.task_list_message_id = sent_message.id
            print(f"Создано новое сообщение со списком задач: {self.task_list_message_id}")
            await self.update_task_list_message()  # Обновляем его сразу
        except discord.Forbidden:
            print(f"Ошибка: Нет прав для отправки сообщения в канал {channel.name} ({settings.CHANNEL_ID})")
        except discord.HTTPException as e:
            print(f"Ошибка при создании сообщения со списком задач: {e}")

    async def update_task_list_message(self):
        """Редактирует сообщение со списком задач, обновляя его содержимое."""
        if not self.task_list_message_id or not settings.CHANNEL_ID:
            # print("ID сообщения со списком задач или CHANNEL_ID не заданы, обновление невозможно.")
            return

        channel = self.bot.get_channel(settings.CHANNEL_ID)
        if not channel:
            print(f"Канал с ID {settings.CHANNEL_ID} не найден для обновления списка задач.")
            return

        try:
            message_to_edit = await channel.fetch_message(self.task_list_message_id)
            tasks = database.get_all_tasks()  # Получаем все задачи

            task_list_content = "Актуальные задачи:\n\n"
            if not tasks:
                task_list_content += "Список задач пуст."
            else:
                for key, text, author_id in tasks:
                    author_member = channel.guild.get_member(author_id)
                    author_name = author_member.display_name if author_member else f"ID: {author_id}"
                    task_list_content += f"**`{key}`**: {text} (Автор: {author_name})\n"

            # Проверяем, что сообщение не превышает лимит Discord
            if len(task_list_content) > 2000:
                task_list_content = task_list_content[:1950] + "\n...(список урезан)"

            await message_to_edit.edit(content=task_list_content)
            print("Сообщение со списком задач обновлено.")
        except discord.NotFound:
            print(f"Сообщение со списком задач с ID {self.task_list_message_id} не найдено. Создаем новое.")
            self.task_list_message_id = None  # Сбрасываем ID, чтобы создать новое при следующем обновлении
            await self.get_or_create_task_list_message()  # Попытаемся создать новое
        except discord.Forbidden:
            print(f"Ошибка: Нет прав для редактирования сообщения в канале {channel.name} ({settings.CHANNEL_ID})")
        except discord.HTTPException as e:
            print(f"Ошибка при обновлении сообщения со списком задач: {e}")

    # Ваша существующая команда ping
    @app_commands.command(name="ping", description="Проверяет задержку бота")
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Задержка: {latency_ms}ms")


async def setup(bot):
    await bot.add_cog(Utils(bot))
    # После загрузки кога, бот сможет получить доступ к его методам
    # Мы будем вызывать send_startup_greeting и get_or_create_task_list_message из bot.py