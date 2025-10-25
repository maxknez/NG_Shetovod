import sqlite3
import os
from config.settings import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Создаёт таблицы, если они ещё не существуют."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        author_id INTEGER,
        assigned_to INTEGER,
        status TEXT DEFAULT 'в процессе'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_ratings (
        user_id INTEGER PRIMARY KEY,
        rating INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
