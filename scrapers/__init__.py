"""News scrapers for TMT (Tech, Media, Telecom) sources."""

from .base import BaseScraper
from .techmeme import TechmemeScraper
from .trendforce import TrendforceScraper
from .techcrunch import TechcrunchScraper

__all__ = [
    "BaseScraper",
    "TechmemeScraper",
    "TrendforceScraper",
    "TechcrunchScraper",
]
