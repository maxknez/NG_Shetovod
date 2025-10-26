import sqlite3
from config.settings import DB_PATH
import os

def get_connection():
    """Создаёт подключение к БД, создавая папку database если её нет"""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Создаёт таблицу tasks, если её нет"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        text TEXT NOT NULL,
        author_id INTEGER NOT NULL,
        user_id INTEGER,
        status TEXT DEFAULT 'надо сделать'
    )
    """)

    conn.commit()
    conn.close()
    print("База данных и таблица tasks готовы.")

# --- Функции для управления задачами ---
def add_task(key: str, text: str, author_id: int):
    """Добавить новую задачу"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tasks (key, text, author_id) VALUES (?, ?, ?)",
            (key, text, author_id)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Задача с ключом '{key}' уже существует")
    finally:
        conn.close()

def take_task(key: str, user_id: int):
    """Назначить задачу пользователю"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET user_id = ?, status = 'назначено' WHERE key = ? AND user_id IS NULL", (user_id, key))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def remove_task_user(key: str, user_id: int):
    """Снять задачу с пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET user_id = NULL, status = 'надо сделать' WHERE key = ? AND user_id = ?", (key, user_id))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def complete_task(key: str, user_id: int):
    """Отметить задачу как выполненную"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'выполнено' WHERE key = ? AND user_id = ?", (key, user_id))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def delete_task(key: str):
    """Удалить задачу"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE key = ?", (key,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

def get_task(key: str):
    """Получить задачу по ключу"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, key, text, author_id, user_id, status FROM tasks WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row

def list_tasks():
    """Вернуть все задачи"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, key, text, author_id, user_id, status FROM tasks ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- Тестовая проверка ---
if __name__ == "__main__":
    init_db()
    add_task("тест", "Тестовая задача", 123456789)
    take_task("тест", 111)
    complete_task("тест", 111)
    tasks = list_tasks()
    for t in tasks:
        print(t)
