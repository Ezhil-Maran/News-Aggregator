import asyncio

from app.services.news_fetcher import fetch_all_feeds
from app.services.clustering import cluster_articles


async def main():

    print("\n" + "=" * 80)
    print("LIVE CLUSTERING TEST")
    print("=" * 80)

    articles = await fetch_all_feeds()

    print(f"\nFetched articles: {len(articles)}")

    clusters = cluster_articles(articles)

    print(f"Clusters formed: {len(clusters)}")

    multi_source = [
        cluster
        for cluster in clusters
        if len(cluster) > 1
    ]

    print(
        f"Multi-source clusters: "
        f"{len(multi_source)}"
    )

    print("\n" + "-" * 80)
    print("MULTI-SOURCE CLUSTERS")
    print("-" * 80)

    for index, cluster in enumerate(
        multi_source,
        start=1,
    ):

        print(
            f"\nCluster {index} "
            f"({len(cluster)} articles)"
        )

        for article in cluster:
            print(
                f"  - {article.get('domain')}: "
                f"{article.get('title')}"
            )


if __name__ == "__main__":
    asyncio.run(main())