"""
prompt_builder.py

Builds a structured prompt for the language model from a cluster
of related news articles.

This module is responsible only for prompt construction.
It does NOT perform inference or interact with the model.

Public API
----------
build_news_prompt(cluster: List[Dict]) -> str
"""

from typing import Dict, List


# ============================================================
# HEADER
# ============================================================

def _build_header() -> str:
    """
    Returns the introductory section of the prompt.
    """

    return (
        "Below are multiple news reports describing the same event.\n\n"
        "Each report may contain overlapping or unique information.\n"
        "Read every article carefully before generating the final article.\n\n"
    )


# ============================================================
# ARTICLE FORMATTER
# ============================================================

def _build_article(article: Dict, index: int) -> str:
    """
    Formats a single article for the prompt.

    Missing fields are replaced with sensible defaults.
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
        f"{'=' * 60}\n"
        f"Article {index}\n"
        f"{'=' * 60}\n\n"
        f"Title:\n"
        f"{title}\n\n"
        f"Source:\n"
        f"{source}\n\n"
        f"Published:\n"
        f"{published}\n\n"
        f"Content:\n"
        f"{content}\n\n"
    )


# ============================================================
# INSTRUCTIONS
# ============================================================

def _build_instructions() -> str:
    """
    Returns the final instructions for the model.
    """

    return (
        "\n"
        + "=" * 60
        + "\n"
        "TASK\n"
        + "=" * 60
        + "\n\n"
        "Construct ONE professional news article using all the reports above.\n\n"
        "Requirements:\n\n"
        "- Preserve factual accuracy.\n"
        "- Never invent information.\n"
        "- Remove duplicate information.\n"
        "- Merge overlapping facts naturally.\n"
        "- Maintain a neutral journalistic tone.\n"
        "- Preserve important names, places and dates.\n"
        "- Present information in a logical order.\n"
        "- Do not mention that multiple reports were provided.\n"
        "- Do not produce bullet points.\n"
        "- Create an engaging headline.\n"
        "- Write a complete article with an introduction, body and conclusion.\n\n"
        "Return ONLY the final news article."
    )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def build_news_prompt(cluster: List[Dict]) -> str:
    """
    Builds a complete prompt from a cluster of related articles.

    Parameters
    ----------
    cluster : List[Dict]
        List of related news articles.

    Returns
    -------
    str
        Prompt ready to be sent to the LLM.
    """

    sections = [_build_header()]

    for index, article in enumerate(cluster, start=1):
        sections.append(_build_article(article, index))

    sections.append(_build_instructions())

    return "\n".join(sections)