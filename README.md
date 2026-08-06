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
