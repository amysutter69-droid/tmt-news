"""Scraper for DigiTimes.com - Asia tech industry news."""

from datetime import datetime
from dateutil import parser as date_parser

from .base import BaseScraper, NewsStory


class DigitimesScraper(BaseScraper):
    """Scraper for DigiTimes tech news."""

    def __init__(self):
        super().__init__("digitimes")

    def scrape(self) -> list[NewsStory]:
        """Scrape news from DigiTimes."""
        soup = self.fetch_page()
        if not soup:
            return []

        stories = []
        seen_urls = set()

        # DigiTimes has various article layouts
        # Try multiple selector patterns

        # Pattern 1: Article cards/items
        articles = soup.select("article, div.article-item, div.news-item, div.story")

        if not articles:
            # Pattern 2: List-based layout
            articles = soup.select("div.list-item, li.news-entry, div.col-news")

        if not articles:
            # Pattern 3: Generic content blocks
            articles = soup.select("div[class*='news'], div[class*='article'], div[class*='story']")

        for article in articles:
            # Find headline and link
            headline = article.select_one("h2 a, h3 a, a.title, a[href*='/news/'], a[href*='/tech/']")

            if not headline:
                headline = article.select_one("a")

            if not headline:
                continue

            url = headline.get("href", "")
            title = headline.get_text(strip=True)

            if not url or not title or len(title) < 10 or url in seen_urls:
                continue

            # Ensure full URL
            if url.startswith("/"):
                url = f"https://www.digitimes.com{url}"

            seen_urls.add(url)

            # Get summary
            summary = ""
            summary_elem = article.select_one("p.summary, p.excerpt, div.desc, p:not(.date)")
            if summary_elem:
                summary = summary_elem.get_text(strip=True)

            # Get date
            published_date = None
            date_elem = article.select_one("time, span.date, div.date, span.time")
            if date_elem:
                date_str = date_elem.get("datetime") or date_elem.get_text(strip=True)
                try:
                    published_date = date_parser.parse(date_str)
                except (ValueError, TypeError):
                    pass

            stories.append(NewsStory(
                title=title,
                url=url,
                source=self.name,
                summary=summary,
                published_date=published_date
            ))

        # Fallback if no articles found
        if not stories:
            stories = self._fallback_scrape(soup, seen_urls)

        return stories

    def _fallback_scrape(self, soup, seen_urls: set) -> list[NewsStory]:
        """Fallback scraping using generic link patterns."""
        stories = []

        # Look for links that match DigiTimes article patterns
        for link in soup.select("a[href*='/news/'], a[href*='/tech/'], a[href*='/story/']"):
            url = link.get("href", "")
            title = link.get_text(strip=True)

            if not url or not title or len(title) < 15 or url in seen_urls:
                continue

            # Skip navigation links
            if any(x in url.lower() for x in ["/tag/", "/category/", "/author/", "/search"]):
                continue

            if url.startswith("/"):
                url = f"https://www.digitimes.com{url}"

            seen_urls.add(url)

            stories.append(NewsStory(
                title=title,
                url=url,
                source=self.name
            ))

        return stories
