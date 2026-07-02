"""X.com (Twitter) scraper using the official X API v2.

Pulls two sets of posts:
  1. Everything recent from a curated list of semiconductor accounts
  2. A keyword search for semiconductor/hardware terms, filtered by a
     minimum like count to cut noise

Requires an X API bearer token with search access (Basic tier or above)
in the X_BEARER_TOKEN environment variable. Without a token this source
is skipped with a clear message and the rest of the digest still runs.
X.com blocks unauthenticated scraping, so the API is the only reliable path.
"""

import requests
from dateutil import parser as date_parser

import config
from .base import BaseScraper, NewsStory

SEARCH_URL = "https://api.x.com/2/tweets/search/recent"


class XScraper(BaseScraper):
    """Scraper for X posts via the v2 recent search API."""

    def __init__(self):
        super().__init__("x")
        self.token = config.get_x_bearer_token()

    def scrape(self) -> list[NewsStory]:
        if not self.token:
            print(
                f"  Skipping X: set the {config.X_BEARER_TOKEN_ENV} environment "
                "variable with an X API v2 bearer token to enable this source."
            )
            return []

        stories = []
        seen_ids = set()

        # 1. Curated accounts - keep everything they post
        if config.X_ACCOUNTS:
            from_clause = " OR ".join(f"from:{h}" for h in config.X_ACCOUNTS)
            account_query = f"({from_clause}) -is:retweet"
            for story in self._search(account_query):
                if story.url not in seen_ids:
                    seen_ids.add(story.url)
                    stories.append(story)

        # 2. Keyword search - require engagement to cut noise
        for story in self._search(config.X_KEYWORD_QUERY, min_likes=config.X_MIN_LIKES):
            if story.url not in seen_ids:
                seen_ids.add(story.url)
                stories.append(story)

        return stories

    def _search(self, query: str, min_likes: int = 0) -> list[NewsStory]:
        """Run one recent-search request and map results to NewsStory."""
        params = {
            "query": query,
            "max_results": config.X_MAX_RESULTS,
            "tweet.fields": "created_at,public_metrics,author_id",
            "expansions": "author_id",
            "user.fields": "username,name",
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(
                SEARCH_URL, params=params, headers=headers,
                timeout=config.REQUEST_TIMEOUT,
            )
        except requests.RequestException as e:
            print(f"  Error reaching X API: {e}")
            return []

        if response.status_code == 401:
            print("  X API error 401: bearer token is invalid or expired.")
            return []
        if response.status_code == 403:
            print(
                "  X API error 403: this token's access tier does not include "
                "search. The recent-search endpoint requires Basic tier or above."
            )
            return []
        if response.status_code == 429:
            print("  X API error 429: rate limited, skipping this query.")
            return []
        if response.status_code != 200:
            print(f"  X API error {response.status_code}: {response.text[:200]}")
            return []

        data = response.json()
        tweets = data.get("data", [])
        users = {
            u["id"]: u
            for u in data.get("includes", {}).get("users", [])
        }

        stories = []
        for tweet in tweets:
            metrics = tweet.get("public_metrics", {})
            likes = metrics.get("like_count", 0)
            if likes < min_likes:
                continue

            user = users.get(tweet.get("author_id"), {})
            username = user.get("username", "unknown")
            display_name = user.get("name", username)

            text = tweet.get("text", "").replace("\n", " ").strip()
            title = text if len(text) <= 120 else text[:117] + "..."

            retweets = metrics.get("retweet_count", 0)
            summary = f"{text} [{likes} likes, {retweets} reposts]"

            published_date = None
            if tweet.get("created_at"):
                try:
                    published_date = date_parser.parse(tweet["created_at"])
                except (ValueError, TypeError):
                    pass

            stories.append(NewsStory(
                title=title,
                url=f"https://x.com/{username}/status/{tweet['id']}",
                source=self.name,
                summary=summary,
                published_date=published_date,
                author=f"@{username} ({display_name})",
            ))

        return stories
