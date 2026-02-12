# main.py
import re
import asyncio
import sqlite3
from typing import List, Dict

import httpx
import feedparser
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
DB_PATH = "news_cache.db"

# 🌍 STABLE GLOBAL NEWS SOURCES
RSS_FEEDS = [
    "https://feeds.reuters.com/reuters/topNews",
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.theguardian.com/world/rss",
]

SIMILARITY_THRESHOLD = 0.42

# -------------------------------------------------
# APP
# -------------------------------------------------
app = FastAPI(title="Unified News Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# DB
# -------------------------------------------------
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
            content TEXT
        )
    """)
    con.commit()
    con.close()

def save_articles(articles: List[Dict]):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    for a in articles:
        cur.execute("""
            INSERT OR IGNORE INTO articles
            (title, link, domain, published, content)
            VALUES (?, ?, ?, ?, ?)
        """, (
            a["title"],
            a["link"],
            a["domain"],
            a["published"],
            a["content"]
        ))
    con.commit()
    con.close()

def get_all_articles():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT title, link, domain, published, content FROM articles")
    rows = cur.fetchall()
    con.close()
    return [
        dict(title=r[0], link=r[1], domain=r[2], published=r[3], content=r[4])
        for r in rows
    ]

# -------------------------------------------------
# CLEANING
# -------------------------------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"\b(By|Reporter|Editor).*?\.", "", text, flags=re.I)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -------------------------------------------------
# FETCHING (FAULT TOLERANT)
# -------------------------------------------------
async def fetch_rss():
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        for feed in RSS_FEEDS:
            try:
                r = await client.get(feed)
                parsed = feedparser.parse(r.text)
                domain = feed.split("//")[1].split("/")[0]

                for e in parsed.entries[:12]:
                    results.append({
                        "title": e.get("title", ""),
                        "link": e.get("link", ""),
                        "domain": domain,
                        "published": e.get("published", ""),
                        "content": clean_text(
                            e.get("summary", "") or e.get("description", "")
                        )
                    })

                print(f"Fetched from {domain}")

            except Exception as e:
                print(f"⚠️ Skipped feed {feed} → {e}")

    return results

# -------------------------------------------------
# CLUSTERING
# -------------------------------------------------
def cluster_articles(articles: List[Dict]):
    titles = [a["title"] for a in articles]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(titles)
    similarity = cosine_similarity(tfidf)

    clusters = []
    used = set()

    for i, article in enumerate(articles):
        if i in used:
            continue

        cluster = [article]
        used.add(i)

        for j in range(i + 1, len(articles)):
            if j in used:
                continue
            if similarity[i][j] >= SIMILARITY_THRESHOLD:
                if articles[j]["domain"] != article["domain"]:
                    cluster.append(articles[j])
                    used.add(j)

        clusters.append(cluster)

    return clusters

# -------------------------------------------------
# STRUCTURED ARTICLE
# -------------------------------------------------
def build_structured_article(cluster: List[Dict]):
    publishers = {a["domain"] for a in cluster}
    if len(publishers) < 2:
        return None

    sentences = []
    for a in cluster:
        sentences.extend(a["content"].split(". "))

    unique = list(dict.fromkeys(sentences))

    return {
        "title": cluster[0]["title"],
        "publisher_count": len(publishers),
        "summary": (
            "Summary:\n"
            + ". ".join(unique[:2])
            + "\n\nWhat happened:\n- "
            + "\n- ".join(unique[2:4])
            + "\n\nWhy it matters:\n- "
            + "\n- ".join(unique[4:6])
        ),
        "sources": [a["link"] for a in cluster]
    }

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.on_event("startup")
async def startup():
    init_db()
    articles = await fetch_rss()
    save_articles(articles)
    print(f"Startup complete. Articles stored: {len(articles)}")

@app.get("/news")
def news():
    articles = get_all_articles()
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
