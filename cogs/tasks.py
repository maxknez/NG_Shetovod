import discord
from discord.ext import commands
import asyncio
from database import db

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Команда /добавить "ключ" "описание"
    @commands.command(name="добавить")
    async def add_task(self, ctx, key: str, *, description: str):
        try:
            await asyncio.to_thread(db.add_task, key, description, ctx.author.id)
            await ctx.send(f"✅ Задача '{key}' добавлена!")
        except Exception as e:
            await ctx.send(f"❌ Ошибка при добавлении задачи: {e}")

        # Команда /взять "ключ" — назначает текущего пользователя
    @commands.command(name="взять")
    async def take_task(self, ctx, key: str):
        try:
            success = await asyncio.to_thread(db.take_task, key, ctx.author.id)
            if success:
                await ctx.send(f"✅ Вы взяли задачу '{key}'!")
            else:
                await ctx.send(f"❌ Задача '{key}' не найдена или уже занята.")
        except Exception as e:
            await ctx.send(f"❌ Ошибка: {e}")

        # Команда /снять "ключ" — снимает пользователя
    @commands.command(name="снять")
    async def unassign_task(self, ctx, key: str):
        try:
            success = await asyncio.to_thread(db.remove_task_user, key, ctx.author.id)
            if success:
                await ctx.send(f"✅ Вы сняли задачу '{key}'.")
            else:
                await ctx.send(f"❌ Задача '{key}' не найдена или не назначена на вас.")
        except Exception as e:
            await ctx.send(f"❌ Ошибка: {e}")

        # Команда /сделал "ключ" — отмечает выполненной
    @commands.command(name="сделал")
    async def complete_task(self, ctx, key: str):
        try:
            success = await asyncio.to_thread(db.complete_task, key, ctx.author.id)
            if success:
                await ctx.send(f"🎉 Задача '{key}' выполнена!")
            else:
                await ctx.send(f"❌ Задача '{key}' не найдена или не назначена на вас.")
        except Exception as e:
            await ctx.send(f"❌ Ошибка: {e}")

        # Команда /удалить "ключ"
    @commands.command(name="удалить")
    async def delete_task(self, ctx, key: str):
        try:
            success = await asyncio.to_thread(db.delete_task, key)
            if success:
                await ctx.send(f"✅ Задача '{key}' удалена.")
            else:
                await ctx.send(f"❌ Задача '{key}' не найдена.")
        except Exception as e:
            await ctx.send(f"❌ Ошибка: {e}")

        # Команда /задачи — выводит список задач
    @commands.command(name="задачи")
    async def list_tasks(self, ctx):
        try:
            tasks = await asyncio.to_thread(db.list_tasks)
            if not tasks:
                await ctx.send("📋 Задач нет.")
                return
            
            msg = "📋 **Список задач:**\n\n"
            for task_id, key, text, author_id, user_id, status in tasks:
                # Получаем пользователей по ID
                author = await self.bot.fetch_user(author_id) if author_id else None
                user = await self.bot.fetch_user(user_id) if user_id else None
                
                author_name = author.name if author else "Неизвестен"
                user_name = user.name if user else "—"
                
                # Эмодзи для статуса
                status_emoji = {"надо сделать": "⏳", "назначено": "👤", "выполнено": "✅"}
                emoji = status_emoji.get(status, "❓")
                
                msg += f"{emoji} **{key}** | {status}\n"
                msg += f"   Автор: {author_name} | Исполнитель: {user_name}\n"
                msg += f"   Описание: {text}\n\n"
            
            await ctx.send(msg)
        except Exception as e:
            await ctx.send(f"❌ Ошибка при получении задач: {e}")

async def setup(bot):
    await bot.add_cog(Tasks(bot))
