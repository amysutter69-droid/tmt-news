"""Podcast RSS feed fetcher — returns episodes published in the last N days."""

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional
import feedparser
import requests


@dataclass
class Episode:
    podcast: str
    title: str
    url: str
    published: datetime
    duration: Optional[str]
    description: str

    def to_dict(self) -> dict:
        return {
            "podcast": self.podcast,
            "title": self.title,
            "url": self.url,
            "published": self.published.isoformat(),
            "duration": self.duration,
            "description": self.description[:1000],
        }


def _parse_date(entry) -> Optional[datetime]:
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        import time
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return None


def fetch_episodes(feed_url: str, podcast_name: str, days: int = 7) -> list[Episode]:
    """Fetch episodes published within the last `days` days from an RSS feed."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        print(f"  [podcast_rss] Failed to parse {feed_url}: {e}")
        return []

    episodes = []
    for entry in feed.entries:
        pub = _parse_date(entry)
        if pub is None or pub < cutoff:
            continue

        # Prefer enclosure URL (audio), fall back to entry link
        url = entry.get("link", "")
        for enc in getattr(entry, "enclosures", []):
            if "audio" in enc.get("type", ""):
                url = enc.get("href", url)
                break

        duration = None
        for tag in ("itunes_duration", "duration"):
            if hasattr(entry, tag):
                duration = getattr(entry, tag)
                break

        description = (
            entry.get("summary")
            or entry.get("description")
            or entry.get("content", [{}])[0].get("value", "")
            or ""
        )
        # Strip basic HTML tags
        import re
        description = re.sub(r"<[^>]+>", " ", description).strip()

        episodes.append(Episode(
            podcast=podcast_name,
            title=entry.get("title", "Untitled"),
            url=url,
            published=pub,
            duration=duration,
            description=description,
        ))

    return episodes


def fetch_all_podcasts(podcasts: list[dict], days: int = 7) -> list[Episode]:
    """Fetch episodes from all configured podcasts, sorted newest-first."""
    all_episodes: list[Episode] = []
    for pod in podcasts:
        name = pod["name"]
        url = pod["rss_url"]
        print(f"  Fetching {name}...")
        eps = fetch_episodes(url, name, days)
        print(f"    {len(eps)} episode(s) in the last {days} days")
        all_episodes.extend(eps)

    all_episodes.sort(key=lambda e: e.published, reverse=True)
    return all_episodes
