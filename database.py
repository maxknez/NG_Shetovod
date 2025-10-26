import sqlite3
import os

DATABASE_NAME = "tasks.db"

TASK_STATUSES = {
    "todo": "Надо сделать",
    "assigned": "Назначено",
    "done": "Выполнено"
}

def connect_db():
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,       -- Уникальный ключ задачи
                text TEXT NOT NULL,             -- Текст задачи
                author_id INTEGER NOT NULL,     -- ID автора задачи
                assigned_to_id INTEGER,         -- ID пользователя, которому назначена задача (может быть NULL)
                status TEXT NOT NULL DEFAULT 'todo', -- Статус задачи (todo, assigned, done)
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME           -- Время выполнения задачи
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                user_id INTEGER PRIMARY KEY,
                score INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()
    print("База данных инициализирована.")

def add_task(key: str, text: str, author_id: int) -> bool:
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO tasks (key, text, author_id) VALUES (?, ?, ?)", (key, text, author_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_task_by_key(key: str):
    """Возвращает задачу по ключу."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, key, text, author_id, assigned_to_id, status, created_at, completed_at FROM tasks WHERE key = ?", (key,))
        return cursor.fetchone()

def get_tasks_by_status(status: str):
    """Возвращает задачи по указанному статусу."""
    if status not in TASK_STATUSES:
        return []
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, text, author_id, assigned_to_id, status FROM tasks WHERE status = ? ORDER BY created_at ASC", (status,))
        return cursor.fetchall()

def get_active_tasks(): # <-- ВОТ ЭТА ФУНКЦИЯ ДОЛЖНА БЫТЬ
    """Возвращает задачи со статусом 'todo' или 'assigned'."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, text, author_id, assigned_to_id, status FROM tasks WHERE status IN ('todo', 'assigned') ORDER BY created_at ASC")
        return cursor.fetchall()

def assign_task(key: str, user_id: int) -> bool:
    """Назначает задачу пользователю, меняя статус на 'assigned'."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET assigned_to_id = ?, status = 'assigned' WHERE key = ? AND status = 'todo'", (user_id, key))
        conn.commit()
        return cursor.rowcount > 0

def complete_task(key: str, user_id: int) -> bool:
    """
    Завершает задачу, меняя статус на 'done' и устанавливая время выполнения.
    Возвращает True, если задача была назначена этому пользователю и успешно завершена.
    """
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = 'done', completed_at = CURRENT_TIMESTAMP WHERE key = ? AND assigned_to_id = ? AND status = 'assigned'", (key, user_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_task_by_key(key: str) -> bool:
    """Удаляет задачу по ключу. Возвращает True, если удалено, иначе False."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE key = ?", (key,))
        conn.commit()
        return cursor.rowcount > 0

def get_user_rating(user_id: int) -> int:
    """Возвращает рейтинг пользователя."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT score FROM ratings WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

def add_rating_point(user_id: int):
    """Добавляет одно очко рейтинга пользователю."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ratings (user_id, score) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET score = score + 1", (user_id,))
        conn.commit()

def get_top_ratings(limit: int = 10):
    """Возвращает список пользователей с наивысшим рейтингом."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, score FROM ratings ORDER BY score DESC LIMIT ?", (limit,))
        return cursor.fetchall()