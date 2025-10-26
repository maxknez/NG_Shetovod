import sqlite3
import os

DATABASE_NAME = "tasks.db"

def connect_db():
    """Устанавливает соединение с базой данных."""
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    """Инициализирует базу данных, создавая таблицу tasks, если она не существует."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,       -- Уникальный ключ задачи
                text TEXT NOT NULL,             -- Текст задачи
                author_id INTEGER NOT NULL,     -- ID автора задачи
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    print("База данных инициализирована.")

def add_task(key: str, text: str, author_id: int) -> bool:
    """
    Добавляет новую задачу в базу данных.
    Возвращает True, если задача успешно добавлена (ключ уникален), иначе False.
    """
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO tasks (key, text, author_id) VALUES (?, ?, ?)", (key, text, author_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Ключ уже существует (UNIQUE constraint failed)
            return False

def get_all_tasks():
    """Возвращает все задачи из базы данных."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, text, author_id FROM tasks ORDER BY created_at ASC")
        return cursor.fetchall()

def delete_task_by_key(key: str) -> bool:
    """Удаляет задачу по ключу. Возвращает True, если удалено, иначе False."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE key = ?", (key,))
        conn.commit()
        return cursor.rowcount > 0 # rowcount покажет, сколько строк было затронуто