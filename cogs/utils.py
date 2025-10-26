import discord
from discord.ext import commands
from discord import app_commands

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Проверяет задержку бота")
    async def ping(self, interaction: discord.Interaction):
        """
        Отвечает текущей задержкой бота (latency).
        """
        # Задержка (latency) измеряется в секундах, умножаем на 1000 для миллисекунд
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Задержка: {latency_ms}ms")

async def setup(bot):
    await bot.add_cog(Utils(bot))