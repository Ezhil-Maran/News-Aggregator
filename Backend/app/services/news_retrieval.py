"""
news_retrieval.py

Builds the API response from the latest stored pipeline run.
"""

from typing import Dict

from app.api.database.database import (
    get_latest_pipeline_run,
    get_generated_articles_by_run,
    get_articles_by_run,
)


def get_latest_news() -> Dict:
    """
    Retrieves the latest successful pipeline run
    and builds the news API response from the database.
    """

    run = get_latest_pipeline_run()

    # No successful pipeline run exists
    if run is None:
        return {
            "success": False,
            "generated_at": None,
            "processing_time_seconds": 0.0,
            "error": "No completed news pipeline run found.",
            "statistics": {},
            "generated_articles": [],
            "single_source_articles": [],
        }

    run_id = run["id"]

    generated_articles = get_generated_articles_by_run(run_id)
    raw_articles = get_articles_by_run(run_id)

    return {
        "success": True,
        "generated_at": run["generated_at"],
        "processing_time_seconds": run["processing_time_seconds"],
        "statistics": {
            "total_articles": run["total_articles"],
            "clusters": run["clusters"],
            "generated_articles": run["generated_articles"],
            "single_source_articles": run["single_source_articles"],
        },
        "generated_articles": generated_articles,
        "single_source_articles": raw_articles,
    }