import discord
from discord.ext import commands
import settings
import database  # Импортируем наш модуль для работы с БД

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    print("Инициализация базы данных...")
    database.init_db()  # Инициализируем базу данных при запуске бота
    print("База данных инициализирована.")

    print("Загрузка когов...")
    await bot.load_extension("cogs.utils")  # Ваш ког с командой ping
    await bot.load_extension("cogs.tasks")  # Новый ког с командами для тасков
    print("Коги загружены.")

    await bot.tree.sync()
    # Если вы хотите синхронизировать только с конкретной гильдией для тестирования:
    # await bot.tree.sync(guild=discord.Object(id=ID_ВАШЕЙ_ГИЛЬДИИ_ЗДЕСЬ))
    print("Слеш-команды синхронизированы.")
    print("Бот готов к работе!")


if __name__ == "__main__":
    if not settings.DISCORD_BOT_TOKEN:
        print("Ошибка: Токен бота не найден в файле .env")
        print("Пожалуйста, создайте файл .env и добавьте DISCORD_BOT_TOKEN=ВАШ_ТОКЕН")
    else:
        bot.run(settings.DISCORD_BOT_TOKEN)