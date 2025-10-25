import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import sqlite3
import asyncio

load_dotenv()
TOKEN = os.getenv("TOKEN")

# Инициализация intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

DB_PATH = "tasks.db"

# Асинхронная инициализация базы данных
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            key TEXT,
            description TEXT,
            author TEXT,
            user TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

async def setup_db():
    await asyncio.to_thread(init_db)
    print("База данных и таблица tasks готовы!")

# Событие при готовности бота
@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    # Отправка сообщения на первый доступный канал
    for guild in bot.guilds:
        if guild.text_channels:
            channel = guild.text_channels[0]
            await channel.send("Я жив!")
            break

async def main():
    await setup_db()

    # Здесь подключаем все cogs
    # await bot.load_extension("cogs.tasks")
    # await bot.load_extension("cogs.rating")

    await bot.start(TOKEN)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
