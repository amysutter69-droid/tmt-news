#!/usr/bin/env python3
"""
Scheduler for TMT News Scraper.

Runs the scraper automatically at a configured time each day.
Can also be used with system schedulers like cron or systemd.
"""

import time
from datetime import datetime

import schedule

import config
from main import run


def job():
    """Scheduled job to run the scraper."""
    print(f"\n{'#' * 60}")
    print(f"# SCHEDULED RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#' * 60}")

    try:
        run()
    except Exception as e:
        print(f"Error during scheduled run: {e}")


def start_scheduler():
    """Start the scheduler to run daily at the configured time."""
    run_time = config.DAILY_RUN_TIME

    print(f"TMT News Scheduler")
    print(f"=" * 40)
    print(f"Scheduled to run daily at: {run_time}")
    print(f"Press Ctrl+C to stop")
    print(f"=" * 40)

    # Schedule the job
    schedule.every().day.at(run_time).do(job)

    # Run the scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TMT News Scheduler")
    parser.add_argument(
        "--run-now", "-r",
        action="store_true",
        help="Run once immediately then exit"
    )
    parser.add_argument(
        "--daemon", "-d",
        action="store_true",
        help="Run as daemon (continuous scheduling)"
    )

    args = parser.parse_args()

    if args.run_now:
        print("Running scraper once...")
        job()
    elif args.daemon:
        start_scheduler()
    else:
        # Default: run once
        print("Running scraper once (use --daemon for continuous scheduling)...")
        job()
