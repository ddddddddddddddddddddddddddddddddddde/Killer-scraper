import os
import webbrowser
from urllib.parse import urlencode

from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT


AUTH_URL = "https://www.reddit.com/api/v1/authorize.compact"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"


def build_auth_url(redirect_uri: str = "http://localhost:8080") -> str:
    params = {
        "client_id": REDDIT_CLIENT_ID or "",
        "response_type": "code",
        "state": "sentinel_osint",
        "redirect_uri": redirect_uri,
        "duration": "permanent",
        "scope": "submit read identity",
    }
    return AUTH_URL + "?" + urlencode(params)


def open_auth_flow(redirect_uri: str = "http://localhost:8080") -> str:
    url = build_auth_url(redirect_uri=redirect_uri)
    webbrowser.open(url)
    return url
