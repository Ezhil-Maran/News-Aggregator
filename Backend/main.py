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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ============================================================
# CONFIG
# ============================================================

DB_PATH = "news_cache.db"

RSS_FEEDS = [
    "http://rss.cnn.com/rss/edition_politics.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "http://feeds.foxnews.com/foxnews/politics",
    "https://apnews.com/hub/politics?outputType=xml"
]

SIMILARITY_THRESHOLD = 0.32
FETCH_TIMEOUT = 15
MAX_ARTICLES_PER_FEED = 15
CLUSTER_TIME_WINDOW_HOURS = 48

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

app = FastAPI(title="Unified News Backend - Research Grade")

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
            content=r[4]
        )
        for r in rows
    ]

# ============================================================
# CLEANING
# ============================================================

BOILERPLATE_PATTERNS = [
    r"live blog",
    r"follow us",
    r"subscribe",
    r"newsletter",
    r"advertisement",
    r"©",
    r"all rights reserved",
    r"read more",
    r"traffic_source",
    r"utm_source",
]

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text)

    for pattern in BOILERPLATE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text.strip()

# ============================================================
# FETCHING
# ============================================================

async def fetch_single_feed(client, feed_url):
    domain = feed_url.split("//")[1].split("/")[0]

    try:
        response = await client.get(feed_url)
        if response.status_code != 200:
            return []

        parsed = feedparser.parse(response.text)
        articles = []

        for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:
            articles.append({
                "title": clean_text(entry.get("title", "")),
                "link": entry.get("link", "").split("?")[0],
                "domain": domain,
                "published": entry.get("published", ""),
                "content": clean_text(
                    entry.get("summary", "") or entry.get("description", "")
                )
            })

        return articles

    except Exception:
        return []


async def fetch_all_feeds():
    async with httpx.AsyncClient(timeout=FETCH_TIMEOUT) as client:
        tasks = [fetch_single_feed(client, feed) for feed in RSS_FEEDS]
        results = await asyncio.gather(*tasks)

    articles = []
    for r in results:
        articles.extend(r)

    unique_links = set()
    deduped = []

    for a in articles:
        if a["link"] not in unique_links:
            unique_links.add(a["link"])
            deduped.append(a)

    return deduped

# ============================================================
# CLUSTERING
# ============================================================

def within_time_window(a_date, b_date):
    try:
        a = dateparser.parse(a_date)
        b = dateparser.parse(b_date)
        delta = abs((a - b).total_seconds()) / 3600
        return delta <= CLUSTER_TIME_WINDOW_HOURS
    except Exception:
        return True


def cluster_articles(articles: List[Dict]):
    if len(articles) < 2:
        return [[a] for a in articles]

    texts = [
        a["title"] + " " + (a["content"] or "")
        for a in articles
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    tfidf = vectorizer.fit_transform(texts)
    similarity = cosine_similarity(tfidf)

    clusters = []
    used = set()

    for i in range(len(articles)):
        if i in used:
            continue

        cluster = [articles[i]]
        used.add(i)

        for j in range(i + 1, len(articles)):
            if j in used:
                continue

            if not within_time_window(
                articles[i]["published"],
                articles[j]["published"]
            ):
                continue

            if similarity[i][j] >= SIMILARITY_THRESHOLD:
                if articles[i]["domain"] != articles[j]["domain"]:
                    cluster.append(articles[j])
                    used.add(j)

        clusters.append(cluster)

    return clusters

# ============================================================
# RESEARCH-GRADE SUMMARIZATION
# ============================================================

def summarize_cluster(cluster: List[Dict]):
    all_sentences = []
    sentence_source_count = {}

    for article in cluster:
        sentences = article["content"].split(". ")
        for s in sentences:
            s = s.strip()
            if len(s) < 50:
                continue

            all_sentences.append(s)
            sentence_source_count[s] = sentence_source_count.get(s, 0) + 1

    if len(all_sentences) < 3:
        return None

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(all_sentences)

    scores = tfidf.sum(axis=1).A1

    # Boost sentences appearing in multiple sources
    boosted_scores = []
    for i, sentence in enumerate(all_sentences):
        boost = sentence_source_count[sentence] * 0.5
        boosted_scores.append(scores[i] + boost)

    ranked_indices = np.argsort(boosted_scores)[::-1]

    selected = []
    selected_vectors = []

    for idx in ranked_indices:
        candidate = all_sentences[idx]

        # Redundancy reduction
        if selected_vectors:
            candidate_vec = tfidf[idx]
            sims = cosine_similarity(candidate_vec, selected_vectors)
            if np.max(sims) > 0.75:
                continue

        selected.append(candidate)
        selected_vectors.append(tfidf[idx])

        if len(selected) >= 6:
            break

    overview = selected[:2]
    developments = selected[2:4]
    implications = selected[4:6]

    summary = ""

    if overview:
        summary += "**Overview**\n" + " ".join(overview) + ".\n\n"

    if developments:
        summary += "**Key Developments**\n"
        summary += "\n".join(f"• {s}." for s in developments) + "\n\n"

    if implications:
        summary += "**Implications**\n"
        summary += "\n".join(f"• {s}." for s in implications)

    return summary.strip()


def build_structured_article(cluster: List[Dict]):
    publishers = {a["domain"] for a in cluster}
    if len(publishers) < 2:
        return None

    summary = summarize_cluster(cluster)
    if not summary:
        return None

    return {
        "title": cluster[0]["title"],
        "publisher_count": len(publishers),
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


@app.get("/news")
def get_news():
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

# ============================================================
# EVALUATION MODULE
# ============================================================

from rouge_score import rouge_scorer


def lead3_baseline(cluster: List[Dict]):
    first_article = cluster[0]
    sentences = first_article["content"].split(". ")
    sentences = [s.strip() for s in sentences if len(s) > 50]
    return " ".join(sentences[:3])


def evaluate_cluster(cluster: List[Dict]):
    system_summary = summarize_cluster(cluster)
    if not system_summary:
        return None

    baseline_summary = lead3_baseline(cluster)

    scorer = rouge_scorer.RougeScorer(
        ['rouge1', 'rouge2', 'rougeL'],
        use_stemmer=True
    )

    scores = scorer.score(baseline_summary, system_summary)

    return {
        "rouge1": scores["rouge1"].fmeasure,
        "rouge2": scores["rouge2"].fmeasure,
        "rougeL": scores["rougeL"].fmeasure
    }


@app.get("/evaluate")
def evaluate():
    articles = get_all_articles()
    clusters = cluster_articles(articles)

    for cluster in clusters:
        if len({a["domain"] for a in cluster}) >= 2:
            result = evaluate_cluster(cluster)
            if result:
                return result

    return {"message": "No suitable multi-source cluster found."}
