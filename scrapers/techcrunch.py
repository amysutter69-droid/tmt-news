"""Scraper for TechCrunch.com - startup and technology news."""

from datetime import datetime
from dateutil import parser as date_parser

from .base import BaseScraper, NewsStory


class TechcrunchScraper(BaseScraper):
    """Scraper for TechCrunch news."""

    def __init__(self):
        super().__init__("techcrunch")

    def scrape(self) -> list[NewsStory]:
        """Scrape news from TechCrunch."""
        soup = self.fetch_page()
        if not soup:
            return []

        stories = []
        seen_urls = set()

        # TechCrunch uses article elements with various data attributes
        # Try multiple selector patterns

        # Pattern 1: Article elements (most common)
        articles = soup.select("article[data-post-id], article.post-block")

        if not articles:
            # Pattern 2: Div-based article containers
            articles = soup.select("div.post-block, div.article-card, div.river-item")

        if not articles:
            # Pattern 3: List-based layout
            articles = soup.select("li.river__item, div.content-card")

        for article in articles:
            # Find headline and link
            headline = article.select_one("h2 a, h3 a, a.post-block__title, a[data-omni-click='article_link']")

            if not headline:
                headline = article.select_one("a.article-link, a[href*='/20']")

            if not headline:
                continue

            url = headline.get("href", "")
            title = headline.get_text(strip=True)

            if not url or not title or url in seen_urls:
                continue

            seen_urls.add(url)

            # Ensure full URL
            if url.startswith("/"):
                url = f"https://techcrunch.com{url}"

            # Get summary/excerpt
            summary = ""
            summary_elem = article.select_one("p.excerpt, div.post-block__content, p.article-excerpt")
            if summary_elem:
                summary = summary_elem.get_text(strip=True)

            # Get author
            author = ""
            author_elem = article.select_one("span.river-byline__authors a, a[rel='author'], span.byline a")
            if author_elem:
                author = author_elem.get_text(strip=True)

            # Get date
            published_date = None
            time_elem = article.select_one("time, span.river-byline__time")
            if time_elem:
                date_str = time_elem.get("datetime") or time_elem.get_text(strip=True)
                try:
                    published_date = date_parser.parse(date_str)
                except (ValueError, TypeError):
                    pass

            stories.append(NewsStory(
                title=title,
                url=url,
                source=self.name,
                summary=summary,
                author=author,
                published_date=published_date
            ))

        # Fallback if no articles found
        if not stories:
            stories = self._fallback_scrape(soup, seen_urls)

        return stories

    def _fallback_scrape(self, soup, seen_urls: set) -> list[NewsStory]:
        """Fallback scraping using generic link patterns."""
        stories = []

        # Look for links that match TechCrunch article URL patterns
        # TechCrunch URLs typically: /YYYY/MM/DD/article-slug/
        for link in soup.select("a[href*='/202']"):
            url = link.get("href", "")
            title = link.get_text(strip=True)

            # Filter out navigation and short titles
            if not url or not title or len(title) < 15 or url in seen_urls:
                continue

            # Skip if it's clearly not an article (images, categories, etc.)
            if any(x in url for x in ["/tag/", "/category/", "/author/", ".jpg", ".png"]):
                continue

            if url.startswith("/"):
                url = f"https://techcrunch.com{url}"

            seen_urls.add(url)

            stories.append(NewsStory(
                title=title,
                url=url,
                source=self.name
            ))

        return stories
