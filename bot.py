import discord
from discord.ext import commands
from config.settings import TOKEN, VERSION
import asyncio
from database.db import init_db

# Инициализация intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Асинхронная инициализация базы данных
async def setup_db():
    await asyncio.to_thread(init_db)
    print("База данных инициализирована!")

# Событие при готовности бота
@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    print(f"Версия: {VERSION}")
    print(f"Подключен к {len(bot.guilds)} серверам")

async def main():
    await setup_db()

    # Здесь подключаем все cogs
    await bot.load_extension("cogs.tasks")
    await bot.load_extension("cogs.rating")
    # await bot.load_extension("cogs.utils")

    await bot.start(TOKEN)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
