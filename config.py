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

# Free, script-friendly Socrata open-data 911/CAD feeds (no key/login, not
# bot-walled like OpenMHz/Broadcastify). Mix of a major city and smaller
# counties/towns, each refreshing continuously through the day.
OPEN_DATA_SCANNER_FEEDS = [
    {
        "label": "Seattle Fire 911 Dispatch",
        "domain": "data.seattle.gov",
        "resource_id": "kzjm-xkqj",
        "time_field": "datetime",
        "title_field": "type",
        "location_field": "address",
        "id_field": "incident_number",
    },
    {
        "label": "Seattle Police Calls for Service",
        "domain": "data.seattle.gov",
        "resource_id": "33kz-ixgy",
        "time_field": "cad_event_original_time_queued",
        "title_field": "initial_call_type",
        "location_field": "dispatch_address",
        "id_field": "cad_event_number",
    },
    {
        "label": "Montgomery County MD Police Dispatch",
        "domain": "data.montgomerycountymd.gov",
        "resource_id": "98cc-bc7d",
        "time_field": "start_time",
        "title_field": "initial_type",
        "location_field": "address",
        "id_field": "incident_id",
        "extra_field": "disposition_desc",
    },
    {
        "label": "Everett WA Police Incidents",
        "domain": "data.everettwa.gov",
        "resource_id": "f6vp-3svh",
        "time_field": "datetimereceived",
        "title_field": "incidenttype",
        "location_field": "eventaddressby100block",
        "id_field": "eventnumber",
    },
    {
        "label": "Winnebago County IL Dispatch Log",
        "domain": "illinois-edp.data.socrata.com",
        "resource_id": "i96m-iu3n",
        "time_field": "dispatch_date_time",
        "title_field": "incident_type_desc_display",
        "location_field": "full_address",
        "id_field": "event_number",
    },
]

# Records fetched per open-data feed per scan; duplicates are skipped by link.
OPEN_DATA_FEED_LIMIT = int(os.getenv("OPEN_DATA_FEED_LIMIT", "25"))

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

