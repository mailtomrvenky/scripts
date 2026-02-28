#!/usr/bin/env python3
"""Fetch top global news stories from Al Jazeera RSS and print a concise digest."""
from __future__ import annotations

import datetime as dt
import sys
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore

RSS_URL = "https://www.aljazeera.com/xml/rss/all.xml"
MAX_ITEMS = 6
IST = ZoneInfo("Asia/Kolkata") if ZoneInfo else None

def fetch_feed_xml() -> str:
    req = urllib.request.Request(
        RSS_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; OpenClawBot/1.0; +https://openclaw.ai)",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read()
        return data.decode("utf-8", errors="ignore")

def parse_items(xml_text: str) -> List[Dict[str, str]]:
    root = ET.fromstring(xml_text)
    items: List[Dict[str, str]] = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "(untitled)").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        summary = (item.findtext("description") or "").strip()
        items.append({
            "title": title,
            "link": link,
            "pubDate": pub,
            "summary": summary,
        })
        if len(items) >= MAX_ITEMS:
            break
    return items

def parse_pubdate(pubdate: str) -> dt.datetime | None:
    if not pubdate:
        return None
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S",
    ):
        try:
            dt_obj = dt.datetime.strptime(pubdate, fmt)
            if dt_obj.tzinfo is None:
                dt_obj = dt_obj.replace(tzinfo=dt.timezone.utc)
            return dt_obj
        except ValueError:
            continue
    return None

def format_item(item: Dict[str, str], idx: int) -> str:
    title = item["title"]
    link = item["link"]
    summary = item["summary"]
    pub = parse_pubdate(item["pubDate"])
    if pub and IST:
        pub = pub.astimezone(IST)
    pub_str = pub.strftime("%d %b %Y %H:%M %Z") if isinstance(pub, dt.datetime) else "time n/a"
    link_fmt = f"[{title}]({link})" if link else title
    summary_clean = summary.replace("\n", " ").strip()
    return f"{idx}. {link_fmt}\n   • {summary_clean}\n   • Published: {pub_str}"

def main() -> int:
    try:
        xml_text = fetch_feed_xml()
        items = parse_items(xml_text)
    except Exception as exc:  # pragma: no cover
        print(f"Failed to fetch Al Jazeera RSS feed: {exc}", file=sys.stderr)
        return 1

    if not items:
        print("No Al Jazeera global news items available right now.")
        return 0

    now = dt.datetime.now(tz=IST) if IST else dt.datetime.now()
    header = now.strftime("Global Nightly Brief · %d %b %Y (%H:%M %Z)")
    print(header)
    print("=" * len(header))
    for idx, item in enumerate(items, start=1):
        print(format_item(item, idx))
        print()

    print("Source: Al Jazeera RSS (all stories)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
