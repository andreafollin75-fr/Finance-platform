from datetime import datetime, timezone
from pathlib import Path

from pipeline.fetch import canonical_url, make_excerpt, parse_feed

NOW = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
SOURCE = {"name": "Sample", "themes": ["us"], "kind": "media"}
FEED = (Path(__file__).parent / "fixtures" / "sample_feed.xml").read_bytes()


def test_parse_feed_reads_items_and_skips_items_without_link():
    articles = parse_feed(FEED, SOURCE, NOW)
    titles = [a["title"] for a in articles]
    assert "Item without a link is skipped" not in titles
    assert len(articles) == 3


def test_parse_feed_strips_html_and_converts_dates_to_utc():
    articles = {a["title"]: a for a in parse_feed(FEED, SOURCE, NOW)}
    fed = articles["Fed holds interest rates steady as inflation cools"]
    assert fed["excerpt"] == "The Federal Reserve left its policy rate unchanged on Wednesday."
    assert fed["published"] == "2026-11-20T18:00:00+00:00"
    ecb = articles["ECB's Lagarde signals patience on rate cuts"]
    assert ecb["published"] == "2026-11-20T11:30:00+00:00"  # +01:00 converted to UTC


def test_missing_date_uses_fetch_time():
    articles = {a["title"]: a for a in parse_feed(FEED, SOURCE, NOW)}
    assert articles["Item without a date gets the fetch time"]["published"] == NOW.isoformat()


def test_canonical_url_removes_tracking_parameters():
    assert canonical_url("https://Example.com/a/?utm_source=x&id=3#top") == "https://example.com/a?id=3"
    assert canonical_url("https://example.com/a") == canonical_url("https://example.com/a/?utm_medium=rss")


def test_excerpt_is_short_and_ends_on_a_word():
    text = "word " * 200
    excerpt = make_excerpt(text, limit=50)
    assert len(excerpt) <= 51
    assert excerpt.endswith("…")
    assert "wor…" not in excerpt
