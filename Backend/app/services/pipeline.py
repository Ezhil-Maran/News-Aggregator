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
from app.api.database.database import (
    save_articles_bulk,
    create_pipeline_run,
    save_generated_articles,
)


# ============================================================
# PIPELINE
# ============================================================

async def run_pipeline() -> Dict:
    """
    Executes the complete AI news generation pipeline.
    """

    pipeline_start = time.perf_counter()
    generated_at = datetime.now(timezone.utc).isoformat()

    logger.info("=" * 70)
    logger.info("Starting AI News Generation Pipeline")
    logger.info("=" * 70)

    try:

        # ----------------------------------------------------
        # STEP 1 — Fetch RSS Articles
        # ----------------------------------------------------

        fetch_start = time.perf_counter()

        logger.info("[STEP 1] Fetching RSS feeds...")

        articles = await fetch_all_feeds()

        fetch_time = time.perf_counter() - fetch_start

        logger.info(
            f"[STEP 1] Fetched {len(articles)} unique articles "
            f"in {fetch_time:.2f}s"
        )

        # ----------------------------------------------------
        # STEP 2 — Cluster Articles
        # ----------------------------------------------------

        cluster_start = time.perf_counter()

        logger.info("[STEP 2] Clustering related articles...")

        clusters = cluster_articles(articles)

        cluster_time = time.perf_counter() - cluster_start

        logger.info(
            f"[STEP 2] Generated {len(clusters)} clusters "
            f"in {cluster_time:.2f}s"
        )

        # ----------------------------------------------------
        # STEP 3 — Generate AI Articles
        # ----------------------------------------------------

        generated_articles = []
        single_source_articles = []

        logger.info("[STEP 3] Generating AI articles...")

        ai_start = time.perf_counter()

        for index, cluster in enumerate(clusters, start=1):

            logger.info(
                f"[STEP 3] Processing cluster "
                f"{index}/{len(clusters)} "
                f"({len(cluster)} source article(s))"
            )

            if len(cluster) > 1:

                generation_start = time.perf_counter()

                logger.info(
                    f"[STEP 3] Calling Qwen for cluster {index}..."
                )

                article = generate_article(cluster)

                generation_time = (
                    time.perf_counter() - generation_start
                )

                logger.info(
                    f"[STEP 3] Cluster {index} generated in "
                    f"{generation_time:.2f}s"
                )

                generated_articles.append(article)

            else:

                single_source_articles.extend(cluster)

                logger.info(
                    f"[STEP 3] Cluster {index} is a "
                    f"single-source article. Skipping Qwen."
                )

        ai_time = time.perf_counter() - ai_start

        # ----------------------------------------------------
        # TOTAL TIME
        # ----------------------------------------------------

        single_source_links = {
            article["link"]
            for article in single_source_articles
        }
        
        processing_time = round(
            time.perf_counter() - pipeline_start,
            2,
        )

        logger.info(
            f"[STEP 3] AI generation completed in "
            f"{ai_time:.2f}s"
        )

        logger.info(
            f"[TOTAL] Pipeline completed in "
            f"{processing_time}s"
        )

        run_id = create_pipeline_run(
            generated_at=generated_at,
            processing_time_seconds=processing_time,
            total_articles=len(articles),
            clusters=len(clusters),
            generated_articles=len(generated_articles),
            single_source_articles=len(single_source_articles),
            success=True,
        )

        save_articles_bulk(
            articles,
            run_id,
            single_source_links
        )

        save_generated_articles(    
            run_id,
            generated_articles
        )

        logger.info("=" * 70)

        return {

            "success": True,

            "generated_at": generated_at,

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

        processing_time = round(
            time.perf_counter() - pipeline_start,
            2,
        )

        logger.exception(
            "Pipeline execution failed."
        )

        return {

            "success": False,

            "generated_at": generated_at,

            "processing_time_seconds": processing_time,

            "error": str(e),

            "generated_articles": [],

            "single_source_articles": [],

            "statistics": {},

        }