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
    tbody tr.row { cursor: pointer; }
    tbody tr.row:hover { background: rgba(255,255,255,0.035); }
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
    .caret { display: inline-block; margin-right: 0.5rem; color: #74b9ff; transition: transform 0.15s ease; }
    tr.row.open .caret { transform: rotate(90deg); }
    tr.details { display: none; background: rgba(255,255,255,0.03); }
    tr.details.open { display: table-row; }
    tr.details td { padding: 0.9rem 1.1rem 1.1rem 2rem; }
    .detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.6rem 1.5rem; margin-bottom: 0.7rem; }
    .detail-grid div span.label { display: block; color: #8ca3be; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.15rem; }
    .detail-summary { color: #dbe4f2; line-height: 1.5; white-space: pre-wrap; }
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
      <thead><tr><th></th><th>Title</th><th>Source</th><th>Type</th><th>Score</th><th>Priority</th><th>Collected</th><th>Status</th></tr></thead>
      <tbody>
      {% for article in articles %}
      <tr class="row" onclick="toggleDetails({{ loop.index }})">
        <td><span class="caret">&#9656;</span></td>
        <td>{{ article.title }}</td>
        <td>{{ article.source or 'n/a' }}</td>
        <td>{{ article.source_type or 'n/a' }}</td>
        <td>{{ article.score }}</td>
        <td>{{ article.priority }}</td>
        <td>{{ article.collected_at or 'n/a' }}</td>
        <td><span class=\"pill\">{{ article.status }}</span></td>
      </tr>
      <tr class="details" id="details-{{ loop.index }}">
        <td colspan="8">
          <div class="detail-grid">
            <div><span class="label">Source</span>{{ article.source or 'n/a' }}</div>
            <div><span class="label">Type</span>{{ article.source_type or 'n/a' }}</div>
            <div><span class="label">Score</span>{{ article.score }}</div>
            <div><span class="label">Priority</span>{{ article.priority }}</div>
            <div><span class="label">Collected</span>{{ article.collected_at or 'n/a' }}</div>
            <div><span class="label">Status</span>{{ article.status }}</div>
          </div>
          <div><span class="label">Summary</span></div>
          <p class="detail-summary">{{ article.summary or 'No summary available.' }}</p>
          <p><a href=\"{{ article.link }}\" target=\"_blank\" rel=\"noreferrer\" onclick=\"event.stopPropagation()\">Open original source &#8594;</a></p>
        </td>
      </tr>
      {% else %}
      <tr><td colspan="8">No articles found yet.</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>

</body>
<script>
  function toggleDetails(index) {
    var detailsRow = document.getElementById('details-' + index);
    var row = detailsRow.previousElementSibling;
    var isOpen = detailsRow.classList.toggle('open');
    row.classList.toggle('open', isOpen);
  }
</script>
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
                    "SELECT title, link, source, source_type, score, priority, date, status, summary FROM articles ORDER BY id DESC LIMIT 50"
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
                    "summary": row[8],
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
