# TMT News Scraper

Daily aggregator for Tech, Media, and Telecom news from top sources.

## Sources

- **Techmeme** - Tech news aggregator
- **TrendForce** - Tech industry research and news
- **TechCrunch** - Startup and technology news

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run Once

```bash
python main.py
```

### Options

```bash
# JSON output only
python main.py --format json

# Markdown output only
python main.py --format markdown

# Limit stories per source
python main.py --max 5
```

### Output

Files are saved to the `output/` directory:
- `news_YYYY-MM-DD_HH-MM-SS.json` - Machine-readable JSON
- `news_YYYY-MM-DD_HH-MM-SS.md` - Human-readable Markdown

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

### Option 4: Systemd Service (Linux)

Create `/etc/systemd/system/tmt-news.service`:

```ini
[Unit]
Description=TMT News Scraper
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/tmt-news
ExecStart=/path/to/venv/bin/python scheduler.py --daemon
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable tmt-news
sudo systemctl start tmt-news
```

## Configuration

Edit `config.py` to customize:

- `MAX_STORIES_PER_SOURCE` - Number of stories to fetch per source (default: 10)
- `DAILY_RUN_TIME` - Time to run when using built-in scheduler (default: "07:00")
- `OUTPUT_DIR` - Where to save output files (default: "output")

## Adding New Sources

1. Create a new scraper in `scrapers/` (use `base.py` as template)
2. Add source config to `config.py`
3. Import and add scraper to `main.py`
