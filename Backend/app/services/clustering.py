from typing import Dict, List, Set
import re

from app.api.config.logging_config import logger


# Common words that do not provide much information
# when determining whether two news titles describe
# the same event.
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "by",
    "for",
    "from",
    "has",
    "have",
    "he",
    "her",
    "his",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
    "after",
    "before",
    "over",
    "under",
    "how",
    "why",
    "what",
    "who",
    "when",
    "where",
    "could",
    "would",
    "says",
    "said",
}


# Minimum Jaccard similarity required to group
# two articles together.
JACCARD_THRESHOLD = 0.25

# Minimum number of meaningful words that must overlap.
MIN_SHARED_WORDS = 2


def _normalize_title(title: str) -> Set[str]:
    """
    Convert a news title into a set of meaningful words.
    """

    title = title.lower()

    # Keep alphabetic/numeric words.
    words = re.findall(r"[a-z0-9]+", title)

    # Remove common words.
    words = {
        word
        for word in words
        if word not in STOPWORDS
    }

    return words


def _calculate_similarity(
    words_a: Set[str],
    words_b: Set[str],
) -> float:
    """
    Calculate Jaccard similarity between two title word sets.
    """

    if not words_a or not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b

    return len(intersection) / len(union)


def cluster_articles(articles: List[Dict]) -> List[List[Dict]]:
    """
    Group related news articles using title similarity.

    Articles from the same domain are not grouped together because
    they are already from the same source.
    """

    clusters = []
    used = set()

    for i, article in enumerate(articles):

        if i in used:
            continue

        cluster = [article]
        used.add(i)

        words_a = _normalize_title(
            article.get("title", "")
        )

        for j, other in enumerate(articles):

            if j in used:
                continue

            # Do not cluster articles from the same source.
            if article.get("domain") == other.get("domain"):
                continue

            words_b = _normalize_title(
                other.get("title", "")
            )

            shared_words = words_a & words_b

            if len(shared_words) < MIN_SHARED_WORDS:
                continue

            similarity = _calculate_similarity(
                words_a,
                words_b,
            )

            if similarity >= JACCARD_THRESHOLD:

                cluster.append(other)
                used.add(j)

                logger.debug(
                    "Articles clustered | "
                    f"similarity={similarity:.2f} | "
                    f"shared={sorted(shared_words)}"
                )

        clusters.append(cluster)

    logger.info(
        f"Clusters formed: {len(clusters)}"
    )

    return clusters