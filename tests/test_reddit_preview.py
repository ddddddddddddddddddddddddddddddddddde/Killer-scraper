import unittest
from unittest.mock import patch

from reddit.client import validate_reddit_config
from reddit.poster import validate_posting_settings
from config import REDDIT_POST_MODE


class RedditPreviewTests(unittest.TestCase):
    def test_dry_run_allows_missing_credentials(self) -> None:
        if REDDIT_POST_MODE != "dry_run":
            self.skipTest("dry_run mode is required for this test")

        validate_posting_settings()

        try:
            validate_reddit_config(allow_missing=True)
        except RuntimeError as exc:
            self.fail(f"Expected dry-run to tolerate missing credentials, got: {exc}")

    def test_dry_run_does_not_require_subreddit(self) -> None:
        with patch("reddit.poster.REDDIT_SUBREDDIT", ""):
            with self.assertRaisesRegex(RuntimeError, "REDDIT_SUBREDDIT"):
                validate_posting_settings()


if __name__ == "__main__":
    unittest.main()
