from __future__ import annotations

from typing import Any

import requests

from config import OPEN_DATA_FEED_LIMIT, OPEN_DATA_SCANNER_FEEDS


class OpenDataScanner:
    """Pulls near-real-time 911/CAD incident records from free, public Socrata
    open-data portals (city/county governments). Unlike OpenMHz or Broadcastify,
    these have no bot-wall and no login/key requirement.
    """

    def __init__(self, session: requests.Session | None = None) -> None:
        self.session = session or requests.Session()

    def _fetch_feed(self, feed: dict[str, Any]) -> list[dict[str, Any]]:
        url = f"https://{feed['domain']}/resource/{feed['resource_id']}.json"
        params = {
            "$limit": OPEN_DATA_FEED_LIMIT,
            "$order": f"{feed['time_field']} DESC",
        }

        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            records = response.json()
        except Exception:
            return []

        articles: list[dict[str, Any]] = []
        for record in records:
            record_id = record.get(feed["id_field"], "")
            if not record_id:
                continue

            call_type = record.get(feed["title_field"], "Incident")
            location = record.get(feed["location_field"], "")
            extra = record.get(feed.get("extra_field", ""), "")

            summary_parts = [part for part in (location, extra) if part]

            articles.append(
                {
                    "title": f"{feed['label']}: {call_type}",
                    "link": f"https://{feed['domain']}/d/{feed['resource_id']}#{record_id}",
                    "source": feed["label"],
                    "date": record.get(feed["time_field"], ""),
                    "summary": " - ".join(summary_parts) if summary_parts else call_type,
                    "source_type": "police_scanner",
                }
            )

        return articles

    def collect_articles(self) -> list[dict[str, Any]]:
        collected: list[dict[str, Any]] = []
        for feed in OPEN_DATA_SCANNER_FEEDS:
            collected.extend(self._fetch_feed(feed))
        return collected
