import os
from typing import Optional

import praw

from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_PASSWORD,
    REDDIT_USER_AGENT,
    REDDIT_USERNAME,
)


def validate_reddit_config(allow_missing: bool = False, env: Optional[dict] = None) -> None:
    data = env or {
        "REDDIT_CLIENT_ID": REDDIT_CLIENT_ID,
        "REDDIT_CLIENT_SECRET": REDDIT_CLIENT_SECRET,
        "REDDIT_USERNAME": REDDIT_USERNAME,
        "REDDIT_PASSWORD": REDDIT_PASSWORD,
        "REDDIT_USER_AGENT": REDDIT_USER_AGENT,
        "REDDIT_REFRESH_TOKEN": os.getenv("REDDIT_REFRESH_TOKEN"),
    }

    required = {
        "REDDIT_CLIENT_ID": data.get("REDDIT_CLIENT_ID"),
        "REDDIT_CLIENT_SECRET": data.get("REDDIT_CLIENT_SECRET"),
        "REDDIT_USER_AGENT": data.get("REDDIT_USER_AGENT"),
    }

    if data.get("REDDIT_REFRESH_TOKEN"):
        missing = [
            name
            for name, value in required.items()
            if not value
        ]
    else:
        missing = [
            name
            for name, value in {
                **required,
                "REDDIT_USERNAME": data.get("REDDIT_USERNAME"),
                "REDDIT_PASSWORD": data.get("REDDIT_PASSWORD"),
            }.items()
            if not value
        ]

    if missing and not allow_missing:
        raise RuntimeError(
            "Missing Reddit configuration: "
            + ", ".join(missing)
        )


def build_reddit_kwargs(env: Optional[dict] = None) -> dict:
    data = env or {
        "REDDIT_CLIENT_ID": REDDIT_CLIENT_ID,
        "REDDIT_CLIENT_SECRET": REDDIT_CLIENT_SECRET,
        "REDDIT_PASSWORD": REDDIT_PASSWORD,
        "REDDIT_USERNAME": REDDIT_USERNAME,
        "REDDIT_USER_AGENT": REDDIT_USER_AGENT,
        "REDDIT_REFRESH_TOKEN": os.getenv("REDDIT_REFRESH_TOKEN"),
    }

    kwargs = {
        "client_id": data.get("REDDIT_CLIENT_ID"),
        "client_secret": data.get("REDDIT_CLIENT_SECRET"),
        "user_agent": data.get("REDDIT_USER_AGENT"),
        "check_for_async": False,
    }

    if data.get("REDDIT_REFRESH_TOKEN"):
        kwargs["refresh_token"] = data.get("REDDIT_REFRESH_TOKEN")
    else:
        kwargs.update(
            {
                "username": data.get("REDDIT_USERNAME"),
                "password": data.get("REDDIT_PASSWORD"),
            }
        )

    return kwargs


def get_reddit_client() -> praw.Reddit:
    validate_reddit_config(allow_missing=False)
    kwargs = build_reddit_kwargs()
    return praw.Reddit(**kwargs)
