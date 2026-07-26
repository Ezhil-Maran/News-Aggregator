"""
prompt_builder.py

Builds the user prompt from a cluster of related news articles.

This module ONLY formats the news reports.
The AI behaviour is defined in system_prompt.py.
"""

from typing import Dict, List


# ============================================================
# HEADER
# ============================================================

def _build_header() -> str:
    """
    Builds the introduction shown before the articles.
    """

    return (
        "The following news reports describe the same event.\n\n"
        "Each report may contain overlapping or unique information.\n"
        "Carefully read every report before writing the final article.\n\n"
    )


# ============================================================
# SINGLE ARTICLE
# ============================================================

def _build_article(article: Dict, index: int) -> str:
    """
    Formats a single article.
    """

    title = article.get("title", "Unknown Title")

    source = article.get("domain", "Unknown Source")

    published = article.get("published", "Unknown Date")

    content = (
        article.get("content")
        or article.get("summary")
        or article.get("description")
        or "No content available."
    )

    return (
        f"{'=' * 70}\n"
        f"REPORT {index}\n"
        f"{'=' * 70}\n\n"
        f"Title:\n"
        f"{title}\n\n"
        f"Source:\n"
        f"{source}\n\n"
        f"Published:\n"
        f"{published}\n\n"
        f"Report:\n"
        f"{content}\n\n"
    )


# ============================================================
# FOOTER
# ============================================================

def _build_footer() -> str:
    """
    Final reminder for the model.
    """

    return (
        "=" * 70
        + "\n"
        "END OF REPORTS\n"
        + "=" * 70
        + "\n\n"
        "Generate ONE professional news article using ONLY the information contained in the reports above."
    )


# ============================================================
# PUBLIC API
# ============================================================

def build_news_prompt(cluster: List[Dict]) -> str:
    """
    Builds the complete user prompt.
    """

    sections = [_build_header()]

    for index, article in enumerate(cluster, start=1):
        sections.append(_build_article(article, index))

    sections.append(_build_footer())

    return "\n".join(sections)