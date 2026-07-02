# Semiconductor & Hardware News Scraper

Daily aggregator of semiconductor and hardware news from news sites and
X.com, ranked by relevance for a morning investor email.

## How it works

1. Scrapes stories from 13 news sources plus X.com
2. Scores every story against weighted semiconductor/hardware keywords
   (company names like TSMC/Nvidia/ASML, industry terms like HBM, EUV,
   foundry, advanced packaging - see `relevance.py`)
3. Drops irrelevant stories, dedupes across sources, and ranks the rest
4. Emails a digest: **Top Stories** (cross-source ranked), **From X**,
   and **More by Source**

## Sources

**HTML scrapers:** Techmeme, TrendForce, TechCrunch, DigiTimes

**RSS feeds:** Tom's Hardware, SemiEngineering, EE Times, The Register,
ServeTheHome, The Next Platform, SemiWiki, Ars Technica, CNBC Tech

**X.com:** curated semiconductor accounts (@dnystedt, @dylan522p,
@SemiAnalysis_, @IanCutress, @TrendForce, @SKundojjala) plus a keyword
search, via the official X API v2

## Automated Daily Email (GitHub Actions)

The easiest way to use this scraper - no local setup required!

### Setup Steps

1. **Fork or clone this repo** to your GitHub account

2. **Add email secrets** in your repo settings:
   - Go to: Settings → Secrets and variables → Actions
   - Add these two secrets:
     - `GMAIL_USERNAME`: Your Gmail address
     - `GMAIL_APP_PASSWORD`: A Gmail **App Password** (not your regular
       password) - generate one at https://myaccount.google.com/apppasswords

3. **(Optional but recommended) Add an X API token** to include X.com posts:
   - Sign up at https://developer.x.com and subscribe to a tier that
     includes search (Basic or above - the free tier does not include
     reading/search)
   - Copy the app's **Bearer Token**
   - Add it as a repo secret named `X_BEARER_TOKEN`
   - Without this secret, the digest still runs; the X section is just skipped

4. **Enable the workflow**:
   - Go to: Actions tab → "Daily TMT News Digest" → Enable workflow

5. **Test it**: Click "Run workflow" to test immediately

The digest will be emailed to you every day at 7:00 AM EST.

---

## Local Installation (Alternative)

```bash
# Clone the repo
git clone https://github.com/amysutter69-droid/tmt-news.git
cd tmt-news

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: enable the X.com source
export X_BEARER_TOKEN="your-x-api-bearer-token"

# Run it
python main.py
```

## Usage

### Run Once

```bash
python main.py
```

### Options

```bash
# Email-format output only
python main.py --format email

# JSON output only (all stories with relevance scores, unfiltered)
python main.py --format json

# Limit stories per source in the by-source sections
python main.py --max 5

# Turn off semiconductor/hardware filtering (include all TMT stories)
python main.py --no-filter
```

### Output

Files are saved to the `output/` directory:
- `news_YYYY-MM-DD_HH-MM-SS.json` - All scraped stories with relevance scores
- `news_YYYY-MM-DD_HH-MM-SS.md` - Human-readable Markdown digest
- `news_YYYY-MM-DD_HH-MM-SS_email.txt` - Plain-text digest for email

## Scheduling

### Option 1: Built-in Scheduler

Run as a daemon (stays running and executes daily):

```bash
python scheduler.py --daemon
```

### Option 2: Cron (Linux/Mac)

Add to crontab (`crontab -e`):

```bash
# Run every day at 7:00 AM
0 7 * * * cd /path/to/tmt-news && /path/to/venv/bin/python main.py
```

### Option 3: Windows Task Scheduler

Create a task that runs:
```
C:\path\to\venv\Scripts\python.exe C:\path\to\tmt-news\main.py
```

## Configuration

Edit `config.py` to customize:

- `RSS_SOURCES` - Add or remove RSS feed sources (easiest way to add sites)
- `X_ACCOUNTS` - Curated X accounts to always include
- `X_KEYWORD_QUERY` - X search query (X API query syntax)
- `X_MIN_LIKES` - Minimum likes for X keyword-search results (default: 20)
- `RELEVANCE_THRESHOLD` - Minimum relevance score to keep a story (default: 3)
- `TOP_STORIES_COUNT` - Stories in the Top Stories section (default: 15)
- `MAX_STORIES_PER_SOURCE` - Stories per source in by-source sections (default: 10)
- `DAILY_RUN_TIME` - Time to run when using built-in scheduler (default: "07:00")

Edit `relevance.py` to tune the keyword lists used for scoring (companies,
technology terms, and their weights).

## Adding New Sources

**RSS feed (preferred):** add one entry to `RSS_SOURCES` in `config.py` - done.

**HTML site:** create a scraper in `scrapers/` (use `base.py` as template),
add the source to `NEWS_SOURCES` in `config.py`, and register it in
`main.py`'s `get_all_scrapers()`.
