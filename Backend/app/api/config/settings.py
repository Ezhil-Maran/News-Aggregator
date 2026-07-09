# settings.py

DB_PATH = "news_cache.db"

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.theguardian.com/world/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "http://rss.cnn.com/rss/edition_world.rss",
    "https://www.thehindu.com/news/national/feeder/default.rss"
]

FETCH_TIMEOUT = 20

MAX_ARTICLES_PER_FEED = 30

TITLE_OVERLAP_THRESHOLD = 3