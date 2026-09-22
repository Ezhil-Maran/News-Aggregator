import sqlite3
import json

from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.api.config.settings import DB_PATH
from app.api.config.logging_config import logger


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # --------------------------------------------------------
    # RAW RSS ARTICLES
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PIPELINE RUNS
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generated_at TEXT,
            processing_time_seconds REAL,
            total_articles INTEGER,
            clusters INTEGER,
            generated_articles INTEGER,
            single_source_articles INTEGER,
            success INTEGER,
            error TEXT
        )
    """)

    # --------------------------------------------------------
    # GENERATED AI ARTICLES
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS generated_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            headline TEXT,
            content TEXT,
            sources TEXT,
            article_count INTEGER,

            FOREIGN KEY (run_id)
                REFERENCES pipeline_runs(id)
        )
    """)

    # --------------------------------------------------------
    # MIGRATE ARTICLES TABLE
    # --------------------------------------------------------

    cur.execute("""
        PRAGMA table_info(articles)
    """)

    columns = [
        row[1]
        for row in cur.fetchall()
    ]

    if "run_id" not in columns:

        cur.execute("""
            ALTER TABLE articles
            ADD COLUMN run_id INTEGER
        """)

        logger.info(
            "Database migration: added run_id to articles."
        )

    if "is_single_source" not in columns:

        cur.execute("""
            ALTER TABLE articles
            ADD COLUMN is_single_source INTEGER DEFAULT 0
        """)

        logger.info(
            "Database migration: added is_single_source to articles."
        )

    con.commit()
    con.close()

    logger.info("Database initialized.")


# ============================================================
# RAW ARTICLE STORAGE
# ============================================================

def save_articles_bulk(
    articles: List[Dict],
    run_id: int,
    single_source_links: set
):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    for article in articles:

        is_single_source = (
            article["link"] in single_source_links
        )

        try:

            cur.execute("""
                INSERT INTO articles
                (
                    run_id,
                    title,
                    link,
                    domain,
                    published,
                    content,
                    fetched_at,
                    is_single_source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(link) DO UPDATE SET
                    run_id = excluded.run_id,
                    title = excluded.title,
                    domain = excluded.domain,
                    published = excluded.published,
                    content = excluded.content,
                    fetched_at = excluded.fetched_at,
                    is_single_source = excluded.is_single_source
            """, (
                run_id,
                article["title"],
                article["link"],
                article["domain"],
                article["published"],
                article["content"],
                datetime.now(timezone.utc).isoformat(),
                int(is_single_source)
            ))

        except Exception as e:

            logger.warning(
                f"DB insert failed: {e}"
            )

    con.commit()
    con.close()

# ============================================================
# PIPELINE RUN
# ============================================================

def create_pipeline_run(
    generated_at: str,
    processing_time_seconds: float,
    total_articles: int,
    clusters: int,
    generated_articles: int,
    single_source_articles: int,
    success: bool,
    error: Optional[str] = None,
) -> int:

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        INSERT INTO pipeline_runs (
            generated_at,
            processing_time_seconds,
            total_articles,
            clusters,
            generated_articles,
            single_source_articles,
            success,
            error
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        generated_at,
        processing_time_seconds,
        total_articles,
        clusters,
        generated_articles,
        single_source_articles,
        1 if success else 0,
        error
    ))

    run_id = cur.lastrowid

    con.commit()
    con.close()

    return run_id


# ============================================================
# GENERATED ARTICLE STORAGE
# ============================================================

def save_generated_articles(
    run_id: int,
    articles: List[Dict]
):

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    for article in articles:

        try:

            cur.execute("""
                INSERT INTO generated_articles (
                    run_id,
                    headline,
                    content,
                    sources,
                    article_count
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                run_id,
                article["headline"],
                article["content"],
                json.dumps(article["sources"]),
                article["article_count"]
            ))

        except Exception as e:

            logger.warning(
                f"Generated article DB insert failed: {e}"
            )

    con.commit()
    con.close()


# ============================================================
# RETRIEVE ALL RAW ARTICLES
# ============================================================

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
        {
            "title": row[0],
            "link": row[1],
            "domain": row[2],
            "published": row[3],
            "content": row[4] or ""
        }
        for row in rows
    ]

def get_latest_pipeline_run() -> Optional[Dict]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("""
        SELECT *
        FROM pipeline_runs
        WHERE success = 1
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()

    con.close()

    if row is None:
        return None

    return dict(row)

def get_generated_articles_by_run(run_id: int) -> List[Dict]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("""
        SELECT
            headline,
            content,
            sources,
            article_count
        FROM generated_articles
        WHERE run_id = ?
        ORDER BY id ASC
    """, (run_id,))

    rows = cur.fetchall()

    con.close()

    articles = []

    for row in rows:
        article = dict(row)

        article["sources"] = json.loads(
            article["sources"]
        )

        articles.append(article)

    return articles

def get_articles_by_run(run_id: int) -> List[Dict]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("""
        SELECT
            title,
            link,
            domain,
            published,
            content
        FROM articles
        WHERE run_id = ?
        AND is_single_source = 1
        ORDER BY id ASC
    """, (run_id,))

    rows = cur.fetchall()

    con.close()

    return [dict(row) for row in rows]