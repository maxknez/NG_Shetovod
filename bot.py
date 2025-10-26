import discord
from discord.ext import commands
import settings
import database
import asyncio  # Для задержки

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Необходим для получения информации об авторах тасков

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
    print("Коги загружены.")

    await bot.tree.sync()
    print("Слеш-команды синхронизированы.")
    print("Бот готов к работе!")

    # После загрузки когов и синхронизации, получаем доступ к когу Utils
    # и вызываем его методы
    utils_cog = bot.get_cog("Utils")
    if utils_cog:
        # Отправка приветствия
        await utils_cog.send_startup_greeting()
        # Инициализация сообщения со списком задач
        # Даем небольшую задержку, чтобы Discord успел обновить внутренние кэши после приветствия
        await asyncio.sleep(1)
        await utils_cog.get_or_create_task_list_message()
    else:
        print("Ког 'Utils' не найден после загрузки.")


if __name__ == "__main__":
    if not settings.DISCORD_BOT_TOKEN:
        print("Ошибка: Токен бота не найден в файле .env")
        print("Пожалуйста, создайте файл .env и добавьте DISCORD_BOT_TOKEN=ВАШ_ТОКЕН")
    else:
        bot.run(settings.DISCORD_BOT_TOKEN)