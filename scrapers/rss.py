"""Generic RSS/Atom feed scraper.

One class covers every source in config.RSS_SOURCES. Feeds are far more
stable than HTML scraping, so this is the preferred way to add sources.
"""

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

import config
from .base import BaseScraper, NewsStory


class RSSScraper(BaseScraper):
    """Scraper for a single RSS/Atom feed from config.RSS_SOURCES."""

    def __init__(self, source_key: str):
        # BaseScraper reads from NEWS_SOURCES; RSS sources live in their
        # own dict, so set up the same attributes directly.
        self.source_key = source_key
        self.source_config = config.RSS_SOURCES[source_key]
        self.url = self.source_config["url"]
        self.name = self.source_config["name"]
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        })

    def scrape(self) -> list[NewsStory]:
        """Fetch and parse the feed (handles both RSS 2.0 and Atom)."""
        try:
            response = self.session.get(self.url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching feed {self.url}: {e}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        entries = soup.find_all("item") or soup.find_all("entry")

        stories = []
        for entry in entries:
            title_tag = entry.find("title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            url = self._entry_link(entry)
            if not title or not url:
                continue

            summary = ""
            summary_tag = (
                entry.find("description")
                or entry.find("summary")
                or entry.find("content")
            )
            if summary_tag:
                # Feed summaries often embed HTML; strip it to plain text
                raw = summary_tag.get_text(" ", strip=True)
                summary = BeautifulSoup(raw, "lxml").get_text(" ", strip=True)
                if len(summary) > 300:
                    summary = summary[:297] + "..."

            published_date = None
            date_tag = (
                entry.find("pubDate")
                or entry.find("published")
                or entry.find("updated")
                or entry.find("date")
            )
            if date_tag:
                try:
                    published_date = date_parser.parse(date_tag.get_text(strip=True))
                except (ValueError, TypeError):
                    pass

            author = ""
            author_tag = entry.find("creator") or entry.find("author")
            if author_tag:
                name_tag = author_tag.find("name")
                author = (name_tag or author_tag).get_text(strip=True)

            stories.append(NewsStory(
                title=title,
                url=url,
                source=self.name,
                summary=summary,
                published_date=published_date,
                author=author,
            ))

        return stories

    @staticmethod
    def _entry_link(entry) -> str:
        """Extract the entry URL for both RSS (<link>text</link>) and
        Atom (<link href="..."/>) formats."""
        for link_tag in entry.find_all("link"):
            href = link_tag.get("href")
            if href:
                # Atom: prefer rel="alternate" or links without rel
                rel = link_tag.get("rel")
                if rel in (None, "alternate", ["alternate"]):
                    return href.strip()
            else:
                text = link_tag.get_text(strip=True)
                if text:
                    return text
        # Fall back to any href at all
        for link_tag in entry.find_all("link"):
            href = link_tag.get("href")
            if href:
                return href.strip()
        return ""
