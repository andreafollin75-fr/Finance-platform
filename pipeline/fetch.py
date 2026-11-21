"""Download RSS/Atom feeds and turn their entries into simple article dicts.

Politeness rules (see SOURCES.md):
- an explicit User-Agent is sent with every request;
- conditional requests (ETag / Last-Modified) are used, so an unchanged feed
  costs the publisher almost nothing;
- each feed is requested once per run, and runs happen at most once per hour.
"""

from __future__ import annotations

import hashlib
import html
import logging
import re
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import requests

from .config import EXCERPT_MAX_CHARS, REQUEST_TIMEOUT_SECONDS, USER_AGENT

log = logging.getLogger(__name__)

# Query parameters that only track clicks and never change the page.
TRACKING_PARAMS = re.compile(r"^(utm_|mc_|fbclid|gclid|cmpid|ncid|yptr|guccounter|__source)", re.I)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


class FeedError(Exception):
    """Raised when a feed cannot be downloaded or parsed."""


def canonical_url(url: str) -> str:
    """Return the URL without tracking parameters, fragment, or trailing slash."""
    parts = urlsplit(url.strip())
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not TRACKING_PARAMS.match(k)]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def article_id(url: str) -> str:
    return hashlib.sha1(canonical_url(url).encode("utf-8")).hexdigest()[:16]


def clean_text(raw: str) -> str:
    """Strip HTML tags and entities and collapse whitespace."""
    text = TAG_RE.sub(" ", raw or "")
    text = html.unescape(text)
    return SPACE_RE.sub(" ", text).strip()


def make_excerpt(raw: str, limit: int = EXCERPT_MAX_CHARS) -> str:
    """Short excerpt from the feed's own description, cut on a word boundary."""
    text = clean_text(raw)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:.-")
    return cut + "…"


def entry_datetime(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        value = entry.get(key)
        if value:
            # feedparser always returns these as UTC struct_time values.
            return datetime(*value[:6], tzinfo=timezone.utc)
    return None


def parse_feed(content: bytes, source: dict, now: datetime) -> list[dict]:
    """Parse raw feed bytes into article dicts. Pure function, easy to test."""
    parsed = feedparser.parse(content)
    if parsed.bozo and not parsed.entries:
        raise FeedError(f"could not parse feed: {parsed.get('bozo_exception')}")
    articles = []
    for entry in parsed.entries:
        url = entry.get("link")
        title = clean_text(entry.get("title", ""))
        if not url or not title:
            continue
        published = entry_datetime(entry)
        # Ignore dates in the future (badly configured feeds) by clamping to now.
        if published is None or published > now:
            published = now
        articles.append(
            {
                "id": article_id(url),
                "title": title,
                "url": url.strip(),
                "source": source["name"],
                "source_kind": source.get("kind", "media"),
                "published": published.isoformat(),
                "excerpt": make_excerpt(entry.get("summary", "")),
                "themes": list(source.get("themes", [])),
            }
        )
    return articles


def fetch_source(source: dict, http_cache: dict, now: datetime, session: requests.Session | None = None) -> list[dict] | None:
    """Download one feed.

    Returns a list of articles, or None if the feed has not changed since the
    last run (HTTP 304). Raises FeedError on any failure.
    """
    session = session or requests.Session()
    headers = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.5"}
    cached = http_cache.get(source["url"], {})
    if cached.get("etag"):
        headers["If-None-Match"] = cached["etag"]
    if cached.get("last_modified"):
        headers["If-Modified-Since"] = cached["last_modified"]
    try:
        response = session.get(source["url"], headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise FeedError(f"network error: {exc}") from exc
    if response.status_code == 304:
        return None
    if response.status_code != 200:
        raise FeedError(f"HTTP {response.status_code}")
    http_cache[source["url"]] = {
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
    }
    return parse_feed(response.content, source, now)
