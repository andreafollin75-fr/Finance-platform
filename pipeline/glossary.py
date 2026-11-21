"""Load glossary entries and detect glossary terms in text.

Each entry is a Markdown file in content/glossary/ with a YAML header:

    ---
    title: Inflation
    short: One sentence shown in tooltips.
    aliases: [inflation, inflationary]   # words detected in news titles
    related: [deflation, policy-rate]    # slugs (file names) of related entries
    ---
    ## Definition
    ...

The file name (without .md) is the entry's "slug", used in URLs.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .config import GLOSSARY_DIR
from .textmatch import PhraseMatcher

REQUIRED_FIELDS = ("title", "short", "aliases")
REQUIRED_SECTIONS = ("## Definition", "## Example", "## Why it matters")


def parse_entry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: missing YAML header")
    _, header, body = text.split("---", 2)
    try:
        meta = yaml.safe_load(header) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"{path.name}: invalid YAML header: {exc}") from exc
    for field in REQUIRED_FIELDS:
        if not meta.get(field):
            raise ValueError(f"{path.name}: missing field {field!r}")
    for section in REQUIRED_SECTIONS:
        if section not in body:
            raise ValueError(f"{path.name}: missing section {section!r}")
    return {
        "slug": path.stem,
        "title": meta["title"],
        # Short label for chips, e.g. "Stock index" for "Stock index (S&P 500, Nasdaq, Euro Stoxx 50)".
        "label": meta["title"].split(" (")[0],
        "short": meta["short"].strip(),
        "aliases": list(meta["aliases"]),
        "related": list(meta.get("related", [])),
        "body": body.strip(),
    }


def load_glossary(directory: Path = GLOSSARY_DIR) -> list[dict]:
    entries = [parse_entry(p) for p in sorted(directory.glob("*.md"))]
    slugs = {e["slug"] for e in entries}
    for e in entries:
        missing = [r for r in e["related"] if r not in slugs]
        if missing:
            raise ValueError(f"{e['slug']}: related entries not found: {missing}")
    return sorted(entries, key=lambda e: e["title"].lower())


class TermDetector:
    """Find glossary terms in a text (see textmatch.py for the matching rules)."""

    def __init__(self, entries: list[dict]):
        self.alias_to_slug = {}
        for e in entries:
            for alias in e["aliases"]:
                self.alias_to_slug[alias] = e["slug"]
        self.matcher = PhraseMatcher(self.alias_to_slug)

    def find(self, text: str) -> list[tuple[int, int, str]]:
        """Return (start, end, slug) for each term, linking each slug only once."""
        found, seen = [], set()
        for start, end, phrase in self.matcher.find_all(text):
            slug = self.alias_to_slug[phrase]
            if slug in seen:
                continue
            seen.add(slug)
            found.append((start, end, slug))
        return found

    def slugs_in(self, text: str) -> list[str]:
        return [slug for _, _, slug in self.find(text)]
