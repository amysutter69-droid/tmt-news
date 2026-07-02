#!/usr/bin/env python3
"""
Semiconductor & Hardware News Scraper - daily digest for investor emails.

Pulls stories from tech news sites (HTML + RSS) and X.com, scores each
story for semiconductor/hardware relevance, and produces a ranked digest.
"""

import json
from datetime import datetime
from pathlib import Path

import config
import relevance
from scrapers import (
    TechmemeScraper, TrendforceScraper, TechcrunchScraper, DigitimesScraper,
    RSSScraper, XScraper,
)

X_SOURCE_NAME = config.NEWS_SOURCES["x"]["name"]


def get_all_scrapers():
    """Return instances of all available scrapers."""
    scrapers = [
        TechmemeScraper(),
        TrendforceScraper(),
        TechcrunchScraper(),
        DigitimesScraper(),
    ]
    scrapers.extend(RSSScraper(key) for key in config.RSS_SOURCES)
    scrapers.append(XScraper())
    return scrapers


def scrape_all_sources() -> dict:
    """
    Scrape news from all configured sources and score each story.

    Returns:
        Dictionary with source names as keys and lists of story dicts
        (including relevance_score) as values.
    """
    all_stories = {}
    scrapers = get_all_scrapers()

    for scraper in scrapers:
        print(f"Scraping {scraper.name}...")
        try:
            stories = scraper.get_stories(config.RAW_STORIES_PER_SOURCE)
            scored = [relevance.score_story(s.to_dict()) for s in stories]
            all_stories[scraper.name] = scored
            print(f"  Found {len(scored)} stories from {scraper.name}")
        except Exception as e:
            print(f"  Error scraping {scraper.name}: {e}")
            all_stories[scraper.name] = []

    return all_stories


def build_digest(all_stories: dict, filtered: bool = True, max_per_source: int = None) -> dict:
    """
    Turn raw scraped stories into a structured digest.

    Returns a dict with:
        top_stories: ranked, deduped semiconductor/hardware stories (web sources)
        x_posts: ranked posts from X
        by_source: relevant stories per source, trimmed for display
    """
    per_source_limit = max_per_source or config.MAX_STORIES_PER_SOURCE

    web_stories = []
    x_posts = []
    by_source = {}

    for source_name, stories in all_stories.items():
        if filtered:
            stories = [s for s in stories if relevance.is_relevant(s)]
        ranked = relevance.rank_stories(stories)

        if source_name == X_SOURCE_NAME:
            x_posts = ranked[:config.X_POSTS_COUNT]
        else:
            by_source[source_name] = ranked[:per_source_limit]
            web_stories.extend(ranked)

    top_stories = relevance.dedupe_stories(relevance.rank_stories(web_stories))
    top_stories = top_stories[:config.TOP_STORIES_COUNT]

    return {
        "top_stories": top_stories,
        "x_posts": x_posts,
        "by_source": by_source,
    }


def save_to_json(all_stories: dict, output_dir: str = None) -> str:
    """Save all scraped stories (with scores) to a JSON file."""
    output_path = Path(output_dir or config.OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = output_path / f"news_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "scraped_at": datetime.now().isoformat(),
            "sources": all_stories
        }, f, indent=2, ensure_ascii=False)

    return str(filename)


