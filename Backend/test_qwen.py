"""
test_qwen.py

Tests the complete article generation pipeline.
"""

from datasets.sample_cluster import SAMPLE_CLUSTER

from app.services.article_generator import generate_article


def main():

    article = generate_article(SAMPLE_CLUSTER)

    print("\n" + "=" * 80)
    print("GENERATED ARTICLE")
    print("=" * 80)

    print("\nHeadline\n")
    print(article["headline"])

    print("\nArticle\n")
    print(article["content"])

    print("\nSources\n")
    print(article["sources"])

    print("\nArticles Used\n")
    print(article["article_count"])


if __name__ == "__main__":
    main()