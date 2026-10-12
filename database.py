"""
Database module for DMI(F-N) infobot.
Uses SQLite to store:
- Subscribed users and their preferences
- Seen notices to avoid duplicate alerts
"""

import sqlite3
import datetime
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = "dmi_bot.db"


@contextmanager
def get_connection(db_path: str = DEFAULT_DB_PATH):
    """Context manager for SQLite connection that guarantees connection is closed."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()



def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initializes tables in the SQLite database if they don't exist."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_active INTEGER DEFAULT 1,
                include_cds INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Seen notices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seen_notices (
                notice_id TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                date TEXT,
                link TEXT,
                reason TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


def register_user(
    chat_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH
) -> bool:
    """
    Registers a new user or reactivates an existing user.
    Returns True if user was newly created, False if reactivated/updated.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, is_active FROM users WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()

        now = datetime.datetime.now().isoformat()

        if row is None:
            cursor.execute("""
                INSERT INTO users (chat_id, username, first_name, is_active, include_cds, created_at, updated_at)
                VALUES (?, ?, ?, 1, 0, ?, ?)
            """, (chat_id, username, first_name, now, now))
            conn.commit()
            return True
        else:
            cursor.execute("""
                UPDATE users
                SET username = ?, first_name = ?, is_active = 1, updated_at = ?
                WHERE chat_id = ?
            """, (username, first_name, now, chat_id))
            conn.commit()
            return False


def set_user_active(chat_id: int, is_active: bool, db_path: str = DEFAULT_DB_PATH) -> None:
    """Sets user active status (for /stop or resume)."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        now = datetime.datetime.now().isoformat()
        cursor.execute("""
            UPDATE users SET is_active = ?, updated_at = ? WHERE chat_id = ?
        """, (1 if is_active else 0, now, chat_id))
        conn.commit()


def toggle_user_cds(chat_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Toggles user setting for receiving general CdS notices. Returns new boolean state."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT include_cds FROM users WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        new_val = 1
        if row and row["include_cds"]:
            new_val = 0

        now = datetime.datetime.now().isoformat()
        cursor.execute("""
            UPDATE users SET include_cds = ?, updated_at = ? WHERE chat_id = ?
        """, (new_val, now, chat_id))
        conn.commit()
        return bool(new_val)


def get_user(chat_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Gets user record by chat_id."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_active_users(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Returns all currently active subscribed users."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE is_active = 1")
        return [dict(r) for r in cursor.fetchall()]


def is_notice_seen(notice_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Checks whether a notice ID has already been recorded."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM seen_notices WHERE notice_id = ?", (notice_id,))
        return cursor.fetchone() is not None


def mark_notice_seen(notice: Dict[str, Any], db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Marks a notice as seen. Returns True if inserted, False if already existed.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO seen_notices (notice_id, title, author, date, link, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                notice.get("id", ""),
                notice.get("title", ""),
                notice.get("author", ""),
                notice.get("date", ""),
                notice.get("link", ""),
                notice.get("reason", "")
            ))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False


def seed_initial_notices(notices: List[Dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Seeds initial notices so the bot does not spam past notices upon cold startup.
    Returns count of newly seeded notices.
    """
    count = 0
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for n in notices:
            cursor.execute("SELECT 1 FROM seen_notices WHERE notice_id = ?", (n.get("id"),))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT OR IGNORE INTO seen_notices (notice_id, title, author, date, link, reason)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    n.get("id", ""),
                    n.get("title", ""),
                    n.get("author", ""),
                    n.get("date", ""),
                    n.get("link", ""),
                    n.get("reason", "")
                ))
                count += 1
        conn.commit()
    return count
