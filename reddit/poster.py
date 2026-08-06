import logging
import time
from typing import Optional

import prawcore
from sqlalchemy.orm import Session as SessionType

from config import (
    REDDIT_DELAY_SECONDS,
    REDDIT_MAX_POSTS_PER_RUN,
    REDDIT_MIN_SCORE,
    REDDIT_POST_MODE,
    REDDIT_SUBREDDIT,
)
from database.models import Article, RedditPost
from reddit.client import get_reddit_client, validate_reddit_config
from reddit.formatter import format_reddit_post

logger = logging.getLogger("Sentinel")

VALID_POST_MODES = {"disabled", "dry_run", "automatic"}


def validate_posting_settings() -> None:
    if REDDIT_POST_MODE not in VALID_POST_MODES:
        raise RuntimeError(
            "REDDIT_POST_MODE must be 'disabled', 'dry_run', or 'automatic'."
        )

    if not REDDIT_SUBREDDIT:
        raise RuntimeError("REDDIT_SUBREDDIT is missing.")

    if REDDIT_POST_MODE == "automatic":
        validate_reddit_config(allow_missing=False)


def get_post_candidates(session: SessionType) -> list[Article]:
    already_processed = session.query(RedditPost.article_id).subquery()

    return (
        session.query(Article)
        .filter(Article.score >= REDDIT_MIN_SCORE)
        .filter(~Article.id.in_(session.query(already_processed.c.article_id)))
        .order_by(Article.score.desc(), Article.id.asc())
        .limit(REDDIT_MAX_POSTS_PER_RUN)
        .all()
    )


def create_tracking_record(session: SessionType, article: Article, status: str) -> RedditPost:
    record = RedditPost(article_id=article.id, subreddit=REDDIT_SUBREDDIT, status=status)
    session.add(record)
    session.flush()
    return record


def post_article(session: SessionType, article: Article, reddit) -> Optional[str]:
    title, body = format_reddit_post(article)

    if REDDIT_POST_MODE == "dry_run":
        create_tracking_record(session=session, article=article, status="dry_run")
        logger.info("Dry run for article %s: %s", article.id, title)
        print("\n" + "=" * 70)
        print("REDDIT DRY RUN")
        print("=" * 70)
        print(f"Subreddit: r/{REDDIT_SUBREDDIT}")
        print(f"Title: {title}")
        print("-" * 70)
        print(body)
        print("=" * 70)
        return None

    record = create_tracking_record(session=session, article=article, status="pending")

    try:
        subreddit = reddit.subreddit(REDDIT_SUBREDDIT)
        submission = subreddit.submit(title=title, selftext=body, send_replies=False)

        record.reddit_post_id = submission.id
        record.reddit_url = f"https://www.reddit.com{submission.permalink}"
        record.status = "posted"
        article.status = "posted"

        logger.info("Posted article %s to %s", article.id, record.reddit_url)
        return record.reddit_url

    except (
        prawcore.exceptions.Forbidden,
        prawcore.exceptions.OAuthException,
        prawcore.exceptions.ResponseException,
        prawcore.exceptions.ServerError,
        prawcore.exceptions.TooManyRequests,
    ) as error:
        record.status = "failed"
        record.error_message = str(error)
        logger.exception("Reddit posting failed for article %s", article.id)
        return None


def publish_pending_articles(session: SessionType) -> int:
    validate_posting_settings()

    if REDDIT_POST_MODE == "disabled":
        logger.info("Reddit posting is disabled.")
        return 0

    candidates = get_post_candidates(session)

    if not candidates:
        logger.info("No Reddit post candidates found.")
        return 0

    reddit = None

    if REDDIT_POST_MODE == "automatic":
        reddit = get_reddit_client()
        authenticated_user = reddit.user.me()
        logger.info("Authenticated to Reddit as %s", authenticated_user)

    successful_posts = 0

    for index, article in enumerate(candidates):
        url = post_article(session=session, article=article, reddit=reddit)
        session.commit()

        if url:
            successful_posts += 1
            print(f"Posted: {url}")

        should_pause = REDDIT_POST_MODE == "automatic" and index < len(candidates) - 1
        if should_pause:
            time.sleep(REDDIT_DELAY_SECONDS)

    return successful_posts
