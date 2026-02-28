#!/usr/bin/env python3
"""Fetch recent technology stories from the Hacker News Algolia API and format a concise digest."""
from __future__ import annotations

import datetime as dt
import json
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, List

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore

API_URL = "https://hn.algolia.com/api/v1/search_by_date"
MAX_ITEMS = 6
POINTS_FLOOR = 25
QUERY = "technology"
IST = ZoneInfo("Asia/Kolkata") if ZoneInfo else None


def fetch_items() -> List[dict[str, Any]]:
    params = {
        "query": QUERY,
        "tags": "story",
        "hitsPerPage": 30,
        "numericFilters": f"points>{POINTS_FLOOR}",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.load(resp).get("hits", [])


def normalize_item(raw: dict[str, Any]) -> dict[str, Any]:
    title = raw.get("title") or raw.get("story_title") or "(untitled)"
    url = raw.get("url") or raw.get("story_url") or ""
    author = raw.get("author") or "unknown"
    points = raw.get("points") or 0
    created = raw.get("created_at") or ""
    published = None
    if created:
        try:
            published = dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
            if IST:
                published = published.astimezone(IST)
        except Exception:
            published = None
    domain = ""
    if url:
        try:
            domain = urllib.parse.urlparse(url).netloc
        except ValueError:
            domain = ""
    return {
        "title": title.strip(),
        "url": url,
        "author": author,
        "points": points,
        "published": published,
        "domain": domain,
    }


def format_item(item: dict[str, Any], idx: int) -> str:
    title = item["title"] or "(untitled)"
    url = item["url"]
    author = item["author"]
    points = item["points"]
    domain = item["domain"]
    published = item["published"]
    published_str = published.strftime("%d %b %Y %H:%M") if isinstance(published, dt.datetime) else "time n/a"
    link = f"[{title}]({url})" if url else title
    domain_part = f" · {domain}" if domain else ""
    return f"{idx}. {link}{domain_part}\n   • {points} pts · by {author} · {published_str}"


def main() -> int:
    try:
        items = [normalize_item(hit) for hit in fetch_items()]
    except Exception as exc:  # pragma: no cover - runtime failure reporting
        print(f"Failed to fetch technology stories: {exc}", file=sys.stderr)
        return 1

    filtered = items[:MAX_ITEMS]
    if not filtered:
        print("No recent technology stories found with current filters.")
        return 0

    now = dt.datetime.now(tz=IST) if IST else dt.datetime.now()
    header = now.strftime("Daily Tech Brief · %d %b %Y (%H:%M %Z)")
    print(header)
    print("=" * len(header))
    for idx, item in enumerate(filtered, start=1):
        print(format_item(item, idx))
        print()

    print("Source: Hacker News Algolia API (query='technology', points>25, last ~30 posts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
