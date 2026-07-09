import sqlite3
from datetime import datetime
from typing import Dict, List

from app.api.config.settings import DB_PATH
from app.api.config.logging_config import logger


def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            domain TEXT,
            published TEXT,
            content TEXT,
            fetched_at TEXT
        )
    """)

    con.commit()
    con.close()


def save_articles_bulk(articles: List[Dict]):

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    for article in articles:

        try:

            cur.execute("""
                INSERT OR IGNORE INTO articles
                (title, link, domain, published, content, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                article["title"],
                article["link"],
                article["domain"],
                article["published"],
                article["content"],
                datetime.utcnow().isoformat()
            ))

        except Exception as e:

            logger.warning(f"DB insert failed: {e}")

    con.commit()
    con.close()


def get_all_articles():

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        SELECT
            title,
            link,
            domain,
            published,
            content
        FROM articles
    """)

    rows = cur.fetchall()

    con.close()

    return [
        dict(
            title=row[0],
            link=row[1],
            domain=row[2],
            published=row[3],
            content=row[4] or ""
        )
        for row in rows
    ]