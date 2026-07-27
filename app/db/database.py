import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parent / "resources" / "history.db"


def connect():
    return sqlite3.connect(DB)


def init_database():
    conn = connect()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT,

        platform TEXT,

        url TEXT,

        position TEXT,

        last_time TEXT

    )
    """)

    conn.commit()

    conn.close()


def add_video(
        title,
        platform,
        url,
        position
):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO videos
        (
        title,
        platform,
        url,
        position,
        last_time
        )
        VALUES(?,?,?,?,?)
        """,
        (
            title,
            platform,
            url,
            position,
            datetime.now().isoformat()
        ))
    conn.commit()
    conn.close()


def search_video(keyword):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
        title,
        platform,
        url,
        position
        FROM videos
        WHERE title LIKE ?
        ORDER BY last_time DESC
        LIMIT 1
        """,
        (
            f"%{keyword}%",
        ))

    result = cursor.fetchone()

    conn.close()

    return result
