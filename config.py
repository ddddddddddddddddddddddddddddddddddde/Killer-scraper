import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Sentinel OSINT Monitor"

DATABASE = "data/sentinel.db"

# How often main.py's scheduler re-runs the full scan.
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=homicide",
    "https://news.google.com/rss/search?q=missing+person",
    "https://news.google.com/rss/search?q=unidentified+remains",
    "https://news.google.com/rss/search?q=suspicious+death",
    "https://news.google.com/rss/search?q=police+scanner",
    "https://news.google.com/rss/search?q=police+report",
    "https://news.google.com/rss/search?q=police+blotter",
    "https://news.google.com/rss/search?q=police+dispatch",
    "https://news.google.com/rss/search?q=911+call",
    "https://news.google.com/rss/search?q=active+police+scene",
    "https://news.google.com/rss/search?q=officer+involved",
    "https://news.google.com/rss/search?q=breaking+police+news",
]

# Police-scanner-style feeds that publish live dispatch/incident chatter.
POLICE_SCANNER_FEEDS = [
    "https://www.broadcastify.com/calls/rss",
    "https://www.broadcastify.com/rss/feeds.rss",
]

KEYWORDS = [
    "missing",
    "found dead",
    "homicide",
    "unidentified",
    "body found",
    "investigation",
    "suspicious death",
    "murder",
    "killers",
    "fatal",
    "deceased",
    "cold case",
    "disappearance",
    "person of interest",
    "suspect",
    "police",
    "authorities",
    "remains",
    "victim",
    "abduction",
    "kidnapping",
    "unconfirmed",
    "unknown identity",
    "police scanner",
    "scanner traffic",
    "police report",
    "police blotter",
    "dispatch",
    "911 call",
    "active scene",
    "officer involved",
    "all units",
    "bolo",
]

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_SUBREDDIT = os.getenv("REDDIT_SUBREDDIT")
REDDIT_USER_AGENT = os.getenv(
    "REDDIT_USER_AGENT",
    "windows:sentinel-osint-monitor:v1.2.0",
)

REDDIT_POST_MODE = os.getenv(
    "REDDIT_POST_MODE",
    "dry_run",
).lower()

REDDIT_MIN_SCORE = int(
    os.getenv("REDDIT_MIN_SCORE", "2")
)

REDDIT_MAX_POSTS_PER_RUN = int(
    os.getenv("REDDIT_MAX_POSTS_PER_RUN", "3")
)

REDDIT_DELAY_SECONDS = int(
    os.getenv("REDDIT_DELAY_SECONDS", "20")
)

