import discord
from discord.ext import commands

# Разрешаем доступ к содержимому сообщений
intents = discord.Intents.default()
intents.message_content = True

# Создаём экземпляр бота с префиксом "!"
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} успешно запущен!")

@bot.command()
async def привет(ctx):
    await ctx.send(f"Привет, {ctx.author.display_name}! 👋")

@bot.command()
async def пинг(ctx):
    await ctx.send(f"Понг! 🏓 {round(bot.latency * 1000)} мс")

# Запуск бота (вставь сюда токен из Discord Developer Portal)
bot.run("MTQzMTU5MDM0MjUxMTI5NjYzNQ.G35sT3.mhGO1mmsUbEJ7T00olRwz4jzgMxA8mP0kq9T88")