def save_to_markdown(digest: dict, output_dir: str = None) -> str:
    """Save the digest to a readable Markdown file."""
    output_path = Path(output_dir or config.OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_display = datetime.now().strftime("%B %d, %Y")
    filename = output_path / f"news_{timestamp}.md"

    lines = [
        f"# Semiconductor & Hardware Daily - {date_display}",
        "",
        f"*Generated at {datetime.now().strftime('%H:%M:%S')}*",
        "",
        "## Top Stories",
        "",
    ]

    if not digest["top_stories"]:
        lines.append("*No relevant stories found*")
        lines.append("")
    for i, story in enumerate(digest["top_stories"], 1):
        lines.append(f"**{i}. {story['title']}** *({story['source']})*")
        lines.append(f"{story['url']}")
        if story.get("summary"):
            lines.append(f"> {story['summary']}")
        lines.append("")

    lines.append("## From X")
    lines.append("")
    if not digest["x_posts"]:
        lines.append("*No X posts (source unavailable or no relevant posts)*")
        lines.append("")
    for i, post in enumerate(digest["x_posts"], 1):
        lines.append(f"**{i}. {post.get('author', '')}**: {post['title']}")
        lines.append(f"{post['url']}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## By Source")
    lines.append("")

    for source_name, source_stories in digest["by_source"].items():
        lines.append(f"### {source_name}")
        lines.append("")
        if not source_stories:
            lines.append("*No relevant stories found*")
            lines.append("")
            continue
        for i, story in enumerate(source_stories, 1):
            lines.append(f"**{i}. {story['title']}**")
            lines.append(f"{story['url']}")
            lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return str(filename)


def save_to_email_text(digest: dict, output_dir: str = None) -> str:
    """Save the digest to a plain text file optimized for email."""
    output_path = Path(output_dir or config.OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_display = datetime.now().strftime("%B %d, %Y")
    filename = output_path / f"news_{timestamp}_email.txt"

    lines = [
        f"SEMICONDUCTOR & HARDWARE DAILY - {date_display}",
        "=" * 50,
        "",
        "TOP STORIES",
        "-" * 30,
        "",
    ]

    if not digest["top_stories"]:
        lines.append("No relevant stories found")
        lines.append("")
    for i, story in enumerate(digest["top_stories"], 1):
        lines.append(f"{i}. {story['title']} [{story['source']}]")
        lines.append(f"   {story['url']}")
        lines.append("")

    lines.append("FROM X")
    lines.append("-" * 30)
    lines.append("")
    if not digest["x_posts"]:
        lines.append("No X posts (source unavailable or no relevant posts)")
        lines.append("")
    for i, post in enumerate(digest["x_posts"], 1):
        lines.append(f"{i}. {post.get('author', '')}: {post['title']}")
        lines.append(f"   {post['url']}")
        lines.append("")

    lines.append("")
    lines.append("MORE BY SOURCE")
    lines.append("=" * 50)
    lines.append("")

    for source_name, source_stories in digest["by_source"].items():
        if not source_stories:
            continue
        lines.append(source_name.upper())
        lines.append("-" * 30)
        for i, story in enumerate(source_stories, 1):
            lines.append(f"{i}. {story['title']}")
            lines.append(f"   {story['url']}")
            lines.append("")
        lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return str(filename)


def print_summary(digest: dict):
    """Print a console summary of the digest."""
    print("\n" + "=" * 60)
    print("SEMICONDUCTOR & HARDWARE DAILY")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    print(f"\n## Top Stories ({len(digest['top_stories'])})")
    print("-" * 40)
    for i, story in enumerate(digest["top_stories"][:10], 1):
        title = story["title"]
        if len(title) > 60:
            title = title[:57] + "..."
        print(f"  {i}. [{story['relevance_score']:>2}] {title} ({story['source']})")

    print(f"\n## X Posts ({len(digest['x_posts'])})")
    print("-" * 40)
    for i, post in enumerate(digest["x_posts"][:5], 1):
        title = post["title"]
        if len(title) > 60:
            title = title[:57] + "..."
        print(f"  {i}. {post.get('author', '')}: {title}")

    print("\n## Relevant stories by source")
    print("-" * 40)
    for source_name, stories in digest["by_source"].items():
        print(f"  {source_name}: {len(stories)}")

    print("=" * 60)


def run(output_format: str = "both", max_per_source: int = None, filtered: bool = True):
    """
    Main entry point for the scraper.

    Args:
        output_format: 'json', 'markdown', 'email', 'both', or 'all'
        max_per_source: Maximum stories per source in by-source sections
        filtered: Apply semiconductor/hardware relevance filtering
    """
    print(f"\nNews scraper starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    all_stories = scrape_all_sources()
    digest = build_digest(all_stories, filtered=filtered, max_per_source=max_per_source)

    saved_files = []

    if output_format in ("json", "both", "all"):
        json_file = save_to_json(all_stories)
        saved_files.append(json_file)
        print(f"\nSaved JSON: {json_file}")

    if output_format in ("markdown", "both", "all"):
        md_file = save_to_markdown(digest)
        saved_files.append(md_file)
        print(f"Saved Markdown: {md_file}")

    if output_format in ("email", "both", "all"):
        email_file = save_to_email_text(digest)
        saved_files.append(email_file)
        print(f"Saved Email text: {email_file}")

    print_summary(digest)

    return digest, saved_files


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Semiconductor & Hardware News Scraper")
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "email", "both", "all"],
        default="both",
        help="Output format: json, markdown, email, both (all three), or all"
    )
    parser.add_argument(
        "--max", "-m",
        type=int,
        default=None,
        help=f"Max stories per source in by-source sections (default: {config.MAX_STORIES_PER_SOURCE})"
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Skip semiconductor/hardware relevance filtering (include all stories)"
    )

    args = parser.parse_args()
    run(output_format=args.format, max_per_source=args.max, filtered=not args.no_filter)
