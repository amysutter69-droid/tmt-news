"""
Summarize podcast episodes through an investor lens using the Claude API.
Requires ANTHROPIC_API_KEY in environment.
"""

import os
import anthropic

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


SYSTEM_PROMPT = """\
You are a sharp investment analyst who listens to tech and business podcasts \
and distills them into actionable intelligence for investors. \
You focus on: market signals, competitive dynamics, funding/M&A activity, \
macro trends, regulatory risk, and technology shifts that could move capital. \
Be concise, direct, and opinionated where the data supports it. \
Avoid filler phrases."""


def summarize_episode(podcast: str, title: str, description: str) -> str:
    """Return a 4-6 bullet investor summary for one episode."""
    if not description.strip():
        return "No transcript or description available to summarize."

    prompt = f"""\
Podcast: {podcast}
Episode: {title}

Description / show notes:
{description[:3000]}

Write 4-6 tight bullet points summarizing this episode from an investor's perspective. \
Each bullet should surface a concrete insight, signal, or risk relevant to markets, \
companies, or capital allocation. Start each bullet with a bold keyword label, e.g. \
**AI Capex:**, **Regulatory Risk:**, **Valuation Signal:**."""

    client = _get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def summarize_all(episodes: list[dict]) -> list[dict]:
    """Add an 'investor_summary' field to each episode dict."""
    results = []
    for ep in episodes:
        print(f"  Summarizing: {ep['podcast']} — {ep['title'][:60]}")
        try:
            summary = summarize_episode(ep["podcast"], ep["title"], ep["description"])
        except Exception as e:
            summary = f"[Summary failed: {e}]"
        results.append({**ep, "investor_summary": summary})
    return results
