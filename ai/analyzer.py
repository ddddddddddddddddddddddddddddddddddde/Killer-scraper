import json
import os
import re

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised when dependency is absent
    OpenAI = None

client = None
if OpenAI is not None and os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = """
Extract structured information from this news article.

Return ONLY valid JSON.

Fields:
incident_type
location
people
agency
summary
confidence

Article:
"""


def _fallback_analysis(article_text: str) -> dict:
    text = article_text.lower()
    location = None
    city = None
    state = None

    city_state_match = re.search(r"\b(?:in|from|near)\s+([A-Z][a-z]+),\s*([A-Z][a-z]+)", article_text)
    if city_state_match:
        city = city_state_match.group(1)
        state = city_state_match.group(2)
    else:
        city_match = re.search(r"\b(?:in|from|near)\s+([A-Z][a-z]+)", article_text)
        if city_match:
            city = city_match.group(1)

    if city or state:
        location = {"city": city or "unknown", "state": state or "unknown", "country": "unknown"}

    if "missing person" in text or "missing" in text:
        incident_type = "Missing Person"
    elif "homicide" in text:
        incident_type = "Homicide"
    elif "unidentified" in text or "body found" in text:
        incident_type = "Unidentified Remains"
    elif "suspicious death" in text:
        incident_type = "Suspicious Death"
    else:
        incident_type = "Unknown"

    agency = "Police" if "police" in text else None

    return {
        "incident_type": incident_type,
        "location": location,
        "people": [],
        "agency": agency,
        "summary": article_text[:400],
        "confidence": 0.35,
    }


def analyze(article_text: str) -> dict:
    if not os.getenv("OPENAI_API_KEY") or client is None:
        return _fallback_analysis(article_text)

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured information from news articles."
                },
                {
                    "role": "user",
                    "content": PROMPT + article_text
                }
            ]
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
    except Exception:
        return _fallback_analysis(article_text)
