"""Scraper for Techmeme.com - tech news aggregator."""

from .base import BaseScraper, NewsStory


class TechmemeScraper(BaseScraper):
    """Scraper for Techmeme headlines."""

    def __init__(self):
        super().__init__("techmeme")

    def scrape(self) -> list[NewsStory]:
        """Scrape top stories from Techmeme."""
        soup = self.fetch_page()
        if not soup:
            return []

        stories = []

        # Techmeme uses divs with class 'clus' for story clusters
        # Each cluster has a main headline in an element with class 'ii'
        # Try multiple selector patterns for robustness

        # Pattern 1: Look for main story items
        story_items = soup.select("div.clus div.ii a")

        if not story_items:
            # Pattern 2: Alternative - look for headline links directly
            story_items = soup.select("a.ourh")

        if not story_items:
            # Pattern 3: Look for any strong tags with links (older structure)
            story_items = soup.select("div#topcol1 strong a")

        seen_urls = set()
        for item in story_items:
            url = item.get("href", "")
            title = item.get_text(strip=True)

            # Skip empty or duplicate entries
            if not url or not title or url in seen_urls:
                continue

            # Ensure full URL
            if url.startswith("/"):
                url = f"https://www.techmeme.com{url}"

            seen_urls.add(url)

            # Try to get summary from sibling or parent elements
            summary = ""
            parent = item.find_parent("div", class_="clus")
            if parent:
                summary_elem = parent.select_one("div.sd")
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)

            stories.append(NewsStory(
                title=title,
                url=url,
                source=self.name,
                summary=summary
            ))

        return stories
