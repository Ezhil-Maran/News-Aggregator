from typing import Dict, List

from app.api.config.settings import TITLE_OVERLAP_THRESHOLD
from app.api.config.logging_config import logger


def cluster_articles(articles: List[Dict]):

    clusters = []
    used = set()

    for i, article in enumerate(articles):

        if i in used:
            continue

        cluster = [article]
        used.add(i)

        words_a = set(article["title"].split())

        for j, other in enumerate(articles):

            if j in used:
                continue

            words_b = set(other["title"].split())

            overlap = len(words_a & words_b)

            if (
                overlap >= TITLE_OVERLAP_THRESHOLD
                and article["domain"] != other["domain"]
            ):
                cluster.append(other)
                used.add(j)

        clusters.append(cluster)

    logger.info(f"Clusters formed: {len(clusters)}")

    return clusters