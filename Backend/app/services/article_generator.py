"""
article_generator.py

Generates a professional news article from a cluster of
related news reports.
"""

from typing import Dict, List

from app.prompts.prompt_builder import build_news_prompt
from app.services.inference import generate_text
from app.services.response_parser import parse_response


# ============================================================
# HELPERS
# ============================================================

def _collect_sources(cluster: List[Dict]) -> List[str]:
    """
    Returns a unique list of source domains.
    """

    sources = []

    for article in cluster:

        domain = article.get("domain")

        if domain and domain not in sources:
            sources.append(domain)

    return sources


# ============================================================
# PUBLIC API
# ============================================================

def generate_article(cluster: List[Dict]) -> Dict:
    """
    Generates one news article from a cluster.
    """

    if not cluster:

        return {
            "headline": "",
            "content": "",
            "sources": [],
            "article_count": 0,
        }

    prompt = build_news_prompt(cluster)

    print("\n========== STEP 4 ==========")
    print("Calling generate_text()...")
    print("============================\n")

    response = generate_text(prompt)

    parsed = parse_response(response)

    headline = parsed["headline"].strip()

    if not headline:
        headline = cluster[0].get("title", "Untitled Article")

    return {
        "headline": headline,
        "content": parsed["content"].strip(),
        "sources": _collect_sources(cluster),
        "article_count": len(cluster),
    }