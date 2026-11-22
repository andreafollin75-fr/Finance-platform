"""Shared settings and file paths for the pipeline."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CONTENT_DIR = ROOT / "content"
GLOSSARY_DIR = CONTENT_DIR / "glossary"
SOURCES_FILE = Path(__file__).resolve().parent / "sources.yml"

# The themes the site knows about. Keys are used in code and URLs,
# values are the labels shown to readers.
THEMES = {
    "europe": "Europe",
    "us": "United States",
    "macro": "Macro & central banks",
    "markets": "Markets",
}

# An explicit User-Agent so that publishers know who is reading their feeds.
USER_AGENT = (
    "FinancePlatformBot/1.0 (+https://github.com/andreafollin75-fr/Finance-platform; "
    "educational news reader, fetches at most once per hour)"
)

REQUEST_TIMEOUT_SECONDS = 20
# How long articles stay on the site.
KEEP_DAYS = 7
# Maximum excerpt length (we never republish full articles).
EXCERPT_MAX_CHARS = 280


def load_sources(path: Path = SOURCES_FILE) -> list[dict]:
    """Read sources.yml and return only the enabled sources."""
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    sources = []
    for src in config.get("sources", []):
        if not src.get("enabled", True):
            continue
        unknown = set(src.get("themes", [])) - set(THEMES)
        if unknown:
            raise ValueError(f"Unknown theme(s) {unknown} in source {src.get('name')!r}")
        sources.append(src)
    return sources
