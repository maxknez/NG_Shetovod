import discord
from discord.ext import commands
from config.settings import TOKEN, VERSION
import asyncio
from database.db import init_db

# Инициализация intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Событие при готовности бота
@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    print(f"Версия: {VERSION}")
    print(f"Подключен к {len(bot.guilds)} серверам")

async def main():
    # Инициализация базы данных
    await init_db()  # Убрано asyncio.to_thread
    print("База данных инициализирована!")

    # Здесь подключаем все cogs
    await bot.load_extension("cogs.tasks")
    await bot.load_extension("cogs.rating")
    # await bot.load_extension("cogs.utils")

    await bot.start(TOKEN)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())