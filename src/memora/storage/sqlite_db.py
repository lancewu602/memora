import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import SQLITE_PATH


def get_conn():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            tags TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            key_hash TEXT PRIMARY KEY,
            api_key TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_memory(id: str, content: str, tags: Optional[str] = None) -> bool:
    try:
        conn = get_conn()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO memories (id, content, created_at, updated_at, tags) VALUES (?, ?, ?, ?, ?)",
            (id, content, now, now, tags),
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_memory(id: str) -> Optional[dict]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memories WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def update_memory(id: str, content: str, tags: Optional[str] = None) -> bool:
    try:
        conn = get_conn()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE memories SET content = ?, updated_at = ?, tags = ? WHERE id = ?",
            (content, now, tags, id),
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    except Exception:
        return False


def delete_memory(id: str) -> bool:
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories WHERE id = ?", (id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    except Exception:
        return False


def list_memories(limit: int = 100) -> list[dict]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memories ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_api_key(api_key: str) -> bool:
    import hashlib

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    try:
        conn = get_conn()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT OR REPLACE INTO api_keys (key_hash, api_key, created_at) VALUES (?, ?, ?)",
            (key_hash, api_key, now),
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def verify_api_key(api_key: str) -> bool:
    import hashlib

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM api_keys WHERE key_hash = ?", (key_hash,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
