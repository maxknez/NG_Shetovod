import discord
from discord.ext import commands
from discord import app_commands
import database


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _update_task_list(self):
        utils_cog = self.bot.get_cog("Utils")
        if utils_cog:
            await utils_cog.update_active_tasks_message()  # Изменено название функции
        else:
            print("Ошибка: Ког 'Utils' не найден при попытке обновить список задач.")

    @app_commands.command(name="добавить", description="Добавить новую задачу с ключом и текстом")
    @app_commands.describe(key="Уникальный ключ для задачи", task_text="Текст задачи")
    async def add_task_command(self, interaction: discord.Interaction, key: str, task_text: str):
        author_id = interaction.user.id

        if len(key) > 50:
            await interaction.response.send_message(
                "Ключ задачи слишком длинный. Пожалуйста, используйте до 50 символов.", ephemeral=True)
            return

        if database.add_task(key.lower(), task_text, author_id):
            await interaction.response.send_message(
                f"Задача с ключом `{key}` и текстом '{task_text}' успешно добавлена со статусом 'Надо сделать'!",
                ephemeral=True)
            await self._update_task_list()  # Обновляем список активных задач
        else:
            await interaction.response.send_message(
                f"Задача с ключом `{key}` уже существует. Пожалуйста, выберите другой ключ.", ephemeral=True)

    @app_commands.command(name="удалить", description="Удалить задачу по ключу")
    @app_commands.describe(key="Ключ задачи, которую нужно удалить")
    async def delete_task_command(self, interaction: discord.Interaction, key: str):
        task = database.get_task_by_key(key.lower())
        if not task:
            await interaction.response.send_message(f"Задача с ключом `{key}` не найдена.", ephemeral=True)
            return

        # Разрешаем удалять только автору или администраторам
        if task[
            3] == interaction.user.id or interaction.user.guild_permissions.manage_messages:  # task[3] это author_id
            if database.delete_task_by_key(key.lower()):
                await interaction.response.send_message(f"Задача с ключом `{key}` успешно удалена.", ephemeral=True)
                await self._update_task_list()  # Обновляем список активных задач
            else:
                await interaction.response.send_message(f"Не удалось удалить задачу с ключом `{key}`.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Вы не являетесь автором этой задачи и не имеете прав для её удаления.", ephemeral=True)

    @app_commands.command(name="взять", description="Взять задачу, присвоив её себе.")
    @app_commands.describe(key="Ключ задачи, которую вы хотите взять.")
    async def assign_task_command(self, interaction: discord.Interaction, key: str):
        task = database.get_task_by_key(key.lower())
        if not task:
            await interaction.response.send_message(f"Задача с ключом `{key}` не найдена.", ephemeral=True)
            return

        if task[5] == 'done':  # task[5] это status
            await interaction.response.send_message(f"Задача с ключом `{key}` уже выполнена.", ephemeral=True)
            return

        if task[5] == 'assigned':
            assigned_member = interaction.guild.get_member(task[4])  # task[4] это assigned_to_id
            assigned_name = assigned_member.display_name if assigned_member else "неизвестному пользователю"
            await interaction.response.send_message(f"Задача с ключом `{key}` уже назначена {assigned_name}.",
                                                    ephemeral=True)
            return

        if database.assign_task(key.lower(), interaction.user.id):
            await interaction.response.send_message(f"Вы взяли задачу с ключом `{key}`! Теперь она 'Назначена' вам.",
                                                    ephemeral=True)
            await self._update_task_list()  # Обновляем список активных задач
        else:
            await interaction.response.send_message(f"Не удалось взять задачу с ключом `{key}`.", ephemeral=True)

    @app_commands.command(name="закрыть", description="Закрыть выполненную задачу, получить очко рейтинга.")
    @app_commands.describe(key="Ключ задачи, которую вы хотите закрыть.")
    async def complete_task_command(self, interaction: discord.Interaction, key: str):
        task = database.get_task_by_key(key.lower())
        if not task:
            await interaction.response.send_message(f"Задача с ключом `{key}` не найдена.", ephemeral=True)
            return

        # Проверяем, что задача назначена этому пользователю
        if task[4] != interaction.user.id:  # task[4] это assigned_to_id
            await interaction.response.send_message(f"Вы можете закрыть только те задачи, которые 'Назначены' вам.",
                                                    ephemeral=True)
            return

        if task[5] == 'done':  # task[5] это status
            await interaction.response.send_message(f"Задача с ключом `{key}` уже была выполнена.", ephemeral=True)
            return

        if database.complete_task(key.lower(), interaction.user.id):
            database.add_rating_point(interaction.user.id)  # Добавляем очко рейтинга
            await interaction.response.send_message(
                f"Задача с ключом `{key}` успешно закрыта! Вы получили 1 очко рейтинга. 🎉", ephemeral=True)
            await self._update_task_list()  # Обновляем список активных задач
        else:
            await interaction.response.send_message(
                f"Не удалось закрыть задачу с ключом `{key}`. Убедитесь, что она назначена вам и не была выполнена.",
                ephemeral=True)

    @app_commands.command(name="выполненные", description="Показать список всех выполненных задач.")
    async def list_completed_tasks_command(self, interaction: discord.Interaction):
        tasks = database.get_tasks_by_status('done')

        if not tasks:
            await interaction.response.send_message("Список выполненных задач пуст.", ephemeral=True)
            return

        task_list_str = "✅ **Список выполненных задач:** ✅\n\n"
        for key, text, author_id, assigned_to_id, status in tasks:
            author_member = interaction.guild.get_member(author_id)
            author_name = author_member.display_name if author_member else f"ID: {author_id}"

            assigned_member = interaction.guild.get_member(assigned_to_id) if assigned_to_id else None
            assigned_name = assigned_member.display_name if assigned_member else "Никому"

            task_list_str += f"**`{key}`**: {text} (Автор: {author_name}, Выполнил: {assigned_name})\n"

        if len(task_list_str) > 2000:
            task_list_str = task_list_str[:1950] + "\n...(список урезан)"
            await interaction.response.send_message(
                "Список выполненных задач слишком длинный. Отображены только первые задачи.", ephemeral=True)
            await interaction.followup.send(task_list_str, ephemeral=True)  # Отправляем через followup
        else:
            await interaction.response.send_message(task_list_str, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tasks(bot))