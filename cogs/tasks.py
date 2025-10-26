import discord
from discord.ext import commands
from discord import app_commands
import database


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _update_task_list(self):
        """Внутренняя вспомогательная функция для обновления сообщения со списком задач."""
        utils_cog = self.bot.get_cog("Utils")
        if utils_cog:
            await utils_cog.update_task_list_message()
        else:
            print("Ошибка: Ког 'Utils' не найден при попытке обновить список задач.")

    @app_commands.command(name="добавить", description="Добавить новую задачу с ключом и текстом")
    @app_commands.describe(key="Уникальный ключ для задачи (например, 'купить_хлеб')", task_text="Текст задачи")
    async def add_task_command(self, interaction: discord.Interaction, key: str, task_text: str):
        author_id = interaction.user.id

        if len(key) > 50:
            await interaction.response.send_message(
                "Ключ задачи слишком длинный. Пожалуйста, используйте до 50 символов.", ephemeral=True)
            return

        if database.add_task(key.lower(), task_text, author_id):
            await interaction.response.send_message(
                f"Задача с ключом `{key}` и текстом '{task_text}' успешно добавлена!", ephemeral=True)
            await self._update_task_list()  # Обновляем список после добавления
        else:
            await interaction.response.send_message(
                f"Задача с ключом `{key}` уже существует. Пожалуйста, выберите другой ключ.", ephemeral=True)

    @app_commands.command(name="удалить", description="Удалить задачу по ключу")
    @app_commands.describe(key="Ключ задачи, которую нужно удалить")
    async def delete_task_command(self, interaction: discord.Interaction, key: str):
        if database.delete_task_by_key(key.lower()):
            await interaction.response.send_message(f"Задача с ключом `{key}` успешно удалена.", ephemeral=True)
            await self._update_task_list()  # Обновляем список после удаления
        else:
            await interaction.response.send_message(f"Задача с ключом `{key}` не найдена.", ephemeral=True)

    @app_commands.command(name="задачи", description="Показать список всех задач")
    async def list_all_tasks_command(self, interaction: discord.Interaction):
        # Эта команда просто вызывает функцию, которая уже делает то же самое
        await self._update_task_list()
        # Отправляем подтверждение, что список обновлен (или показываем пользователю прямо)
        # Если ephemeral=True, то обновление основного сообщения невидимо для пользователя.
        # Можно отправить ephemeral-ссылку на основное сообщение.
        if settings.CHANNEL_ID:
            await interaction.response.send_message(f"Список задач обновлен в канале <#{settings.CHANNEL_ID}>",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Список задач обновлен.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tasks(bot))