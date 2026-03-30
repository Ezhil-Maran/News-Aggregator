# main.py
import re
import asyncio
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict
from dateutil import parser as dateparser

import httpx
import feedparser
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rouge_score import rouge_scorer

# ============================================================
# CONFIG
# ============================================================

DB_PATH = "news_cache.db"

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.theguardian.com/world/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "http://rss.cnn.com/rss/edition_world.rss"
    "https://www.thehindu.com/news/national/tamil-nadu"
]

FETCH_TIMEOUT = 20
MAX_ARTICLES_PER_FEED = 30
TITLE_OVERLAP_THRESHOLD = 3  # lightweight clustering

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ============================================================
# APP
# ============================================================

app = FastAPI(title="Unified News Backend - Stable Research Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# DATABASE
# ============================================================

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

    for a in articles:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO articles
                (title, link, domain, published, content, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                a["title"],
                a["link"],
                a["domain"],
                a["published"],
                a["content"],
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
        SELECT title, link, domain, published, content
        FROM articles
    """)
    rows = cur.fetchall()
    con.close()

    return [
        dict(
            title=r[0],
            link=r[1],
            domain=r[2],
            published=r[3],
            content=r[4] or ""
        )
        for r in rows
    ]

# ============================================================
# CLEANING
# ============================================================

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

# ============================================================
# FETCHING
# ============================================================

async def fetch_single_feed(client, feed_url):
    domain = feed_url.split("//")[1].split("/")[0]

    try:
        response = await client.get(feed_url)
        response.raise_for_status()

        parsed = feedparser.parse(response.text)
        articles = []

        for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:

            content = clean_text(
                entry.get("summary", "") or
                entry.get("description", "")
            )

            if len(content) < 40:
                content = clean_text(entry.get("title", ""))

            articles.append({
                "title": clean_text(entry.get("title", "")),
                "link": entry.get("link", "").split("?")[0],
                "domain": domain,
                "published": entry.get("published", ""),
                "content": content
            })

        logger.info(f"Fetched {len(articles)} from {domain}")
        return articles

    except Exception as e:
        logger.warning(f"Skipped feed {feed_url} → {e}")
        return []


async def fetch_all_feeds():
    async with httpx.AsyncClient(
        timeout=FETCH_TIMEOUT,
        headers={"User-Agent": "UnifiedNewsResearchBot/1.0"}
    ) as client:

        tasks = [fetch_single_feed(client, feed) for feed in RSS_FEEDS]
        results = await asyncio.gather(*tasks)

    articles = []
    for r in results:
        articles.extend(r)

    unique = {}
    for a in articles:
        unique[a["link"]] = a

    logger.info(f"Total unique articles: {len(unique)}")
    return list(unique.values())

# ============================================================
# LIGHTWEIGHT CLUSTERING (NO FREEZE)
# ============================================================

def cluster_articles(articles: List[Dict]):

    clusters = []
    used = set()

    for i, a in enumerate(articles):

        if i in used:
            continue

        cluster = [a]
        used.add(i)

        words_a = set(a["title"].split())

        for j, b in enumerate(articles):

            if j in used:
                continue

            words_b = set(b["title"].split())
            overlap = len(words_a & words_b)

            if overlap >= TITLE_OVERLAP_THRESHOLD and a["domain"] != b["domain"]:
                cluster.append(b)
                used.add(j)

        clusters.append(cluster)

    logger.info(f"Clusters formed: {len(clusters)}")
    return clusters

# ============================================================
# SUMMARIZATION (SAFE VERSION)
# ============================================================

def summarize_cluster(cluster: List[Dict]):

    all_sentences = []

    for article in cluster:
        sentences = re.split(r"[.!?]", article["content"])
        for s in sentences:
            s = s.strip()
            if len(s) > 60:
                all_sentences.append(s)

    if len(all_sentences) < 3:
        return None

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=1500
    )

    tfidf = vectorizer.fit_transform(all_sentences)
    scores = tfidf.sum(axis=1).A1
    ranked = np.argsort(scores)[::-1]

    selected = []

    for idx in ranked:
        selected.append(all_sentences[idx])
        if len(selected) >= 4:
            break

    return " ".join(selected)

# ============================================================
# STRUCTURED ARTICLE
# ============================================================

def build_structured_article(cluster: List[Dict]):

    domains = {a["domain"] for a in cluster}

    if len(domains) < 2:
        return None

    summary = summarize_cluster(cluster)

    if not summary:
        return None

    return {
        "title": cluster[0]["title"],
        "publisher_count": len(domains),
        "summary": summary,
        "sources": [a["link"] for a in cluster]
    }

# ============================================================
# ROUTES
# ============================================================

@app.on_event("startup")
async def startup():
    init_db()
    articles = await fetch_all_feeds()
    save_articles_bulk(articles)
    logger.info("Startup complete.")


@app.get("/news")
def get_news():

    articles = get_all_articles()[:80]  # safety cap
    clusters = cluster_articles(articles)

    multi, single = [], []

    for c in clusters:
        structured = build_structured_article(c)
        if structured:
            multi.append(structured)
        else:
            single.extend(c)
        

    return {
        "multi_source_articles": multi,
        "single_source_articles": single
    }