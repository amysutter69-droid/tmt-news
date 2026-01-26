"""Base scraper class with common functionality."""

import requests
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup

import config


class NewsStory:
    """Represents a single news story."""

    def __init__(
        self,
        title: str,
        url: str,
        source: str,
        summary: str = "",
        published_date: Optional[datetime] = None,
        author: str = ""
    ):
        self.title = title
        self.url = url
        self.source = source
        self.summary = summary
        self.published_date = published_date
        self.author = author
        self.scraped_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert story to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "summary": self.summary,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "author": self.author,
            "scraped_at": self.scraped_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"NewsStory(title='{self.title[:50]}...', source='{self.source}')"


class BaseScraper(ABC):
    """Base class for all news scrapers."""

    def __init__(self, source_key: str):
        self.source_key = source_key
        self.source_config = config.NEWS_SOURCES[source_key]
        self.url = self.source_config["url"]
        self.name = self.source_config["name"]
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def fetch_page(self, url: Optional[str] = None) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage."""
        target_url = url or self.url
        try:
            response = self.session.get(target_url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            print(f"Error fetching {target_url}: {e}")
            return None

    @abstractmethod
    def scrape(self) -> list[NewsStory]:
        """Scrape news stories from the source. Must be implemented by subclasses."""
        pass

    def get_stories(self, max_stories: Optional[int] = None) -> list[NewsStory]:
        """Get stories with optional limit."""
        stories = self.scrape()
        limit = max_stories or config.MAX_STORIES_PER_SOURCE
        return stories[:limit]
