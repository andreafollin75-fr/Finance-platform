from pipeline.dedupe import group_stories, remove_exact_duplicates, similarity, title_words


def art(id, title, source="A", published="2026-11-20T10:00:00+00:00", themes=("markets",)):
    return {"id": id, "title": title, "source": source, "published": published, "themes": list(themes), "url": f"https://x/{id}"}


def test_exact_duplicates_are_removed():
    items = [art("1", "Stocks rise"), art("1", "Stocks rise (copy)"), art("2", "Bonds fall")]
    result = remove_exact_duplicates(items)
    assert [a["id"] for a in result] == ["1", "2"]
    assert result[0]["title"] == "Stocks rise"  # the first one is kept


def test_title_words_ignore_case_stopwords_and_plurals():
    assert title_words("The Fed Cuts Rates") == title_words("fed cut rate")


def test_similar_titles_from_different_sources_are_grouped():
    items = [
        art("1", "Fed cuts interest rates by a quarter point", source="A", published="2026-11-20T18:00:00+00:00"),
        art("2", "Federal Reserve: Fed cuts interest rates by quarter point", source="B", published="2026-11-20T19:00:00+00:00"),
        art("3", "Oil prices jump after supply disruption", source="C"),
    ]
    stories = group_stories(items)
    assert len(stories) == 2
    fed = next(s for s in stories if len(s["related"]) == 1)
    assert fed["lead"]["id"] == "1"  # earliest article leads the story
    assert fed["sources"] == ["A", "B"]


def test_similar_titles_far_apart_in_time_are_not_grouped():
    items = [
        art("1", "Fed cuts interest rates by a quarter point", published="2026-11-01T18:00:00+00:00"),
        art("2", "Fed cuts interest rates by a quarter point", published="2026-11-20T18:00:00+00:00"),
    ]
    assert len(group_stories(items)) == 2


def test_different_stories_are_not_grouped():
    items = [art("1", "ECB keeps deposit rate unchanged"), art("2", "Apple shares rise after earnings beat")]
    assert len(group_stories(items)) == 2


def test_short_titles_are_never_grouped():
    items = [art("1", "Markets wrap"), art("2", "Markets wrap")]
    assert len(group_stories(items)) == 2


def test_similarity_bounds():
    a = title_words("gold hits record high")
    assert similarity(a, a) == 1.0
    assert similarity(a, frozenset()) == 0.0
