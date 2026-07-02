"""Configuration for the TMT News Scraper."""

import os

# News sources scraped from HTML pages
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
    },
    "x": {
        "url": "https://api.x.com/2/tweets/search/recent",
        "name": "X (Twitter)",
        "description": "Posts from semiconductor analysts and keyword search"
    },
}

# News sources scraped from RSS/Atom feeds (much more reliable than HTML).
# A feed that fails just contributes zero stories; the run continues.
RSS_SOURCES = {
    "tomshardware": {
        "url": "https://www.tomshardware.com/feeds/all",
        "name": "Tom's Hardware",
        "description": "PC, chip, and component hardware news"
    },
    "semiengineering": {
        "url": "https://semiengineering.com/feed/",
        "name": "SemiEngineering",
        "description": "Deep semiconductor industry coverage"
    },
    "eetimes": {
        "url": "https://www.eetimes.com/feed/",
        "name": "EE Times",
        "description": "Electronics industry news"
    },
    "theregister": {
        "url": "https://www.theregister.com/headlines.atom",
        "name": "The Register",
        "description": "Enterprise tech news with strong chip coverage"
    },
    "servethehome": {
        "url": "https://www.servethehome.com/feed/",
        "name": "ServeTheHome",
        "description": "Server, networking, and data center hardware"
    },
    "nextplatform": {
        "url": "https://www.nextplatform.com/feed/",
        "name": "The Next Platform",
        "description": "HPC and data center infrastructure analysis"
    },
    "semiwiki": {
        "url": "https://semiwiki.com/feed/",
        "name": "SemiWiki",
        "description": "Semiconductor industry blog network"
    },
    "arstechnica": {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "name": "Ars Technica",
        "description": "Technology news and analysis"
    },
    "cnbctech": {
        "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html",
        "name": "CNBC Tech",
        "description": "Tech business and markets news"
    },
}

# --- X.com (Twitter) settings ---
# Requires an X API v2 bearer token with search access (Basic tier or above).
# Set the token in the X_BEARER_TOKEN environment variable; if unset, the
# X source is skipped and the rest of the digest still runs.
X_BEARER_TOKEN_ENV = "X_BEARER_TOKEN"

# Curated accounts known for semiconductor/hardware news and analysis
X_ACCOUNTS = [
    "dnystedt",        # Dan Nystedt - Asia semiconductor news
    "dylan522p",       # Dylan Patel - SemiAnalysis
    "SemiAnalysis_",   # SemiAnalysis
    "IanCutress",      # Dr. Ian Cutress - TechTechPotato
    "TrendForce",      # TrendForce research
    "SKundojjala",     # Sravan Kundojjala - chip market analysis
]

# Keyword search on X (X API query syntax, max 512 chars on Basic tier)
X_KEYWORD_QUERY = (
    '(semiconductor OR TSMC OR "chip maker" OR chipmaker OR foundry OR HBM '
    'OR EUV OR "advanced packaging" OR "AI chip" OR "data center capex") '
    '-is:retweet -is:reply lang:en'
)

# Minimum likes for keyword-search results (curated accounts are exempt)
X_MIN_LIKES = 20

# Max results per X API request (10-100)
X_MAX_RESULTS = 50

# --- Relevance filtering ---
# Stories scoring below this are dropped from the digest (see relevance.py).
# 3 = one company name or strong industry term is enough.
RELEVANCE_THRESHOLD = 3

# How many stories to pull from each source before filtering
RAW_STORIES_PER_SOURCE = 40

# How many ranked stories to show in the "Top Stories" email section
TOP_STORIES_COUNT = 15

# How many X posts to show in the email
X_POSTS_COUNT = 10

# Request settings
REQUEST_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Output settings
OUTPUT_DIR = "output"
MAX_STORIES_PER_SOURCE = 10

# Schedule settings (24-hour format)
DAILY_RUN_TIME = "07:00"


def get_x_bearer_token() -> str:
    """Return the X API bearer token, or empty string if not configured."""
    return os.environ.get(X_BEARER_TOKEN_ENV, "").strip()
