import os
import discord
from discord import app_commands
from dotenv import load_dotenv

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Настраиваем клиента
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Событие запуска
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Бот {bot.user} запущен и готов к работе")

# Простая команда /пинг
@tree.command(name="пинг", description="Проверить задержку бота")
async def ping_command(interaction: discord.Interaction):
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"Понг! Задержка {latency_ms} мс")

# Запуск бота
bot.run(TOKEN)