import discord
from discord.ext import commands
from config.settings import TOKEN, VERSION
from database.db import init_db

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Бот запущен (версия {VERSION}) — {bot.user}")
    await bot.wait_until_ready()
    # Можно написать в лог или канал "я жив!"
    for guild in bot.guilds:
        print(f"Подключён к серверу: {guild.name}")

async def load_cogs():
    await bot.load_extension("cogs.tasks")
    await bot.load_extension("cogs.rating")

if __name__ == "__main__":
    init_db()
    bot.loop.run_until_complete(load_cogs())
    bot.run(TOKEN)
