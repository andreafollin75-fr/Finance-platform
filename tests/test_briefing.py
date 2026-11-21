from datetime import datetime, timedelta, timezone

from pipeline.briefing import build_briefing, score_story

NOW = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)


def story(id, sources, hours_ago, themes=("markets",), kind="media"):
    published = (NOW - timedelta(hours=hours_ago)).isoformat()
    lead = {"id": id, "source": sources[0], "source_kind": kind, "published": published}
    related = [{"id": f"{id}-{i}", "source": s, "source_kind": "media", "published": published} for i, s in enumerate(sources[1:])]
    return {"id": id, "lead": lead, "related": related, "sources": sorted(set(sources)), "themes": list(themes), "last_published": published}


def test_more_sources_score_higher():
    one = score_story(story("a", ["A"], 1), NOW)
    three = score_story(story("b", ["A", "B", "C"], 1), NOW)
    assert three["total"] > one["total"]


def test_freshness_halves_every_12_hours():
    assert score_story(story("a", ["A"], 0), NOW)["freshness"] == 5.0
    assert score_story(story("a", ["A"], 12), NOW)["freshness"] == 2.5


def test_official_and_macro_bonuses():
    s = score_story(story("a", ["ECB"], 1, themes=("macro",), kind="official"), NOW)
    assert s["official"] == 2.0 and s["theme"] == 2.0


def test_old_stories_are_excluded_and_list_is_capped():
    stories = [story(str(i), [f"S{i}"], 1) for i in range(20)] + [story("old", ["X", "Y", "Z"], 48)]
    picked = build_briefing(stories, NOW)
    assert len(picked) == 10
    assert "old" not in [s["id"] for s in picked]


def test_one_source_cannot_fill_the_briefing():
    stories = [story(str(i), ["Same"], 1) for i in range(10)]
    assert len(build_briefing(stories, NOW)) == 3
