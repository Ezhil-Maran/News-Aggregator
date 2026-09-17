"""
test_pipeline.py

Tests the complete live AI news generation pipeline.
"""

import asyncio

from app.services.pipeline import run_pipeline


async def main():

    print("\n" + "=" * 80)
    print("FULL LIVE NEWS PIPELINE TEST")
    print("=" * 80)

    result = await run_pipeline()

    print("\n" + "=" * 80)
    print("PIPELINE RESULT")
    print("=" * 80)

    print("\nSuccess:")
    print(result.get("success"))

    print("\nStatistics:")
    print(result.get("statistics"))

    print("\nProcessing Time:")
    print(
        f"{result.get('processing_time_seconds')} seconds"
    )

    print("\nGenerated Articles:")

    for index, article in enumerate(
        result.get("generated_articles", []),
        start=1,
    ):

        print("\n" + "-" * 80)
        print(f"ARTICLE {index}")
        print("-" * 80)

        print("\nHeadline:")
        print(article.get("headline"))

        print("\nContent:")
        print(article.get("content"))

        print("\nSources:")
        print(article.get("sources"))

        print("\nArticles Used:")
        print(article.get("article_count"))

    print("\nSingle Source Articles:")
    print(
        len(result.get("single_source_articles", []))
    )


if __name__ == "__main__":
    asyncio.run(main())