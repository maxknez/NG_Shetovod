import discord
from discord import app_commands
from discord.ext import commands
from database import db

class Tasks(commands.Cog):
    """Работа с задачами: создание, взятие, выполнение, удаление, список."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- Добавить задачу ---
    @app_commands.command(name="добавить", description="Добавить новую задачу")
    @app_commands.describe(key="Короткий ключ задачи", text="Описание задачи")
    async def add(self, interaction: discord.Interaction, key: str, text: str):
        try:
            db.add_task(key, text, interaction.user.id)
            await interaction.response.send_message(f"Задача '{key}' добавлена", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Ошибка при добавлении: {e}", ephemeral=True)

    # --- Взять задачу ---
    @app_commands.command(name="взять", description="Взять задачу себе")
    @app_commands.describe(key="Ключ задачи")
    async def take(self, interaction: discord.Interaction, key: str):
        success = db.take_task(key, interaction.user.id)
        if success:
            await interaction.response.send_message(f"Ты взял задачу '{key}'", ephemeral=True)
        else:
            await interaction.response.send_message(f"Задача '{key}' недоступна или уже взята", ephemeral=True)

    # --- Снять задачу ---
    @app_commands.command(name="снять", description="Снять задачу с себя")
    @app_commands.describe(key="Ключ задачи")
    async def drop(self, interaction: discord.Interaction, key: str):
        success = db.remove_task_user(key, interaction.user.id)
        if success:
            await interaction.response.send_message(f"Ты снял задачу '{key}'", ephemeral=True)
        else:
            await interaction.response.send_message(f"Ты не можешь снять эту задачу", ephemeral=True)

    # --- Сделал задачу ---
    @app_commands.command(name="сделал", description="Отметить задачу как выполненную")
    @app_commands.describe(key="Ключ задачи")
    async def done(self, interaction: discord.Interaction, key: str):
        success = db.complete_task(key, interaction.user.id)
        if success:
            await interaction.response.send_message(f"Задача '{key}' выполнена", ephemeral=True)
            # Тут можно добавить начисление рейтинга через rating.py
        else:
            await interaction.response.send_message(f"Ты не можешь выполнить эту задачу", ephemeral=True)

    # --- Удалить задачу ---
    @app_commands.command(name="удалить", description="Удалить задачу")
    @app_commands.describe(key="Ключ задачи")
    async def delete(self, interaction: discord.Interaction, key: str):
        success = db.delete_task(key)
        if success:
            await interaction.response.send_message(f"Задача '{key}' удалена", ephemeral=True)
        else:
            await interaction.response.send_message(f"Задача '{key}' не найдена", ephemeral=True)

    # --- Список задач ---
    @app_commands.command(name="задачи", description="Показать все задачи")
    async def list_tasks(self, interaction: discord.Interaction):
        tasks = db.list_tasks()
        if not tasks:
            await interaction.response.send_message("Список задач пуст", ephemeral=True)
            return

        msg = ""
        for t in tasks:
            user = f"<@{t[4]}>" if t[4] else "никто"
            msg += f"{t[1]} — {t[2]} — автор: <@{t[3]}> — взял: {user} — статус: {t[5]}\n"

        await interaction.response.send_message(msg, ephemeral=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tasks(bot))
