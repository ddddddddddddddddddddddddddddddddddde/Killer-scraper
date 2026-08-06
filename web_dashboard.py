from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from flask import Flask, render_template_string, request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database.models import Base


HTML_TEMPLATE = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Sentinel Dashboard</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body {
      font-family: Inter, Segoe UI, Arial, sans-serif;
      margin: 0;
      background: linear-gradient(135deg, #07111f 0%, #10243d 100%);
      color: #f5f7fb;
      min-height: 100vh;
    }
    .wrap { max-width: 1380px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }
    .hero {
      padding: 1.3rem 1.4rem;
      border-radius: 18px;
      background: rgba(255,255,255,0.06);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255,255,255,0.1);
      margin-bottom: 1rem;
      box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .hero h1 { margin: 0 0 0.4rem; font-size: 1.7rem; }
    .hero p { margin: 0; color: #b8c4d9; }
    .card {
      background: rgba(9, 18, 32, 0.86);
      padding: 1rem 1.2rem;
      border-radius: 16px;
      margin-bottom: 1rem;
      border: 1px solid rgba(255,255,255,0.08);
      box-shadow: 0 10px 24px rgba(0,0,0,0.19);
    }
    .card h2 { margin-top: 0; margin-bottom: 0.6rem; font-size: 1.1rem; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid rgba(255,255,255,0.08); padding: 0.7rem 0.55rem; text-align: left; vertical-align: top; }
    th { color: #8ca3be; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; }
    tbody tr:hover { background: rgba(255,255,255,0.035); }
    a { color: #74b9ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .pill {
      display: inline-block;
      padding: 0.25rem 0.6rem;
      border-radius: 999px;
      background: linear-gradient(90deg, #2c4f7d, #4a6c93);
      font-size: 0.82rem;
      color: #f7fbff;
    }
    .muted { color: #92a2b8; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>Sentinel Dashboard</h1>
      <p>Local backup view for collected articles.</p>
    </div>

  <div class=\"card\">
    <h2>Articles</h2>
    <table>
      <thead><tr><th>Title</th><th>Source</th><th>Type</th><th>Score</th><th>Priority</th><th>Collected</th><th>Status</th></tr></thead>
      <tbody>
      {% for article in articles %}
      <tr>
        <td><a href=\"{{ article.link }}\" target=\"_blank\" rel=\"noreferrer\">{{ article.title }}</a></td>
        <td>{{ article.source or 'n/a' }}</td>
        <td>{{ article.source_type or 'n/a' }}</td>
        <td>{{ article.score }}</td>
        <td>{{ article.priority }}</td>
        <td>{{ article.collected_at or 'n/a' }}</td>
        <td><span class=\"pill\">{{ article.status }}</span></td>
      </tr>
      {% else %}
      <tr><td colspan="7">No articles found yet.</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>

</body>
</html>
"""


def create_app(database_path: Optional[str] = None) -> Flask:
    app = Flask(__name__)

    db_path = Path(database_path or os.getenv("SENTINEL_DB_PATH") or Path(__file__).resolve().parent / "data" / "sentinel.db")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    @app.get("/")
    def index() -> str:
        session = Session()
        try:
            articles = session.execute(
                text(
                    "SELECT title, link, source, source_type, score, priority, date, status FROM articles ORDER BY id DESC LIMIT 50"
                )
            ).fetchall()
            article_rows = [
                {
                    "title": row[0],
                    "link": row[1],
                    "source": row[2],
                    "source_type": row[3],
                    "score": row[4],
                    "priority": row[5],
                    "collected_at": row[6],
                    "status": row[7],
                }
                for row in articles
            ]
        finally:
            session.close()

        return render_template_string(
            HTML_TEMPLATE,
            articles=article_rows,
        )

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
