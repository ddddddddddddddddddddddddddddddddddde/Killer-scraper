# Sentinel OSINT Dashboard

This project includes a lightweight Flask dashboard for viewing collected articles and Reddit post previews.

## Run locally

```bash
python web_dashboard.py
```

## Deploy to a hosting service

This app is ready for a standard Python hosting service that supports Gunicorn.

- Add the files in this folder to the host
- Install dependencies from requirements.txt
- Start with:

```bash
gunicorn web_dashboard:app
```

## Environment variables

- PORT: optional, defaults to 5000
- SENTINEL_DB_PATH: optional, defaults to the local SQLite database in data/sentinel.db

## Automated scanning (GitHub Actions)

`.github/workflows/scan.yml` runs `main.py`'s scan on a schedule (every 15 minutes) directly on
GitHub's infrastructure, so scanning keeps happening even when your computer is off. Each run
commits the updated `data/sentinel.db` back to the repo.

Notes:
- GitHub disables scheduled workflows automatically after 60 days with no repo activity; push a
  commit or click "Run workflow" on the Actions tab to re-enable it.
- Cron schedules are minimum-effort, not exact — GitHub may delay runs during high load.
- To view results, `git pull` and run `python web_dashboard.py` locally, or deploy the dashboard
  (see "Deploy to a hosting service" above) pointed at the same repo.
- If you set an `OPENAI_API_KEY` repo secret, add it under Settings → Secrets and variables →
  Actions so the workflow can use it for AI-generated summaries.
# Killer-scraper
