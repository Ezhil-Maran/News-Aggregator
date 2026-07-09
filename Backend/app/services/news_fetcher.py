import asyncio

import feedparser
import httpx

from app.api.config.settings import (
    RSS_FEEDS,
    FETCH_TIMEOUT,
    MAX_ARTICLES_PER_FEED,
)

from app.api.config.logging_config import logger
from app.utils.preprocessing import clean_text


async def fetch_single_feed(client, feed_url):

    domain = feed_url.split("//")[1].split("/")[0]

    try:

        response = await client.get(feed_url)
        response.raise_for_status()

        parsed = feedparser.parse(response.text)

        articles = []

        for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:

            content = clean_text(
                entry.get("summary", "")
                or entry.get("description", "")
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

        logger.warning(f"Skipped feed {feed_url} -> {e}")

        return []


async def fetch_all_feeds():

    async with httpx.AsyncClient(
        timeout=FETCH_TIMEOUT,
        headers={
            "User-Agent": "UnifiedNewsResearchBot/1.0"
        }
    ) as client:

        tasks = [
            fetch_single_feed(client, feed)
            for feed in RSS_FEEDS
        ]

        results = await asyncio.gather(*tasks)

    articles = []

    for result in results:
        articles.extend(result)

    unique = {}

    for article in articles:
        unique[article["link"]] = article

    logger.info(f"Total unique articles: {len(unique)}")

    return list(unique.values())