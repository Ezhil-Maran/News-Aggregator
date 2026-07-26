"""
pipeline.py

Coordinates the complete AI news generation pipeline.

Pipeline

Fetch Articles
        ↓
Cluster Articles
        ↓
Generate AI Articles
        ↓
Return Structured Response
"""

from typing import Dict

from app.services.news_fetcher import fetch_all_feeds
from app.services.clustering import cluster_articles
from app.services.article_generator import generate_article

from app.api.config.logging_config import logger


# ============================================================
# PIPELINE
# ============================================================

async def run_pipeline() -> Dict:
    """
    Executes the complete news generation pipeline.
    """

    logger.info("=" * 60)
    logger.info("Starting news generation pipeline...")
    logger.info("=" * 60)

    # --------------------------------------------------------
    # Fetch latest news
    # --------------------------------------------------------

    logger.info("STEP 1: Fetching latest RSS articles...")

    articles = await fetch_all_feeds()

    logger.info(f"STEP 1 COMPLETE: {len(articles)} articles fetched.")

    # --------------------------------------------------------
    # Cluster related articles
    # --------------------------------------------------------

    logger.info("STEP 2: Clustering articles...")

    clusters = cluster_articles(articles)

    logger.info(f"STEP 2 COMPLETE: {len(clusters)} clusters created.")

    # --------------------------------------------------------
    # Generate AI articles
    # --------------------------------------------------------

    logger.info("STEP 3: Generating AI articles...")

    generated_articles = []

    single_source_articles = []

    for index, cluster in enumerate(clusters, start=1):

        logger.info(
            f"STEP 3.{index}: Processing cluster containing {len(cluster)} article(s)."
        )

        if len(cluster) > 1:

            generated_articles.append(
                generate_article(cluster)
            )

            logger.info(
                f"STEP 3.{index}: AI article generated successfully."
            )

        else:

            single_source_articles.extend(cluster)

            logger.info(
                f"STEP 3.{index}: Single-source article skipped."
            )

    logger.info(
        f"Generated {len(generated_articles)} AI article(s)."
    )

    logger.info("=" * 60)
    logger.info("Pipeline completed successfully.")
    logger.info("=" * 60)

    return {
        "generated_articles": generated_articles,
        "single_source_articles": single_source_articles,
        "statistics": {
            "total_articles": len(articles),
            "clusters": len(clusters),
            "generated_articles": len(generated_articles),
            "single_source_articles": len(single_source_articles),
        },
    }