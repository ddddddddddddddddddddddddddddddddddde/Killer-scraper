import logging
from pathlib import Path

from config import KEYWORDS, SCAN_INTERVAL_SECONDS
from database.database import engine, initialize_schema
from database.models import Base
from database.storage import save_articles
from logs.logger import logger
from scrapers.multi_source_scraper import MultiSourceScraper

Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename="logs/sentinel.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

initialize_schema()
Base.metadata.create_all(engine)


def calculate_score(article: dict) -> int:
    text = (
        article.get("title", "")
        + " "
        + article.get("summary", "")
    ).lower()

    keyword_hits = sum(
        1
        for keyword in KEYWORDS
        if keyword.lower() in text
    )

    urgency_terms = [
        "dead",
        "missing",
        "remains",
        "abduction",
        "kidnapping",
        "victim",
        "suspect",
        "authorities",
        "police",
        "investigation",
        "cold case",
    ]

    urgency_hits = sum(1 for term in urgency_terms if term.lower() in text)

    source_strength = 1 if article.get("source_type") in {"community", "rss"} else 0
    if article.get("source_type") == "police_scanner":
        source_strength = 2

    return keyword_hits + urgency_hits + source_strength


def calculate_priority(article: dict) -> int:
    base_score = calculate_score(article)
    if article.get("source_type") == "police_scanner":
        source_strength = 3
    elif article.get("source_type") == "community":
        source_strength = 2
    else:
        source_strength = 1
    title_boost = 1 if article.get("title", "").isupper() else 0
    return base_score + source_strength + title_boost


def run_scan() -> None:
    logger.info("Starting Sentinel scan.")

    scraper = MultiSourceScraper()
    collected = scraper.collect_articles()

    filtered = []

    for article in collected:
        article["score"] = calculate_score(article)
        article["priority"] = calculate_priority(article)

        if article["priority"] >= 2:
            filtered.append(article)

    added = save_articles(filtered)

    from collections import Counter

    source_counts = Counter(article.get("source", "") for article in collected)

    print(f"Collected: {len(collected)}")
    print(f"Matched:   {len(filtered)}")
    print(f"Added:     {added}")
    print("Source counts:")
    for source, count in source_counts.most_common(10):
        print(f"  - {source}: {count}")

    logger.info("Sentinel scan complete.")
    print("Sentinel scan complete.")


def run_forever() -> None:
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler()
    scheduler.add_job(run_scan, "interval", seconds=SCAN_INTERVAL_SECONDS)
    logger.info("Sentinel scheduler starting: scanning every %s seconds.", SCAN_INTERVAL_SECONDS)

    run_scan()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Sentinel scheduler stopped.")


if __name__ == "__main__":
    run_forever()
