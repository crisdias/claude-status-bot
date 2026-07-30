import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List

import httpx
import feedparser

RSS_URL = "https://status.claude.com/history.rss"

BRT = timezone(timedelta(hours=-3))


@dataclass
class StatusUpdate:
    timestamp: str
    status: str
    message: str


@dataclass
class Incident:
    guid: str
    title: str
    link: str
    updates: List[StatusUpdate] = field(default_factory=list)


def _to_brt(timestamp: str, ref_year: int) -> str:
    normalized = re.sub(r"\s+", " ", timestamp).strip()
    try:
        parsed = datetime.strptime(f"{ref_year} {normalized}", "%Y %b %d, %H:%M UTC")
    except ValueError:
        return timestamp
    parsed = parsed.replace(tzinfo=timezone.utc)
    if parsed > datetime.now(timezone.utc) + timedelta(days=1):
        parsed = parsed.replace(year=ref_year - 1)
    return parsed.astimezone(BRT).strftime("%d %b, %H:%M BRT")


def _parse_description(html: str, ref_year: int) -> List[StatusUpdate]:
    updates: List[StatusUpdate] = []
    p_pattern = re.compile(r"<p[^>]*>(.*?)</p>", re.DOTALL | re.IGNORECASE)
    strip_tags = re.compile(r"<[^>]+>")

    for p_match in p_pattern.finditer(html):
        p_html = p_match.group(1)

        small_match = re.search(r"<small[^>]*>(.*?)</small>", p_html, re.DOTALL | re.IGNORECASE)
        if not small_match:
            continue
        timestamp = _to_brt(strip_tags.sub("", small_match.group(1)).strip(), ref_year)

        strong_match = re.search(r"<strong[^>]*>(.*?)</strong>", p_html, re.DOTALL | re.IGNORECASE)
        if not strong_match:
            continue
        status = strong_match.group(1).strip()

        msg_match = re.search(r"</strong>\s*[-–—]?\s*(.*)", p_html, re.DOTALL)
        message = strip_tags.sub("", msg_match.group(1)).strip() if msg_match else ""

        updates.append(StatusUpdate(timestamp=timestamp, status=status, message=message))

    return updates


async def fetch_incidents() -> List[Incident]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(RSS_URL)
        resp.raise_for_status()

    feed = feedparser.parse(resp.text)
    incidents: List[Incident] = []
    for entry in feed.entries:
        published = entry.get("published_parsed") or time.gmtime()
        updates = _parse_description(entry.get("description", ""), published.tm_year)
        if not updates:
            continue
        incidents.append(Incident(
            guid=entry.get("id") or entry.get("link", ""),
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            updates=updates,
        ))
    return incidents
