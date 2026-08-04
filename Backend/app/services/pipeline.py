"""
pipeline.py

Coordinates the complete AI news generation pipeline.
"""

from datetime import datetime, timezone
import time
from typing import Dict

from app.api.config.logging_config import logger

from app.services.news_fetcher import fetch_all_feeds
from app.services.clustering import cluster_articles
from app.services.article_generator import generate_article


# ============================================================
# PIPELINE
# ============================================================

async def run_pipeline() -> Dict:
    """
    Executes the complete AI news generation pipeline.
    """

    start_time = time.perf_counter()

    logger.info("=" * 70)
    logger.info("Starting AI News Generation Pipeline")
    logger.info("=" * 70)

    try:

        # ----------------------------------------------------
        # Fetch RSS Articles
        # ----------------------------------------------------

        logger.info("Fetching RSS feeds...")

        articles = await fetch_all_feeds()

        logger.info(
            f"Fetched {len(articles)} unique articles."
        )

        # ----------------------------------------------------
        # Cluster Articles
        # ----------------------------------------------------

        logger.info("Clustering related articles...")

        clusters = cluster_articles(articles)

        logger.info(
            f"Generated {len(clusters)} clusters."
        )

        # ----------------------------------------------------
        # Generate AI Articles
        # ----------------------------------------------------

        generated_articles = []

        single_source_articles = []

        logger.info("Generating AI articles...")

        for cluster in clusters:

            if len(cluster) > 1:

                generated_articles.append(
                    generate_article(cluster)
                )

            else:

                single_source_articles.extend(cluster)

        processing_time = round(
            time.perf_counter() - start_time,
            2,
        )

        logger.info(
            f"Generated {len(generated_articles)} AI article(s)."
        )

        logger.info(
            f"Pipeline completed in {processing_time} seconds."
        )

        logger.info("=" * 70)

        return {

            "success": True,

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "processing_time_seconds": processing_time,

            "statistics": {

                "total_articles": len(articles),

                "clusters": len(clusters),

                "generated_articles": len(generated_articles),

                "single_source_articles": len(single_source_articles),

            },

            "generated_articles": generated_articles,

            "single_source_articles": single_source_articles,

        }

    except Exception as e:

        logger.exception(
            "Pipeline execution failed."
        )

        return {

            "success": False,

            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "error": str(e),

            "generated_articles": [],

            "single_source_articles": [],

            "statistics": {},

        }