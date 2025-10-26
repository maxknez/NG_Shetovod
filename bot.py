import discord
from discord.ext import commands
import settings
import database
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Обязательно для получения display_name участников

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    print("Инициализация базы данных...")
    database.init_db()
    print("База данных инициализирована.")

    print("Загрузка когов...")
    await bot.load_extension("cogs.utils")
    await bot.load_extension("cogs.tasks")
    await bot.load_extension("cogs.rating")  # Загружаем новый ког
    print("Коги загружены.")

    await bot.tree.sync()
    print("Слеш-команды синхронизированы.")
    print("Бот готов к работе!")

    utils_cog = bot.get_cog("Utils")
    if utils_cog:
        await utils_cog.send_startup_greeting()
        await asyncio.sleep(1)
        await utils_cog.get_or_create_task_list_message()
    else:
        print("Ког 'Utils' не найден после загрузки.")


if __name__ == "__main__":
    if not settings.DISCORD_BOT_TOKEN:
        print(
            "Ошибка: Токен бота не найден в файле .env. Пожалуйста, создайте файл .env и добавьте DISCORD_BOT_TOKEN=ВАШ_ТОКЕН")
    else:
        bot.run(settings.DISCORD_BOT_TOKEN)