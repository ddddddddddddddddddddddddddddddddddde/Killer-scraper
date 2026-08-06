from database.database import Session
from database.models import Article


def save_articles(article_list):
    session = Session()
    added = 0

    for article in article_list:
        article_data = dict(article)
        article_data.pop("analysis", None)

        article_data.setdefault("title", "")
        article_data.setdefault("link", "")
        article_data.setdefault("source", "unknown")
        article_data.setdefault("source_type", "unknown")
        article_data.setdefault("date", "")
        article_data.setdefault("summary", "")
        article_data.setdefault("ai_summary", "")
        article_data.setdefault("score", 0)
        article_data.setdefault("priority", 0)
        article_data.setdefault("source_type", "unknown")
        article_data.setdefault("status", "new")

        exists = (
            session.query(Article)
            .filter_by(link=article_data["link"])
            .first()
        )

        if exists:
            continue

        new_article = Article(**article_data)
        session.add(new_article)
        added += 1

    session.commit()
    session.close()
    return added
