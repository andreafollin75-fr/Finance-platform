from pipeline.classify import classify_text
from pipeline.textmatch import PhraseMatcher


def test_source_themes_are_kept():
    assert classify_text("Something unrelated happened", ["europe"]) == ["europe"]


def test_keywords_add_themes():
    assert classify_text("ECB raises rates as eurozone inflation climbs") == ["europe", "macro"]
    assert "markets" in classify_text("S&P 500 hits record as tech stocks rally")
    assert "us" in classify_text("S&P 500 hits record as tech stocks rally")


def test_capitalised_keywords_are_case_sensitive():
    # "US" must not match the pronoun "us", and "Fed" must not match "fed up".
    assert "us" not in classify_text("Tell us what you think")
    assert "macro" not in classify_text("Shoppers are fed up with queues")
    assert "us" in classify_text("US jobs report beats forecasts")


def test_lowercase_keywords_match_any_case():
    assert "macro" in classify_text("INFLATION SURPRISE")


def test_no_match_inside_words():
    matcher = PhraseMatcher(["oil"])
    assert not matcher.contains_any("Toil and trouble")
    assert matcher.contains_any("Oil slips")
