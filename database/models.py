from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Article(Base):

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)

    link = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    source = Column(String)

    source_type = Column(String, default="unknown")

    date = Column(String)

    summary = Column(Text)

    score = Column(Integer, default=0)

    priority = Column(Integer, default=0)

    status = Column(String, default="new")


class RedditPost(Base):

    __tablename__ = "reddit_posts"

    id = Column(Integer, primary_key=True)

    article_id = Column(
        Integer,
        ForeignKey("articles.id"),
        unique=True,
        nullable=False,
    )

    subreddit = Column(String, nullable=False)

    reddit_post_id = Column(
        String,
        unique=True,
        nullable=True,
    )

    reddit_url = Column(String, nullable=True)

    status = Column(
        String,
        nullable=False,
        default="pending",
    )

    error_message = Column(Text, nullable=True)

    created_at = Column(
        String,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )
