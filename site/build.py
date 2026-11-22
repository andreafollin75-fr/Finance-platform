"""Build the static website into dist/ from data/ (news) and content/ (glossary).

Usage:  python site/build.py
        BASE_PATH=/Finance-platform/ python site/build.py   (when served from a sub-folder,
                                                              as on GitHub Pages project sites)
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.briefing import HALF_LIFE_HOURS, MAX_PER_SOURCE, OFFICIAL_BONUS, THEME_BONUS, TOP_N, WINDOW_HOURS  # noqa: E402
from pipeline.config import DATA_DIR, THEMES  # noqa: E402
from pipeline.glossary import TermDetector, load_glossary  # noqa: E402

SITE_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
SITE_NAME = "Finance Explained"
DISCLAIMER = "Educational and informational content only. This site does not provide investment advice."


def read_json(name: str, default):
    try:
        return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


class TermLinker:
    """Turns plain text into HTML where glossary terms link to their definition."""

    def __init__(self, glossary: list[dict], base: str):
        self.detector = TermDetector(glossary)
        self.by_slug = {e["slug"]: e for e in glossary}
        self.base = base
        self.counter = 0

    def __call__(self, text: str) -> Markup:
        out, pos = [], 0
        for start, end, slug in self.detector.find(text):
            entry = self.by_slug[slug]
            self.counter += 1
            tip_id = f"tip{self.counter}"
            out.append(escape(text[pos:start]))
            out.append(
                Markup(
                    '<span class="term-wrap"><a class="term" href="{href}" aria-describedby="{id}">{word}</a>'
                    '<span class="tip" role="tooltip" id="{id}"><strong>{title}</strong> {short}</span></span>'
                ).format(href=f"{self.base}glossary/{slug}/", id=tip_id, word=text[start:end], title=entry["title"], short=entry["short"])
            )
            pos = end
        out.append(escape(text[pos:]))
        return Markup("").join(out)


def format_date(iso: str) -> str:
    dt = datetime.fromisoformat(iso).astimezone(timezone.utc)
    return dt.strftime("%d %b %Y, %H:%M UTC")


def build(base: str = "/") -> Path:
    if not base.endswith("/"):
        base += "/"
    glossary = load_glossary()
    for entry in glossary:
        entry["html"] = Markup(markdown.markdown(entry["body"]))
    by_slug = {e["slug"]: e for e in glossary}

    news = read_json("news.json", {"meta": {}, "stories": []})
    briefing = read_json("briefing.json", {"meta": {}, "stories": []})
    status = read_json("sources_status.json", {})

    env = Environment(loader=FileSystemLoader(SITE_DIR / "templates"), autoescape=select_autoescape(["html", "xml"]))
    env.filters["date"] = format_date
    linker = TermLinker(glossary, base)
    env.filters["terms"] = linker
    env.filters["concepts"] = lambda text: [by_slug[slug] for slug in linker.detector.slugs_in(text)]
    env.globals.update(
        base=base,
        site_name=SITE_NAME,
        disclaimer=DISCLAIMER,
        themes=THEMES,
        generated_at=news["meta"].get("generated_at"),
        build_time=datetime.now(timezone.utc).isoformat(),
    )

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    shutil.copytree(SITE_DIR / "static", DIST_DIR / "static")

    def render(template: str, path: str, **context):
        target = DIST_DIR / path / "index.html" if path else DIST_DIR / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(env.get_template(template).render(**context), encoding="utf-8")

    render("news.html", "", page="news", stories=news["stories"][:300])
    render(
        "briefing.html",
        "briefing",
        page="briefing",
        stories=briefing["stories"],
        rules=dict(window=WINDOW_HOURS, top=TOP_N, per_source=MAX_PER_SOURCE, half_life=HALF_LIFE_HOURS, theme_bonus=THEME_BONUS, official_bonus=OFFICIAL_BONUS),
    )
    render("glossary_index.html", "glossary", page="glossary", entries=glossary)
    for entry in glossary:
        related = [by_slug[r] for r in entry["related"]]
        render("glossary_entry.html", f"glossary/{entry['slug']}", page="glossary", entry=entry, related=related)
    render("about.html", "about", page="about", status=dict(sorted(status.items())), glossary_count=len(glossary))
    (DIST_DIR / "404.html").write_text(env.get_template("404.html").render(page="404"), encoding="utf-8")
    # Machine-readable copies of the data, handy for anyone reusing the site.
    (DIST_DIR / "data").mkdir()
    for name in ("news.json", "briefing.json"):
        if (DATA_DIR / name).exists():
            shutil.copy(DATA_DIR / name, DIST_DIR / "data" / name)
    print(f"Built {len(glossary)} glossary pages and {len(news['stories'])} stories into {DIST_DIR}")
    return DIST_DIR


if __name__ == "__main__":
    build(os.environ.get("BASE_PATH", "/"))
