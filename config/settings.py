import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота
TOKEN = os.getenv("DISCORD_TOKEN")

# Проверяем наличие токена
if not TOKEN:
    print("❌ ОШИБКА: Не найден DISCORD_TOKEN!")
    print("")
    print("Пожалуйста, создайте файл .env в корне проекта:")
    print("1. Скопируйте .env.example как .env")
    print("2. Замените 'your_bot_token_here' на ваш токен бота")
    print("")
    print("Токен можно получить на https://discord.com/developers/applications")
    sys.exit(1)

# Остальные настройки
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
DB_PATH = os.path.join("database", "tasks.db")
VERSION = "0.3"
