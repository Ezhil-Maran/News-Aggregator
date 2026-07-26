"""
test_qwen.py

Development test for the AI news generation pipeline.

This script verifies that:
1. The Qwen model loads correctly.
2. The prompt builder constructs the prompt.
3. The inference module generates a consolidated news article.
"""

from app.services.inference import generate_article


def test_article_generation():
    """
    Tests the complete article generation pipeline using
    a manually created cluster of related news articles.
    """

    cluster = [
        {
            "title": "Apple launches iPhone 18",
            "content": (
                "Apple unveiled the iPhone 18 during its annual event "
                "in California. The smartphone introduces improved "
                "AI capabilities, a redesigned camera system, and a "
                "more efficient processor."
            ),
            "domain": "The Verge",
            "published": "2026-07-22",
        },
        {
            "title": "Apple announces new iPhone 18",
            "content": (
                "During its keynote presentation, Apple introduced the "
                "iPhone 18 featuring advanced AI-powered features, "
                "longer battery life, and a next-generation chipset."
            ),
            "domain": "TechCrunch",
            "published": "2026-07-22",
        },
        {
            "title": "Apple reveals next-generation iPhone",
            "content": (
                "Apple revealed the iPhone 18 with enhanced "
                "photography capabilities, on-device AI, and "
                "significant performance improvements."
            ),
            "domain": "Reuters",
            "published": "2026-07-22",
        },
    ]

    article = generate_article(cluster)

    print("\n" + "=" * 80)
    print("GENERATED ARTICLE")
    print("=" * 80 + "\n")

    print(article)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_article_generation()