from pipeline.glossary import TermDetector, load_glossary

GLOSSARY = load_glossary()
DETECT = TermDetector(GLOSSARY)


def test_glossary_has_at_least_40_complete_entries():
    assert len(GLOSSARY) >= 40
    for entry in GLOSSARY:
        assert entry["short"] and entry["aliases"], entry["slug"]


def test_related_links_point_to_existing_entries():
    slugs = {e["slug"] for e in GLOSSARY}
    for entry in GLOSSARY:
        assert set(entry["related"]) <= slugs


def test_each_alias_belongs_to_only_one_entry():
    seen = {}
    for entry in GLOSSARY:
        for alias in entry["aliases"]:
            assert alias not in seen, f"{alias!r} is used by {seen[alias]} and {entry['slug']}"
            seen[alias] = entry["slug"]


def test_terms_are_detected_in_headlines():
    assert DETECT.slugs_in("Fed holds rates as inflation cools") == ["federal-reserve", "inflation"]
    assert DETECT.slugs_in("Brent crude falls below $70") == ["oil"]


def test_longest_term_wins():
    assert DETECT.slugs_in("Inverted yield curve flashes warning") == ["yield-curve-inversion"]
    assert DETECT.slugs_in("The yield curve steepens") == ["yield-curve"]


def test_each_term_is_linked_once():
    assert DETECT.slugs_in("Inflation, inflation, inflation") == ["inflation"]


def test_no_false_positive_on_common_words():
    assert DETECT.slugs_in("Fans fed up with ticket prices") == []
    assert DETECT.slugs_in("The goldfish was golden") == []


def test_positions_point_to_the_matched_text():
    text = "Euro Stoxx 50 climbs"
    [(start, end, slug)] = DETECT.find(text)
    assert text[start:end] == "Euro Stoxx 50" and slug == "stock-index"
