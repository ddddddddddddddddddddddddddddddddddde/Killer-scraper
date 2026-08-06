from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database.storage as storage
from database.models import Article, Base


def test_save_articles_persists_source_type(tmp_path, monkeypatch):
    db_path = tmp_path / "sentinel-test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    monkeypatch.setattr(storage, "Session", TestSession)

    added = storage.save_articles(
        [
            {
                "title": "Test article",
                "link": "https://example.com/test",
                "source": "Example News",
                "source_type": "community",
                "date": "2026-08-05",
                "summary": "A test article",
                "score": 3,
                "priority": 4,
            }
        ]
    )

    assert added == 1

    with TestSession() as session:
        article = session.query(Article).one()
        assert article.source_type == "community"
        assert article.priority == 4
