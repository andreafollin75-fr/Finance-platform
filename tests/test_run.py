"""End-to-end test of the pipeline with fake feeds (no network)."""

import json
from datetime import datetime, timezone
from pathlib import Path

from pipeline import run as run_module
from pipeline.fetch import FeedError, parse_feed

NOW = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
FEED = (Path(__file__).parent / "fixtures" / "sample_feed.xml").read_bytes()


def test_a_failing_source_keeps_its_previous_articles(tmp_path, monkeypatch):
    first_source = run_module.load_sources()[0]["name"]

    def all_work(source, cache, now, session):
        return parse_feed(FEED, source, now) if source["name"] == first_source else []

    monkeypatch.setattr(run_module, "fetch_source", all_work)
    run_module.run(data_dir=tmp_path, now=NOW)
    before = json.loads((tmp_path / "articles.json").read_text())
    assert len(before) == 3

    def all_fail(source, cache, now, session):
        raise FeedError("HTTP 503")

    monkeypatch.setattr(run_module, "fetch_source", all_fail)
    run_module.run(data_dir=tmp_path, now=NOW)  # must not raise
    after = json.loads((tmp_path / "articles.json").read_text())
    assert {a["id"] for a in after} == {a["id"] for a in before}
    status = json.loads((tmp_path / "sources_status.json").read_text())
    assert status[first_source]["ok"] is False
    assert status[first_source]["last_success"] == NOW.isoformat()  # kept from the good run


def test_output_files_are_written(tmp_path, monkeypatch):
    monkeypatch.setattr(run_module, "fetch_source", lambda s, c, n, sess: parse_feed(FEED, s, n))
    run_module.run(data_dir=tmp_path, now=NOW)
    for name in ("articles.json", "news.json", "briefing.json", "sources_status.json"):
        assert (tmp_path / name).exists()
    news = json.loads((tmp_path / "news.json").read_text())
    # Every fake source returns the same three URLs, so exact de-duplication leaves 3 articles.
    assert news["meta"]["story_count"] == 3
    fed = next(s for s in news["stories"] if s["lead"]["title"].startswith("Fed"))
    assert "inflation" in fed["lead"]["terms"]
