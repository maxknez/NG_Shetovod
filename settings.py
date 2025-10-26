import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0)) # 0 как дефолтное значение, если ID не указан
# Можно добавить другие настройки, например, ID гильдии для тестирования слеш-команд
# GUILD_ID = int(os.getenv("GUILD_ID"))