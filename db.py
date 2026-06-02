import sqlite3
from contextlib import contextmanager

DB_PATH = "bot.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(""" 
            CREATE TABLE IF NOT EXISTS user_conversations ( 
                vk_user_id INTEGER PRIMARY KEY, 
                conversation_id TEXT NOT NULL 
            ) 
        """)


def get_conversation_id(vk_user_id: int) -> str | None:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT conversation_id FROM user_conversations WHERE vk_user_id = ?",
            (vk_user_id,)
        )
        row = cur.fetchone()
        return row[0] if row else None


def save_conversation_id(vk_user_id: int, conversation_id: str) -> None:
    with get_conn() as conn:
        conn.execute(""" 
            INSERT INTO user_conversations (vk_user_id, conversation_id) 
            VALUES (?, ?) 
            ON CONFLICT(vk_user_id) DO UPDATE SET conversation_id = excluded.conversation_id 
        """, (vk_user_id, conversation_id))


def delete_conversation_id(vk_user_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM user_conversations WHERE vk_user_id = ?",
            (vk_user_id,)
        )