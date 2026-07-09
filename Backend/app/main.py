from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.config.logging_config import logger

from app.api.database.database import (
    init_db,
    save_articles_bulk,
    get_all_articles,
)

from app.services.news_fetcher import fetch_all_feeds
from app.services.clustering import cluster_articles
from app.services.article_generator import build_structured_article


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
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():

    init_db()

    articles = await fetch_all_feeds()

    save_articles_bulk(articles)

    logger.info("Startup complete.")


# ============================================================
# ROUTES
# ============================================================

@app.get("/news")
def get_news():

    articles = get_all_articles()[:80]

    clusters = cluster_articles(articles)

    multi = []
    single = []

    for cluster in clusters:

        structured = build_structured_article(cluster)

        if structured:
            multi.append(structured)

        else:
            single.extend(cluster)

    return {
        "multi_source_articles": multi,
        "single_source_articles": single,
    }