from typing import Dict, List

from app.services.summarizer import summarize_cluster


def build_structured_article(cluster: List[Dict]):

    domains = {article["domain"] for article in cluster}

    if len(domains) < 2:
        return None

    summary = summarize_cluster(cluster)

    if not summary:
        return None

    return {
        "title": cluster[0]["title"],
        "publisher_count": len(domains),
        "summary": summary,
        "sources": [
            article["link"]
            for article in cluster
        ],
    }