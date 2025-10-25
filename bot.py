import os
import discord
from discord import app_commands
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Настройка клиента
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Событие запуска
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Бот {bot.user} запущен и готов к работе")

    # Отправляем сообщение в указанный канал
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("я жив, сучки!")
    else:
        print("❗ Канал не найден. Проверь CHANNEL_ID в .env")

# Команда /пинг
@tree.command(name="пинг", description="Проверить задержку бота")
async def ping_command(interaction: discord.Interaction):
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"Понг! Задержка {latency_ms} мс")

# Запуск бота
bot.run(TOKEN)
