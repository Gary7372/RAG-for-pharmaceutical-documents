import sqlite3
from datetime import datetime

DB_NAME = "conversations.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            prompt TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_conversation(query: str, answer: str, prompt: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO conversations (query, prompt, answer, timestamp) VALUES (?, ?, ?, ?)
    """, (query, prompt, answer, timestamp))
    conn.commit()
    conn.close()
