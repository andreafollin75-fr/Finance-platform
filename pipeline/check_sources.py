"""Check every feed in sources.yml (including disabled ones) and print a report.

Usage:  python -m pipeline.check_sources

Use it before enabling a new source. It never fails the build: it only reports.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone

import requests
import yaml

from .config import SOURCES_FILE
from .fetch import FeedError, fetch_source


def main() -> int:
    with open(SOURCES_FILE, encoding="utf-8") as f:
        sources = (yaml.safe_load(f) or {}).get("sources", [])
    now = datetime.now(timezone.utc)
    session = requests.Session()
    print(f"{'Source':45} {'Enabled':8} Result")
    for src in sources:
        enabled = "yes" if src.get("enabled", True) else "no"
        try:
            articles = fetch_source(src, {}, now, session) or []
            newest = max((a["published"] for a in articles), default="-")[:10]
            result = f"OK, {len(articles)} items, newest {newest}"
        except FeedError as exc:
            result = f"FAILED: {exc}"
        print(f"{src['name'][:45]:45} {enabled:8} {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
