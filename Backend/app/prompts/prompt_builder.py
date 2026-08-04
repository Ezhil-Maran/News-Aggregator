"""
prompt_builder.py

Builds the user prompt from a cluster of related news articles.

This module ONLY prepares the news reports and task instructions.
The AI behaviour itself is defined in system_prompt.py.
"""

from typing import Dict, List


# ============================================================
# HEADER
# ============================================================

def _build_header() -> str:
    """
    Builds the task description shown before the reports.
    """

    return (
        "You are provided with multiple news reports describing the SAME news event.\n\n"

        "Your objective is to merge these reports into ONE complete, accurate and "
        "professional news article.\n\n"

        "Before writing:\n"
        "1. Identify the primary event.\n"
        "2. Merge overlapping facts.\n"
        "3. Remove duplicate information.\n"
        "4. Preserve unique verified details.\n"
        "5. Ignore unsupported or conflicting claims.\n"
        "6. Produce ONE publication-ready news article.\n\n"

        "Use ONLY the information contained in the reports below.\n\n"
    )


# ============================================================
# SINGLE REPORT
# ============================================================

def _build_article(article: Dict, index: int) -> str:
    """
    Formats one news report.
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
        f"{'=' * 80}\n"
        f"REPORT {index}\n"
        f"{'=' * 80}\n\n"

        f"Source:\n"
        f"{source}\n\n"

        f"Title:\n"
        f"{title}\n\n"

        f"Published:\n"
        f"{published}\n\n"

        f"Content:\n"
        f"{content}\n\n"
    )


# ============================================================
# FOOTER
# ============================================================

def _build_footer() -> str:
    """
    Final instructions before generation.
    """

    return (
        f"{'=' * 80}\n"
        "END OF REPORTS\n"
        f"{'=' * 80}\n\n"

        "Now write ONE complete professional news article.\n\n"

        "Requirements:\n"
        "- Write a concise factual headline.\n"
        "- Begin with a strong lead paragraph.\n"
        "- Organize information logically.\n"
        "- Avoid repeating facts.\n"
        "- Do not speculate.\n"
        "- Do not mention the reports.\n"
        "- Follow the required output format exactly.\n"
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
        sections.append(
            _build_article(article, index)
        )

    sections.append(
        _build_footer()
    )

    return "\n".join(sections)