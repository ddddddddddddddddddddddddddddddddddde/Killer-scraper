import feedparser

from config import RSS_FEEDS


def collect_articles():
    collected = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        source = feed.feed.get("title", url)

        for item in feed.entries:
            collected.append(
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "source": source,
                    "date": item.get("published", ""),
                    "summary": item.get("summary", ""),
                    "source_type": "rss",
                }
            )

    return collected
