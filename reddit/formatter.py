import html
import re
from typing import Tuple

from database.models import Article

MAX_TITLE_LENGTH = 300


def clean_html(value: str | None) -> str:
    if not value:
        return ""

    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate(value: str, maximum: int) -> str:
    if len(value) <= maximum:
        return value

    return value[: maximum - 1].rstrip() + "…"


def format_reddit_post(article: Article) -> Tuple[str, str]:
    article_title = clean_html(article.title)

    title = truncate(
        f"[Unconfirmed Report] {article_title}",
        MAX_TITLE_LENGTH,
    )

    summary = clean_html(article.summary)

    if not summary:
        summary = (
            "No summary was included in the source feed. "
            "Open the original report for details."
        )

    summary = truncate(summary, 1800)

    source = clean_html(article.source) or "Unknown source"
    published = clean_html(article.date) or "Not provided"

    body = f"""## Public-source incident report

**Headline:** {article_title}

**Source:** {source}

**Published:** {published}

**Sentinel relevance score:** {article.score}

### Source summary

{summary}

### Original report

{article.link}

---

*This post was generated automatically from a publicly available news feed. Details may change as authorities and journalists update their reporting. The linked source—not this automated summary—is the authoritative reference. Do not contact, accuse, or harass people mentioned in a report.*
"""

    return title, body
