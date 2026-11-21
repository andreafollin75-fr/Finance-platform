"""Pick the most important stories for the Daily Briefing, without any AI.

Each story from the last WINDOW_HOURS gets a score:

    score = coverage + freshness + theme bonus + official bonus

- coverage:  3 points per distinct source covering the story (counted up to 5 sources).
             A story reported by several outlets is usually more important.
- freshness: up to 5 points, halved every 12 hours (5 when brand new, 2.5 after 12 h...).
- theme bonus: +2 if the story is about macro & central banks, +1 if about markets.
- official bonus: +2 if a central bank, regulator or statistics office published it.

The TOP_N stories with the highest score are shown, with at most
MAX_PER_SOURCE stories led by the same source so one feed cannot fill the page.
"""

from __future__ import annotations

from datetime import datetime

WINDOW_HOURS = 36
TOP_N = 10
MAX_PER_SOURCE = 3
HALF_LIFE_HOURS = 12
THEME_BONUS = {"macro": 2.0, "markets": 1.0}
OFFICIAL_BONUS = 2.0


def score_story(story: dict, now: datetime) -> dict:
    """Return the score and its parts, so the site can explain each ranking."""
    age_hours = max(0.0, (now - datetime.fromisoformat(story["last_published"])).total_seconds() / 3600)
    coverage = 3.0 * min(len(story["sources"]), 5)
    freshness = 5.0 * 0.5 ** (age_hours / HALF_LIFE_HOURS)
    theme = max((THEME_BONUS.get(t, 0.0) for t in story["themes"]), default=0.0)
    members = [story["lead"], *story["related"]]
    official = OFFICIAL_BONUS if any(a.get("source_kind") == "official" for a in members) else 0.0
    total = coverage + freshness + theme + official
    return {
        "total": round(total, 2),
        "coverage": round(coverage, 2),
        "freshness": round(freshness, 2),
        "theme": theme,
        "official": official,
        "age_hours": round(age_hours, 1),
    }


def build_briefing(stories: list[dict], now: datetime) -> list[dict]:
    candidates = []
    for story in stories:
        s = score_story(story, now)
        if s["age_hours"] <= WINDOW_HOURS:
            candidates.append({**story, "score": s})
    candidates.sort(key=lambda st: (st["score"]["total"], st["last_published"]), reverse=True)

    picked, per_source = [], {}
    for story in candidates:
        src = story["lead"]["source"]
        if per_source.get(src, 0) >= MAX_PER_SOURCE:
            continue
        per_source[src] = per_source.get(src, 0) + 1
        picked.append(story)
        if len(picked) == TOP_N:
            break
    return picked
