"""Configuration for the TMT News Scraper."""

# News sources to scrape
NEWS_SOURCES = {
    "techmeme": {
        "url": "https://www.techmeme.com/",
        "name": "Techmeme",
        "description": "Tech news aggregator"
    },
    "trendforce": {
        "url": "https://www.trendforce.com/news",
        "name": "TrendForce",
        "description": "Tech industry research and news"
    },
    "techcrunch": {
        "url": "https://techcrunch.com/",
        "name": "TechCrunch",
        "description": "Startup and technology news"
    },
    "digitimes": {
        "url": "https://www.digitimes.com/tech/",
        "name": "DigiTimes",
        "description": "Asia tech industry news"
    }
}

# Request settings
REQUEST_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Output settings
OUTPUT_DIR = "output"
MAX_STORIES_PER_SOURCE = 10

# Schedule settings (24-hour format)
DAILY_RUN_TIME = "07:00"

# ── Podcast RSS feeds ─────────────────────────────────────────────────────────
# Add or remove podcasts here. The digest looks back PODCAST_LOOKBACK_DAYS days.
# To find an RSS URL: open the podcast in a browser, or search "<name> RSS feed".
PODCASTS = [
    {
        "name": "All-In Podcast",
        "rss_url": "https://feeds.megaphone.fm/all-in-with-chamath-jason-sacks-friedberg",
    },
    {
        "name": "Invest Like the Best",
        "rss_url": "https://feeds.megaphone.fm/investlikethebest",
    },
    {
        "name": "Dwarkesh Podcast",
        # Dwarkesh Patel's long-form interview podcast
        "rss_url": "https://www.dwarkeshpatel.com/feed",
    },
    {
        "name": "Cheeky Pint",
        # Verify this RSS URL is correct for your version of the show
        "rss_url": "https://feeds.buzzsprout.com/1985510.rss",
    },
]

PODCAST_LOOKBACK_DAYS = 7
