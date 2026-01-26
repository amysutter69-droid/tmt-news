#!/usr/bin/env python3
"""
TMT News Scraper - Daily tech, media, and telecom news aggregator.

Scrapes top stories from:
- Techmeme
- TrendForce
- TechCrunch
"""

import json
import os
from datetime import datetime
from pathlib import Path

import config
from scrapers import TechmemeScraper, TrendforceScraper, TechcrunchScraper


def get_all_scrapers():
    """Return instances of all available scrapers."""
    return [
        TechmemeScraper(),
        TrendforceScraper(),
        TechcrunchScraper(),
    ]


def scrape_all_sources(max_per_source: int = None) -> dict:
    """
    Scrape news from all configured sources.

    Returns:
        Dictionary with source names as keys and lists of stories as values.
    """
    all_stories = {}
    scrapers = get_all_scrapers()

    for scraper in scrapers:
        print(f"Scraping {scraper.name}...")
        try:
            stories = scraper.get_stories(max_per_source)
            all_stories[scraper.name] = [s.to_dict() for s in stories]
            print(f"  Found {len(stories)} stories from {scraper.name}")
        except Exception as e:
            print(f"  Error scraping {scraper.name}: {e}")
            all_stories[scraper.name] = []

    return all_stories


def save_to_json(stories: dict, output_dir: str = None) -> str:
    """Save stories to a JSON file."""
    output_path = Path(output_dir or config.OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = output_path / f"news_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "scraped_at": datetime.now().isoformat(),
            "sources": stories
        }, f, indent=2, ensure_ascii=False)

    return str(filename)


def save_to_markdown(stories: dict, output_dir: str = None) -> str:
    """Save stories to a readable Markdown file."""
    output_path = Path(output_dir or config.OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_display = datetime.now().strftime("%B %d, %Y")
    filename = output_path / f"news_{timestamp}.md"

    lines = [
        f"# TMT News Digest - {date_display}",
        "",
        f"*Generated at {datetime.now().strftime('%H:%M:%S')}*",
        "",
    ]

    for source_name, source_stories in stories.items():
        lines.append(f"## {source_name}")
        lines.append("")

        if not source_stories:
            lines.append("*No stories found*")
            lines.append("")
            continue

        for i, story in enumerate(source_stories, 1):
            title = story.get("title", "Untitled")
            url = story.get("url", "#")
            summary = story.get("summary", "")
            author = story.get("author", "")
            pub_date = story.get("published_date", "")

            lines.append(f"### {i}. [{title}]({url})")

            meta_parts = []
            if author:
                meta_parts.append(f"*By {author}*")
            if pub_date:
                meta_parts.append(f"*{pub_date[:10]}*")
            if meta_parts:
                lines.append(" | ".join(meta_parts))

            if summary:
                lines.append("")
                lines.append(f"> {summary}")

            lines.append("")

        lines.append("---")
        lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return str(filename)


def print_summary(stories: dict):
    """Print a console summary of scraped stories."""
    print("\n" + "=" * 60)
    print("TMT NEWS DIGEST")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    total_stories = 0

    for source_name, source_stories in stories.items():
        print(f"\n## {source_name} ({len(source_stories)} stories)")
        print("-" * 40)

        for i, story in enumerate(source_stories[:5], 1):  # Show top 5 in console
            title = story.get("title", "Untitled")
            if len(title) > 70:
                title = title[:67] + "..."
            print(f"  {i}. {title}")

        if len(source_stories) > 5:
            print(f"  ... and {len(source_stories) - 5} more")

        total_stories += len(source_stories)

    print("\n" + "=" * 60)
    print(f"Total: {total_stories} stories from {len(stories)} sources")
    print("=" * 60)


def run(output_format: str = "both", max_per_source: int = None):
    """
    Main entry point for the scraper.

    Args:
        output_format: 'json', 'markdown', or 'both'
        max_per_source: Maximum stories per source (defaults to config value)
    """
    print(f"\nTMT News Scraper starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    # Scrape all sources
    stories = scrape_all_sources(max_per_source)

    # Save outputs
    saved_files = []

    if output_format in ("json", "both"):
        json_file = save_to_json(stories)
        saved_files.append(json_file)
        print(f"\nSaved JSON: {json_file}")

    if output_format in ("markdown", "both"):
        md_file = save_to_markdown(stories)
        saved_files.append(md_file)
        print(f"Saved Markdown: {md_file}")

    # Print summary
    print_summary(stories)

    return stories, saved_files


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TMT News Scraper")
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "both"],
        default="both",
        help="Output format (default: both)"
    )
    parser.add_argument(
        "--max", "-m",
        type=int,
        default=None,
        help=f"Max stories per source (default: {config.MAX_STORIES_PER_SOURCE})"
    )

    args = parser.parse_args()
    run(output_format=args.format, max_per_source=args.max)
