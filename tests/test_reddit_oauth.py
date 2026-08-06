import unittest

from reddit.client import build_reddit_kwargs, validate_reddit_config


class RedditOAuthTests(unittest.TestCase):
    def test_refresh_token_path_is_selected_when_present(self) -> None:
        env = {
            "REDDIT_CLIENT_ID": "client",
            "REDDIT_CLIENT_SECRET": "secret",
            "REDDIT_USER_AGENT": "test-agent",
            "REDDIT_REFRESH_TOKEN": "refresh-token",
        }

        validate_reddit_config(allow_missing=True, env=env)
        kwargs = build_reddit_kwargs(env=env)

        self.assertEqual(kwargs["refresh_token"], "refresh-token")
        self.assertNotIn("password", kwargs)


if __name__ == "__main__":
    unittest.main()
