from discord.ext import commands
from database import db

class Tasks(commands.Cog):
    """Работа с задачами: создание, просмотр, закрытие."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="создать")
    async def create_task(self, ctx, *, name: str):
        """Добавить новую задачу (пример текстовой команды, позже заменим на slash)."""
        await ctx.send(f"Задача '{name}' добавлена (заглушка).")

async def setup(bot):
    await bot.add_cog(Tasks(bot))
