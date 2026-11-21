"""Run the whole pipeline: fetch -> merge -> classify -> dedupe -> briefing -> JSON.

Usage:  python -m pipeline.run            (fetch the feeds from the internet)
        python -m pipeline.run --offline  (rebuild data from what is already in data/)

A source that fails never stops the run: the error is logged and recorded in
data/sources_status.json, and the articles already stored for that source are
kept until they are older than KEEP_DAYS.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from .briefing import build_briefing
from .classify import classify_article
from .config import DATA_DIR, KEEP_DAYS, load_sources
from .dedupe import group_stories, remove_exact_duplicates
from .fetch import FeedError, fetch_source
from .glossary import TermDetector, load_glossary

log = logging.getLogger("pipeline")


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Could not read %s (%s); starting fresh", path.name, exc)
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)  # atomic: a crash never leaves a half-written file


def run(offline: bool = False, data_dir: Path = DATA_DIR, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    sources = load_sources()
    glossary = load_glossary()
    detector = TermDetector(glossary)

    stored = {a["id"]: a for a in read_json(data_dir / "articles.json", [])}
    http_cache = read_json(data_dir / "http_cache.json", {})
    status = read_json(data_dir / "sources_status.json", {})

    if not offline:
        session = requests.Session()
        for src in sources:
            entry = status.get(src["name"], {})
            entry.update({"url": src["url"], "last_attempt": now.isoformat()})
            try:
                articles = fetch_source(src, http_cache, now, session)
                if articles is None:
                    log.info("%-40s unchanged", src["name"])
                    entry.update({"ok": True, "error": None})
                else:
                    for art in articles:
                        # Keep the first time we saw an article if its feed has no date.
                        old = stored.get(art["id"])
                        if old and old["published"] < art["published"] and art["published"] == now.isoformat():
                            art["published"] = old["published"]
                        stored[art["id"]] = art
                    log.info("%-40s %d items", src["name"], len(articles))
                    entry.update({"ok": True, "error": None, "last_success": now.isoformat(), "items": len(articles)})
            except FeedError as exc:
                log.warning("%-40s FAILED: %s (keeping previous articles)", src["name"], exc)
                entry.update({"ok": False, "error": str(exc)})
            except Exception as exc:  # never let one bad feed break the whole run
                log.exception("%-40s unexpected error", src["name"])
                entry.update({"ok": False, "error": f"unexpected error: {exc}"})
            status[src["name"]] = entry

    # Keep only recent articles from sources that are still enabled.
    cutoff = (now - timedelta(days=KEEP_DAYS)).isoformat()
    names = {s["name"] for s in sources}
    articles = [a for a in stored.values() if a["published"] >= cutoff and a["source"] in names]
    articles = [classify_article(a) for a in remove_exact_duplicates(articles)]
    for a in articles:
        a["terms"] = detector.slugs_in(f"{a['title']} {a['excerpt']}")
    articles.sort(key=lambda a: a["published"], reverse=True)

    stories = group_stories(articles)
    briefing = build_briefing(stories, now)
    status = {k: v for k, v in status.items() if k in names}

    meta = {"generated_at": now.isoformat(), "article_count": len(articles), "story_count": len(stories)}
    write_json(data_dir / "articles.json", articles)
    write_json(data_dir / "news.json", {"meta": meta, "stories": stories})
    write_json(data_dir / "briefing.json", {"meta": meta, "stories": briefing})
    write_json(data_dir / "sources_status.json", status)
    write_json(data_dir / "http_cache.json", http_cache)
    log.info("Done: %d articles, %d stories, %d in briefing", len(articles), len(stories), len(briefing))
    return meta


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--offline", action="store_true", help="do not download feeds")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run(offline=args.offline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
