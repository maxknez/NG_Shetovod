import asyncio
from discord.ext import commands
from config.settings import TOKEN, VERSION
from database.db import init_db

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Бот запущен (версия {VERSION}) — {bot.user}")
    # Можно здесь добавить сообщение в канал, что бот жив

# --- Асинхронная функция для загрузки Cogs ---
async def main():
    init_db()  # инициализация базы
    async with bot:
        await bot.load_extension("cogs.tasks")
        await bot.load_extension("cogs.rating")
        await bot.start(TOKEN)

# Запуск
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
