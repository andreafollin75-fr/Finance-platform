"""Remove duplicate articles and group articles about the same story.

Step 1, exact duplicates: two entries with the same canonical URL (tracking
parameters removed) are the same article. We keep one.

Step 2, similar stories: two articles are put in the same "story" when
- their titles share enough meaningful words (Jaccard similarity of the
  word sets >= SIMILARITY_THRESHOLD), and
- they were published within MAX_HOURS_APART of each other.
Groups are built transitively (if A~B and B~C, then A, B and C are one story).
"""

from __future__ import annotations

import re
from datetime import datetime

SIMILARITY_THRESHOLD = 0.5
MAX_HOURS_APART = 48
MIN_WORDS = 3  # very short titles are never grouped, to avoid false matches

STOPWORDS = set(
    """a an the and or but of to in on at for from by with as is are was were be been
    it its this that these those than then over after before amid into up down out
    about new says said say will would could can may might has have had not no yes
    how why what when who which while more most less least vs via us his her their
    our your we you they he she i""".split()
)
WORD_RE = re.compile(r"[a-z0-9]+(?:['’][a-z]+)?")


def title_words(title: str) -> frozenset[str]:
    words = set()
    for w in WORD_RE.findall(title.lower()):
        w = w.replace("’", "'").split("'")[0]
        if w in STOPWORDS or len(w) < 2:
            continue
        # Very light stemming: "rates" -> "rate", "cuts" -> "cut".
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        words.add(w)
    return frozenset(words)


def similarity(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def remove_exact_duplicates(articles: list[dict]) -> list[dict]:
    """Keep the first article seen for each id (the id is a hash of the canonical URL)."""
    seen: dict[str, dict] = {}
    for art in articles:
        if art["id"] not in seen:
            seen[art["id"]] = art
    return list(seen.values())


def _hours_apart(a: dict, b: dict) -> float:
    ta = datetime.fromisoformat(a["published"])
    tb = datetime.fromisoformat(b["published"])
    return abs((ta - tb).total_seconds()) / 3600


def group_stories(articles: list[dict]) -> list[dict]:
    """Group similar articles into stories.

    Returns a list of stories. Each story has the earliest article as "lead"
    and the other articles under "related", newest stories first.
    """
    n = len(articles)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    words = [title_words(a["title"]) for a in articles]
    for i in range(n):
        if len(words[i]) < MIN_WORDS:
            continue
        for j in range(i + 1, n):
            if len(words[j]) < MIN_WORDS:
                continue
            if similarity(words[i], words[j]) >= SIMILARITY_THRESHOLD and _hours_apart(articles[i], articles[j]) <= MAX_HOURS_APART:
                parent[find(j)] = find(i)

    groups: dict[int, list[dict]] = {}
    for i, art in enumerate(articles):
        groups.setdefault(find(i), []).append(art)

    stories = []
    for members in groups.values():
        members.sort(key=lambda a: a["published"])
        lead, related = members[0], members[1:]
        themes = sorted({t for a in members for t in a["themes"]})
        sources = sorted({a["source"] for a in members})
        stories.append(
            {
                "id": lead["id"],
                "lead": lead,
                "related": related,
                "themes": themes,
                "sources": sources,
                "first_published": lead["published"],
                "last_published": members[-1]["published"],
            }
        )
    stories.sort(key=lambda s: s["last_published"], reverse=True)
    return stories
