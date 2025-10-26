import discord
from discord.ext import commands
from discord import app_commands
import database  # Импортируем наш модуль для работы с БД


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="добавить", description="Добавить новую задачу с ключом и текстом")
    @app_commands.describe(key="Уникальный ключ для задачи (например, 'купить_хлеб')", task_text="Текст задачи")
    async def add_task_command(self, interaction: discord.Interaction, key: str, task_text: str):
        author_id = interaction.user.id

        # Проверяем длину ключа
        if len(key) > 50:  # Пример ограничения длины ключа
            await interaction.response.send_message(
                "Ключ задачи слишком длинный. Пожалуйста, используйте до 50 символов.", ephemeral=True)
            return

        # Проверяем, что ключ не содержит пробелов или специальных символов, если это требуется
        # if not key.isalnum() and '_' not in key:
        #     await interaction.response.send_message("Ключ задачи должен состоять только из букв, цифр и нижнего подчеркивания.", ephemeral=True)
        #     return

        if database.add_task(key.lower(), task_text,
                             author_id):  # key.lower() для унификации, чтобы "КУПИТЬ_ХЛЕБ" и "купить_хлеб" были одним и тем же
            await interaction.response.send_message(
                f"Задача с ключом `{key}` и текстом '{task_text}' успешно добавлена!", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"Задача с ключом `{key}` уже существует. Пожалуйста, выберите другой ключ.", ephemeral=True)

    @app_commands.command(name="удалить", description="Удалить задачу по ключу")
    @app_commands.describe(key="Ключ задачи, которую нужно удалить")
    async def delete_task_command(self, interaction: discord.Interaction, key: str):
        if database.delete_task_by_key(key.lower()):
            await interaction.response.send_message(f"Задача с ключом `{key}` успешно удалена.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Задача с ключом `{key}` не найдена.", ephemeral=True)

    @app_commands.command(name="задачи", description="Показать список всех задач")
    async def list_all_tasks_command(self, interaction: discord.Interaction):
        tasks = database.get_all_tasks()  # Получаем все задачи

        if not tasks:
            await interaction.response.send_message("Список задач пуст.", ephemeral=True)
            return

        task_list_str = "Список задач:\n"
        # Для отображения автора, нам нужно получить имя пользователя по ID.
        # Это требует запроса к API Discord, что может быть медленно для большого списка.
        # Пока просто выводим ID, но можно расширить.
        for key, text, author_id in tasks:
            # Попытка получить объект пользователя, чтобы отобразить его имя
            author_member = interaction.guild.get_member(author_id)  # Получаем пользователя из кэша гильдии
            author_name = author_member.display_name if author_member else f"ID: {author_id}"

            task_list_str += f"**`{key}`**: {text} (Автор: {author_name})\n"

        # Проверяем, что сообщение не превышает лимит Discord (2000 символов)
        if len(task_list_str) > 2000:
            await interaction.response.send_message("Список задач слишком длинный. Отображены только первые задачи.",
                                                    ephemeral=True)
            # Можно реализовать пагинацию или отправку в файле
            await interaction.followup.send(task_list_str[:1900] + "...", ephemeral=True)
        else:
            await interaction.response.send_message(task_list_str, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tasks(bot))