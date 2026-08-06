import tempfile
import unittest
from pathlib import Path

from database.database import initialize_schema
from database.models import Base
from database.storage import save_articles
from scrapers.rss_scraper import collect_articles

initialize_schema()


class SentinelOsintTests(unittest.TestCase):
    def test_parse_feed_content_and_store_articles(self) -> None:
        xml_text = """<?xml version=\"1.0\"?>
        <rss version=\"2.0\">
            <channel>
                <title>Example News</title>
                <item>
                    <title>First story</title>
                    <link>https://example.com/1</link>
                    <description>First summary</description>
                    <pubDate>Tue, 05 Aug 2026 12:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>"""

        articles = [{
            "title": "First story",
            "link": "https://example.com/1",
            "source": "example",
            "date": "Tue, 05 Aug 2026 12:00:00 GMT",
            "summary": "First summary",
            "score": 2,
            "status": "new",
        }]

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "First story")
        self.assertEqual(articles[0]["source"], "example")

        with tempfile.TemporaryDirectory() as tmpdir:
            from database import database as database_module

            database_module.DB_PATH = Path(tmpdir) / "sentinel_test.db"
            database_module.engine = database_module.create_engine(f"sqlite:///{database_module.DB_PATH}")
            database_module.Session = database_module.sessionmaker(bind=database_module.engine)
            import database.storage as storage_module
            storage_module.Session = database_module.Session
            initialize_schema()
            Base.metadata.create_all(database_module.engine)

            saved_count = save_articles(articles)
            self.assertEqual(saved_count, 1)

            from sqlalchemy import text

            with database_module.engine.begin() as connection:
                connection.execute(text("SELECT 1"))

            database_module.engine.dispose()


if __name__ == "__main__":
    unittest.main()
