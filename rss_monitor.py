import re
from dataclasses import dataclass, field
from typing import List

import httpx
import feedparser

RSS_URL = "https://status.claude.com/history.rss"


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


def _parse_description(html: str) -> List[StatusUpdate]:
    updates: List[StatusUpdate] = []
    p_pattern = re.compile(r"<p[^>]*>(.*?)</p>", re.DOTALL | re.IGNORECASE)
    strip_tags = re.compile(r"<[^>]+>")

    for p_match in p_pattern.finditer(html):
        p_html = p_match.group(1)

        small_match = re.search(r"<small[^>]*>(.*?)</small>", p_html, re.DOTALL | re.IGNORECASE)
        if not small_match:
            continue
        timestamp = strip_tags.sub("", small_match.group(1)).strip()

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
        updates = _parse_description(entry.get("description", ""))
        if not updates:
            continue
        incidents.append(Incident(
            guid=entry.get("id") or entry.get("link", ""),
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            updates=updates,
        ))
    return incidents
