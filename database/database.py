from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "sentinel.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}")

Session = sessionmaker(bind=engine)


def initialize_schema() -> None:
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE IF NOT EXISTS articles (id INTEGER PRIMARY KEY AUTOINCREMENT)"))

        existing_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(articles)"))
        }

        for column_name, column_type in [
            ("title", "TEXT"),
            ("link", "TEXT"),
            ("source", "TEXT"),
            ("source_type", "TEXT"),
            ("date", "TEXT"),
            ("summary", "TEXT"),
            ("ai_summary", "TEXT"),
            ("score", "INTEGER"),
            ("priority", "INTEGER"),
            ("status", "TEXT DEFAULT 'new'"),
        ]:
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE articles ADD COLUMN {column_name} {column_type}"))

