from config import REDDIT_SUBREDDIT
from reddit.client import get_reddit_client


def main() -> None:
    reddit = get_reddit_client()

    user = reddit.user.me()

    subreddit = reddit.subreddit(REDDIT_SUBREDDIT)

    print(f"Authenticated as: u/{user}")
    print(f"Target subreddit: r/{subreddit.display_name}")
    print(f"Subreddit title: {subreddit.title}")
    print("Reddit authentication successful.")


if __name__ == "__main__":
    main()
