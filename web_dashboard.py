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
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap\" rel=\"stylesheet\">
  <style>
    :root {
      color-scheme: dark;
      --bg-0: #05080f;
      --bg-1: #0a1526;
      --accent: #4fd1c5;
      --accent-2: #7c9dff;
      --danger: #ff5d7a;
      --warn: #ffb454;
      --ok: #4fd1c5;
      --text: #eef2fb;
      --muted: #8ca3be;
      --border: rgba(255,255,255,0.08);
    }
    * { box-sizing: border-box; }
    body {
      font-family: 'Inter', Segoe UI, Arial, sans-serif;
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      background:
        radial-gradient(1200px 600px at 15% -10%, rgba(79,209,197,0.16), transparent 60%),
        radial-gradient(1000px 500px at 110% 10%, rgba(124,157,255,0.14), transparent 55%),
        linear-gradient(160deg, var(--bg-0) 0%, var(--bg-1) 55%, #0b1c33 100%);
      background-attachment: fixed;
    }
    .wrap { max-width: 1440px; margin: 0 auto; padding: 2.2rem 1.5rem 3.5rem; }

    .hero {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1.5rem;
      flex-wrap: wrap;
      padding: 1.6rem 1.8rem;
      border-radius: 20px;
      background: linear-gradient(120deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
      backdrop-filter: blur(14px);
      border: 1px solid var(--border);
      margin-bottom: 1.6rem;
      box-shadow: 0 20px 50px rgba(0,0,0,0.35);
      position: relative;
      overflow: hidden;
    }
    .hero::before {
      content: "";
      position: absolute; inset: 0;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
      opacity: 0.06;
      pointer-events: none;
    }
    .hero-title { display: flex; align-items: center; gap: 0.85rem; }
    .hero-title .logo {
      width: 46px; height: 46px; border-radius: 14px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.4rem;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      box-shadow: 0 8px 20px rgba(79,209,197,0.35);
    }
    .hero h1 { margin: 0; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; }
    .hero p { margin: 0.15rem 0 0; color: var(--muted); font-size: 0.92rem; }
    .live-badge {
      display: inline-flex; align-items: center; gap: 0.5rem;
      padding: 0.45rem 0.9rem; border-radius: 999px;
      background: rgba(79,209,197,0.12); border: 1px solid rgba(79,209,197,0.35);
      color: var(--accent); font-size: 0.8rem; font-weight: 600; letter-spacing: 0.03em;
    }
    .live-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 rgba(79,209,197,0.6); animation: pulse 1.8s infinite; }
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(79,209,197,0.55); }
      70% { box-shadow: 0 0 0 9px rgba(79,209,197,0); }
      100% { box-shadow: 0 0 0 0 rgba(79,209,197,0); }
    }

    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 1rem; margin-bottom: 1.4rem; }
    .stat-card {
      padding: 1.1rem 1.3rem; border-radius: 16px;
      background: rgba(255,255,255,0.045);
      border: 1px solid var(--border);
      box-shadow: 0 10px 24px rgba(0,0,0,0.2);
      transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .stat-card:hover { transform: translateY(-2px); border-color: rgba(79,209,197,0.4); }
    .stat-card .label { color: var(--muted); font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem; }
    .stat-card .value { font-size: 1.7rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
    .stat-card .value.danger { color: var(--danger); }
    .stat-card .value.accent { color: var(--accent); }
    .stat-card .value.warn { color: var(--warn); }

    .card {
      background: rgba(9, 18, 32, 0.78);
      padding: 1.2rem 1.3rem 0.4rem;
      border-radius: 18px;
      margin-bottom: 1rem;
      border: 1px solid var(--border);
      box-shadow: 0 15px 35px rgba(0,0,0,0.25);
    }
    .card-head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 0.9rem; }
    .card h2 { margin: 0; font-size: 1.05rem; font-weight: 700; }
    .search-box {
      display: flex; align-items: center; gap: 0.5rem;
      background: rgba(255,255,255,0.05); border: 1px solid var(--border);
      border-radius: 10px; padding: 0.5rem 0.8rem; min-width: 240px;
    }
    .search-box input {
      background: transparent; border: none; outline: none; color: var(--text);
      font-family: inherit; font-size: 0.88rem; width: 100%;
    }
    .search-box input::placeholder { color: var(--muted); }
    .search-box svg { flex-shrink: 0; opacity: 0.6; }

    table { width: 100%; border-collapse: collapse; }
    .table-scroll { overflow-x: auto; }
    th, td { border-bottom: 1px solid var(--border); padding: 0.75rem 0.6rem; text-align: left; vertical-align: top; font-size: 0.9rem; }
    th { color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.09em; font-weight: 600; }
    tbody tr.row { cursor: pointer; transition: background 0.12s ease; }
    tbody tr.row:hover { background: rgba(79,209,197,0.06); }
    tbody tr.row td:nth-child(2) { font-weight: 600; }
    a { color: var(--accent-2); text-decoration: none; }
    a:hover { text-decoration: underline; }

    .pill {
      display: inline-flex; align-items: center; gap: 0.3rem;
      padding: 0.28rem 0.65rem;
      border-radius: 999px;
      font-size: 0.76rem;
      font-weight: 600;
      letter-spacing: 0.02em;
    }
    .pill-status { background: linear-gradient(90deg, #2c4f7d, #4a6c93); color: #f7fbff; }
    .pill-source { background: rgba(124,157,255,0.14); color: var(--accent-2); border: 1px solid rgba(124,157,255,0.3); }
    .pill-source.police_scanner { background: rgba(255,93,122,0.14); color: var(--danger); border-color: rgba(255,93,122,0.35); }
    .pill-source.community { background: rgba(255,180,84,0.14); color: var(--warn); border-color: rgba(255,180,84,0.35); }
    .pill-priority { font-family: 'JetBrains Mono', monospace; }
    .pill-priority.p-critical { background: rgba(255,93,122,0.18); color: var(--danger); border: 1px solid rgba(255,93,122,0.4); }
    .pill-priority.p-high { background: rgba(255,180,84,0.18); color: var(--warn); border: 1px solid rgba(255,180,84,0.4); }
    .pill-priority.p-low { background: rgba(255,255,255,0.08); color: var(--muted); border: 1px solid var(--border); }

    .muted { color: var(--muted); }
    .caret { display: inline-block; color: var(--accent); transition: transform 0.18s ease; }
    tr.row.open .caret { transform: rotate(90deg); }

    tr.details td { padding: 0; border-bottom: 1px solid var(--border); }
    .details-inner {
      max-height: 0; overflow: hidden; opacity: 0;
      transition: max-height 0.25s ease, opacity 0.2s ease, padding 0.25s ease;
      padding: 0 1.4rem;
    }
    tr.details.open .details-inner { max-height: 600px; opacity: 1; padding: 1rem 1.4rem 1.3rem 2.2rem; }
    .detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.6rem 1.5rem; margin-bottom: 0.9rem; }
    .detail-grid div span.label { display: block; color: var(--muted); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.2rem; }
    .detail-summary {
      color: #dbe4f2; line-height: 1.55; white-space: pre-wrap;
      background: rgba(255,255,255,0.03); border: 1px solid var(--border);
      border-radius: 10px; padding: 0.8rem 1rem; margin: 0.3rem 0 1rem;
    }
    .section-label { color: var(--accent); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; margin-bottom: 0.3rem; }
    .open-link { display: inline-flex; align-items: center; gap: 0.35rem; font-weight: 600; }

    .empty-state { text-align: center; padding: 3rem 1rem; color: var(--muted); }
    footer.note { text-align: center; color: var(--muted); font-size: 0.8rem; margin-top: 1.5rem; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div class="hero-title">
        <div class="logo">🛰️</div>
        <div>
          <h1>Sentinel Dashboard</h1>
          <p>Real-time OSINT monitoring across news, community and scanner feeds.</p>
        </div>
      </div>
      <div class="live-badge"><span class="live-dot"></span> LIVE MONITORING</div>
    </div>

    <div class="stats">
      <div class="stat-card">
        <div class="label">Total Articles</div>
        <div class="value accent">{{ stats.total }}</div>
      </div>
      <div class="stat-card">
        <div class="label">High Priority</div>
        <div class="value danger">{{ stats.high_priority }}</div>
      </div>
      <div class="stat-card">
        <div class="label">Sources Tracked</div>
        <div class="value">{{ stats.sources }}</div>
      </div>
      <div class="stat-card">
        <div class="label">Last Collected</div>
        <div class="value warn" style="font-size:1.05rem;">{{ stats.latest or 'n/a' }}</div>
      </div>
    </div>

  <div class=\"card\">
    <div class="card-head">
      <h2>Articles</h2>
      <div class="search-box">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input id="searchInput" type="text" placeholder="Filter by title or source..." oninput="filterRows()">
      </div>
    </div>
    <div class="table-scroll">
    <table>
      <thead><tr><th></th><th>Title</th><th>Source</th><th>Type</th><th>Score</th><th>Priority</th><th>Collected</th><th>Status</th></tr></thead>
      <tbody id="articleBody">
      {% for article in articles %}
      <tr class="row" data-search="{{ (article.title or '') ~ ' ' ~ (article.source or '') }}" onclick="toggleDetails({{ loop.index }})">
        <td><span class="caret">&#9656;</span></td>
        <td>{{ article.title }}</td>
        <td><span class="pill pill-source {{ article.source_type or '' }}">{{ article.source or 'n/a' }}</span></td>
        <td>{{ article.source_type or 'n/a' }}</td>
        <td>{{ article.score }}</td>
        <td>
          <span class="pill pill-priority {{ 'p-critical' if article.priority >= 6 else ('p-high' if article.priority >= 4 else 'p-low') }}">{{ article.priority }}</span>
        </td>
        <td class="muted">{{ article.collected_at or 'n/a' }}</td>
        <td><span class=\"pill pill-status\">{{ article.status }}</span></td>
      </tr>
      <tr class="details" id="details-{{ loop.index }}">
        <td colspan="8">
          <div class="details-inner">
            <div class="detail-grid">
              <div><span class="label">Source</span>{{ article.source or 'n/a' }}</div>
              <div><span class="label">Type</span>{{ article.source_type or 'n/a' }}</div>
              <div><span class="label">Score</span>{{ article.score }}</div>
              <div><span class="label">Priority</span>{{ article.priority }}</div>
              <div><span class="label">Collected</span>{{ article.collected_at or 'n/a' }}</div>
              <div><span class="label">Status</span>{{ article.status }}</div>
            </div>
            <div class="section-label">Summary</div>
            <p class="detail-summary">{{ article.summary or 'No summary available.' }}</p>
            <div class="section-label">Transcript Summary</div>
            <p class="detail-summary">{{ article.ai_summary or 'No transcript summary available.' }}</p>
            <a class="open-link" href=\"{{ article.link }}\" target=\"_blank\" rel=\"noreferrer\" onclick=\"event.stopPropagation()\">Open original source &#8594;</a>
          </div>
        </td>
      </tr>
      {% else %}
      <tr><td colspan="8" class="empty-state">No articles found yet. The scanner will populate this once a scan completes.</td></tr>
      {% endfor %}
      </tbody>
    </table>
    </div>
  </div>

  <footer class="note">Sentinel OSINT Monitor &middot; auto-refreshing local view</footer>
  </div>
</body>
<script>
  function toggleDetails(index) {
    var detailsRow = document.getElementById('details-' + index);
    var row = detailsRow.previousElementSibling;
    var isOpen = detailsRow.classList.toggle('open');
    row.classList.toggle('open', isOpen);
  }

  function filterRows() {
    var query = document.getElementById('searchInput').value.toLowerCase();
    var rows = document.querySelectorAll('#articleBody tr.row');
    rows.forEach(function (row) {
      var haystack = (row.getAttribute('data-search') || '').toLowerCase();
      var match = haystack.indexOf(query) !== -1;
      row.style.display = match ? '' : 'none';
      var details = row.nextElementSibling;
      if (details && details.classList.contains('details')) {
        details.style.display = match ? '' : 'none';
      }
    });
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
                    "SELECT title, link, source, source_type, score, priority, date, status, summary, ai_summary FROM articles ORDER BY id DESC LIMIT 50"
                )
            ).fetchall()
            article_rows = [
                {
                    "title": row[0],
                    "link": row[1],
                    "source": row[2],
                    "source_type": row[3],
                    "score": row[4] or 0,
                    "priority": row[5] or 0,
                    "collected_at": row[6],
                    "status": row[7],
                    "summary": row[8],
                    "ai_summary": row[9],
                }
                for row in articles
            ]
        finally:
            session.close()

        stats = {
            "total": len(article_rows),
            "high_priority": sum(1 for a in article_rows if a["priority"] >= 6),
            "sources": len({a["source"] for a in article_rows if a["source"]}),
            "latest": article_rows[0]["collected_at"] if article_rows else None,
        }

        return render_template_string(
            HTML_TEMPLATE,
            articles=article_rows,
            stats=stats,
        )

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
