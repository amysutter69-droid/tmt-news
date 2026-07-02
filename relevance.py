"""Semiconductor & hardware relevance scoring for news stories.

Each story is scored by matching its title and summary against weighted
keyword lists. Stories at or above config.RELEVANCE_THRESHOLD are kept.
"""

import re

import config

# Company / ticker names. Weight 3: one match alone makes a story relevant.
COMPANY_TERMS = [
    "tsmc", "taiwan semiconductor", "nvidia", "intel", "asml",
    "sk hynix", "hynix", "micron", "qualcomm", "broadcom", "arm holdings",
    "applied materials", "lam research", "kla", "tokyo electron",
    "globalfoundries", "umc", "smic", "texas instruments", "nxp",
    "infineon", "stmicroelectronics", "stmicro", "renesas", "onsemi",
    "analog devices", "marvell", "mediatek", "kioxia", "western digital",
    "sandisk", "seagate", "cadence", "synopsys", "rapidus", "amkor",
    "ase technology", "besi", "asm international", "ibiden", "supermicro",
    "super micro", "foxconn", "quanta", "wistron", "inventec", "vertiv",
    "astera labs", "credo", "coherent", "lumentum", "arista", "celestica",
    "samsung electronics", "samsung foundry",
]

# Strong technology / industry terms. Weight 3.
STRONG_TERMS = [
    "semiconductor", "semiconductors", "chipmaker", "chipmakers",
    "foundry", "foundries", "fab", "fabs", "wafer", "wafers",
    "lithography", "euv", "duv", "hbm", "hbm3", "hbm3e", "hbm4",
    "dram", "nand", "chiplet", "chiplets", "cowos", "advanced packaging",
    "interposer", "osat", "tapeout", "tape-out", "2nm", "3nm", "4nm",
    "5nm", "7nm", "18a", "16a", "a16", "n2", "risc-v", "gpu", "gpus",
    "tpu", "asic", "asics", "npu", "ai accelerator", "ai accelerators",
    "ai chip", "ai chips", "memory chip", "memory chips", "logic chip",
    "silicon carbide", "gallium nitride", "photonics",
    "co-packaged optics", "chip export", "chip exports", "export controls",
    "chips act", "memory prices", "wafer fab equipment",
]

# Medium terms. Weight 2: need a second signal to clear the threshold.
MEDIUM_TERMS = [
    "chip", "chips", "silicon", "cpu", "cpus", "x86", "data center",
    "datacenter", "data centers", "datacenters", "hyperscaler",
    "hyperscalers", "server", "servers", "hpc", "infiniband", "ethernet",
    "optical transceiver", "optical transceivers", "liquid cooling",
    "substrate", "substrates", "smartphone shipments", "pc shipments",
    "ai infrastructure", "capex", "teardown",
]

# Weak terms. Weight 1: only matter in combination.
WEAK_TERMS = [
    "hardware", "supply chain", "capacity", "yield", "node", "process node",
    "motherboard", "pcb", "networking", "storage", "memory",
]

_WEIGHTED_TERMS = (
    [(t, 3) for t in COMPANY_TERMS]
    + [(t, 3) for t in STRONG_TERMS]
    + [(t, 2) for t in MEDIUM_TERMS]
    + [(t, 1) for t in WEAK_TERMS]
)

# Pre-compile one word-boundary pattern per term.
_PATTERNS = [
    (re.compile(r"\b" + re.escape(term).replace(r"\ ", r"\s+") + r"\b", re.IGNORECASE), term, weight)
    for term, weight in _WEIGHTED_TERMS
]


def score_text(text: str) -> tuple[int, list[str]]:
    """Score a text blob. Returns (score, matched_terms).

    Each distinct term counts once, so repeating a keyword doesn't
    inflate the score.
    """
    score = 0
    matched = []
    for pattern, term, weight in _PATTERNS:
        if pattern.search(text):
            score += weight
            matched.append(term)
    return score, matched


def score_story(story: dict) -> dict:
    """Attach relevance_score and matched_terms to a story dict."""
    text = f"{story.get('title', '')} {story.get('summary', '')}"
    score, matched = score_text(text)
    story["relevance_score"] = score
    story["matched_terms"] = matched
    return story


def is_relevant(story: dict) -> bool:
    """A story is relevant if it clears the configured threshold."""
    return story.get("relevance_score", 0) >= config.RELEVANCE_THRESHOLD


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def dedupe_stories(stories: list[dict]) -> list[dict]:
    """Drop stories with duplicate URLs or near-identical titles.

    Keeps the first occurrence, so pass stories in priority order.
    """
    seen_urls = set()
    seen_titles = set()
    unique = []
    for story in stories:
        url = (story.get("url") or "").split("?")[0].rstrip("/")
        title_key = _normalize_title(story.get("title", ""))
        if url and url in seen_urls:
            continue
        if title_key and title_key in seen_titles:
            continue
        if url:
            seen_urls.add(url)
        if title_key:
            seen_titles.add(title_key)
        unique.append(story)
    return unique


def rank_stories(stories: list[dict]) -> list[dict]:
    """Sort stories by relevance score (desc), then published date (desc)."""
    return sorted(
        stories,
        key=lambda s: (
            s.get("relevance_score", 0),
            s.get("published_date") or "",
        ),
        reverse=True,
    )
