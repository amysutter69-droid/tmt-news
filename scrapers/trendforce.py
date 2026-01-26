"""Scraper for TrendForce.com - tech industry research and news."""

from datetime import datetime
from dateutil import parser as date_parser

from .base import BaseScraper, NewsStory


class TrendforceScraper(BaseScraper):
    """Scraper for TrendForce news."""

    def __init__(self):
        super().__init__("trendforce")

    def scrape(self) -> list[NewsStory]:
        """Scrape news from TrendForce."""
        soup = self.fetch_page()
        if not soup:
            return []

        stories = []

        # TrendForce news page typically has article cards/items
        # Try multiple selector patterns

        # Pattern 1: News article items
        news_items = soup.select("article.news-item, div.news-item, div.press-item")

        if not news_items:
            # Pattern 2: Generic article elements
            news_items = soup.select("article, div.article-item, div.news-card")

        if not news_items:
            # Pattern 3: Look for list items with links
            news_items = soup.select("ul.news-list li, div.news-list div.item")

        for item in news_items:
            # Find the headline link
            link = item.select_one("a[href*='/news'], a.title, h2 a, h3 a, a.headline")
            if not link:
                link = item.select_one("a")

            if not link:
                continue

            url = link.get("href", "")
            title = link.get_text(strip=True)

            if not url or not title:
                continue

            # Ensure full URL
            if url.startswith("/"):
                url = f"https://www.trendforce.com{url}"

            # Try to get summary
            summary = ""
            summary_elem = item.select_one("p.summary, p.excerpt, div.description, p.desc")
            if summary_elem:
                summary = summary_elem.get_text(strip=True)

            # Try to get date
            published_date = None
            date_elem = item.select_one("time, span.date, div.date, span.time")
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

        # If no items found with patterns above, try a more generic approach
        if not stories:
            stories = self._fallback_scrape(soup)

        return stories

    def _fallback_scrape(self, soup) -> list[NewsStory]:
        """Fallback scraping method using generic patterns."""
        stories = []
        seen_urls = set()

        # Look for any links that look like news articles
        for link in soup.select("a[href*='/news/'], a[href*='/press/'], a[href*='article']"):
            url = link.get("href", "")
            title = link.get_text(strip=True)

            # Skip navigation, empty, or very short titles
            if not url or not title or len(title) < 20 or url in seen_urls:
                continue

            if url.startswith("/"):
                url = f"https://www.trendforce.com{url}"

            seen_urls.add(url)

            stories.append(NewsStory(
                title=title,
                url=url,
                source=self.name
            ))

        return stories
