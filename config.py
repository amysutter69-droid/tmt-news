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
