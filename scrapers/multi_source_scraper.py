from __future__ import annotations

import json
import re
from typing import Any

import feedparser
import requests
from bs4 import BeautifulSoup

from config import RSS_FEEDS


class MultiSourceScraper:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
            }
        )

    def collect_articles(self) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []

        collected.extend(self._collect_social_and_forum_sources())

        for url in RSS_FEEDS:
            collected.extend(self._collect_rss_feed(url))

        return collected

    def _collect_rss_feed(self, url: str) -> list[dict[str, Any]]:
        try:
            feed = feedparser.parse(url)
        except Exception:
            return []

        source = feed.feed.get("title", url)
        articles: list[dict[str, Any]] = []
        for item in feed.entries:
            articles.append(
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "source": source,
                    "date": item.get("published", ""),
                    "summary": item.get("summary", ""),
                    "source_type": "rss",
                }
            )
        return articles

    def _collect_social_and_forum_sources(self) -> list[dict[str, Any]]:
        sources = [
            "https://hnrss.org/newest",
            "https://www.reddit.com/r/UnconfirmedKillers/.rss",
            "https://www.reddit.com/r/TrueCrime/.rss",
            "https://www.reddit.com/r/Crime/.rss",
            "https://www.reddit.com/r/CrimeScene/.rss",
            "https://www.reddit.com/r/UnresolvedMysteries/.rss",
            "https://www.reddit.com/r/serialkillers/.rss",
            "https://www.reddit.com/r/AskReddit/.rss",
            "https://www.reddit.com/r/news/.rss",
            "https://www.reddit.com/r/technology/.rss",
            "https://feeds.feedburner.com/TechCrunch/",
            "https://www.reuters.com/world/rss",
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://feeds.feedburner.com/AllArticlesNewAmericaMedia",
        ]

        collected: list[dict[str, Any]] = []
        for url in sources:
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                feed = feedparser.parse(response.text)
                source = feed.feed.get("title", url)
                for item in feed.entries:
                    collected.append(
                        {
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "source": source,
                            "date": item.get("published", ""),
                            "summary": item.get("summary", ""),
                            "source_type": "community",
                        }
                    )
            except Exception:
                continue
        return collected
