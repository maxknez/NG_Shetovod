import discord
from discord.ext import commands
import sqlite3
import asyncio

DB_PATH = "tasks.db"

# Словарь статусов
STATUSES = ["надо сделать", "назначено", "выполнено"]

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Вспомогательные функции для работы с БД
    async def execute_db(self, query, params=(), fetch=False):
        def db_task():
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall() if fetch else None
            conn.commit()
            conn.close()
            return result
        return await asyncio.to_thread(db_task)

    # Команда /добавить "ключ" "описание"
    @commands.command(name="добавить")
    async def add_task(self, ctx, key: str, *, description: str):
        await self.execute_db(
            "INSERT INTO tasks (key, description, author, status) VALUES (?, ?, ?, ?)",
            (key, description, str(ctx.author), STATUSES[0])
        )
        await ctx.send(f"Задача '{key}' добавлена!")

    # Команда /взять "ключ" — назначает текущего пользователя
    @commands.command(name="взять")
    async def take_task(self, ctx, key: str):
        task = await self.execute_db(
            "SELECT status FROM tasks WHERE key = ?",
            (key,), fetch=True
        )
        if not task:
            await ctx.send(f"Задача '{key}' не найдена.")
            return
        status = task[0][0]
        if status != STATUSES[0]:
            await ctx.send(f"Задачу '{key}' уже кто-то взял.")
            return
        await self.execute_db(
            "UPDATE tasks SET user = ?, status = ? WHERE key = ?",
            (str(ctx.author), STATUSES[1], key)
        )
        await ctx.send(f"Вы взяли задачу '{key}'!")

    # Команда /снять "ключ" — снимает пользователя
    @commands.command(name="снять")
    async def unassign_task(self, ctx, key: str):
        task = await self.execute_db(
            "SELECT user FROM tasks WHERE key = ?",
            (key,), fetch=True
        )
        if not task:
            await ctx.send(f"Задача '{key}' не найдена.")
            return
        if task[0][0] != str(ctx.author):
            await ctx.send(f"Вы не можете снять эту задачу.")
            return
        await self.execute_db(
            "UPDATE tasks SET user = NULL, status = ? WHERE key = ?",
            (STATUSES[0], key)
        )
        await ctx.send(f"Вы сняли задачу '{key}'.")

    # Команда /сделал "ключ" — отмечает выполненной
    @commands.command(name="сделал")
    async def complete_task(self, ctx, key: str):
        task = await self.execute_db(
            "SELECT user FROM tasks WHERE key = ?",
            (key,), fetch=True
        )
        if not task:
            await ctx.send(f"Задача '{key}' не найдена.")
            return
        if task[0][0] != str(ctx.author):
            await ctx.send(f"Вы не можете завершить эту задачу.")
            return
        await self.execute_db(
            "UPDATE tasks SET status = ? WHERE key = ?",
            (STATUSES[2], key)
        )
        await ctx.send(f"Задача '{key}' выполнена!")

    # Команда /удалить "ключ"
    @commands.command(name="удалить")
    async def delete_task(self, ctx, key: str):
        await self.execute_db(
            "DELETE FROM tasks WHERE key = ?",
            (key,)
        )
        await ctx.send(f"Задача '{key}' удалена.")

    # Команда /задачи — выводит список задач
    @commands.command(name="задачи")
    async def list_tasks(self, ctx):
        tasks = await self.execute_db(
            "SELECT key, description, author, user, status FROM tasks",
            fetch=True
        )
        if not tasks:
            await ctx.send("Задач нет.")
            return
        msg = ""
        for key, desc, author, user, status in tasks:
            user_str = user if user else "—"
            msg += f"{key} | {status} | Автор: {author} | Исполнитель: {user_str}\nОписание: {desc}\n\n"
        await ctx.send(f"Список задач:\n{msg}")

async def setup(bot):
    await bot.add_cog(Tasks(bot))
