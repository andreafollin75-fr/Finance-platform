"""Assign themes to articles.

Every article starts with the default themes of its source (from sources.yml).
Keyword rules below then add extra themes when the title or excerpt mentions
them. Themes are only ever added, never removed.
"""

from __future__ import annotations

from .textmatch import PhraseMatcher

THEME_KEYWORDS = {
    "europe": [
        "Europe", "European", "EU", "eurozone", "euro area", "euro zone", "ECB", "Lagarde",
        "Germany", "German", "France", "French", "Italy", "Italian", "Spain", "Spanish",
        "Netherlands", "Dutch", "UK", "Britain", "British", "Bank of England", "BoE",
        "Brussels", "Frankfurt", "London", "FTSE", "DAX", "CAC 40", "Stoxx", "sterling",
        "Bund", "Bunds", "gilt", "gilts", "OAT", "OATs",
    ],
    "us": [
        "U.S.", "US", "USA", "United States", "America", "American", "Fed", "Federal Reserve",
        "FOMC", "Powell", "Wall Street", "S&P 500", "Nasdaq", "Dow", "Dow Jones",
        "Treasury", "Treasuries", "Washington", "White House", "Congress", "SEC",
    ],
    "macro": [
        "inflation", "deflation", "CPI", "PCE", "GDP", "recession", "unemployment",
        "jobless", "payrolls", "jobs report", "labour market", "labor market", "wages",
        "interest rate", "interest rates", "rate cut", "rate cuts", "rate hike", "rate hikes",
        "central bank", "central banks", "monetary policy", "fiscal", "budget deficit",
        "public debt", "national debt", "tariff", "tariffs", "trade deficit", "trade surplus",
        "economic growth", "economy", "PMI", "ECB", "Fed", "FOMC", "Bank of England",
        "quantitative easing", "quantitative tightening",
    ],
    "markets": [
        "stock", "stocks", "shares", "equities", "equity market", "S&P 500", "Nasdaq",
        "Dow", "FTSE", "DAX", "Stoxx", "bond", "bonds", "yield", "yields", "Treasuries",
        "dollar", "euro", "yen", "sterling", "currency", "currencies", "forex", "FX",
        "oil", "crude", "Brent", "WTI", "gold", "commodities", "commodity", "rally",
        "sell-off", "selloff", "earnings", "IPO", "futures", "VIX", "volatility", "investors",
    ],
}

_MATCHERS = {theme: PhraseMatcher(words) for theme, words in THEME_KEYWORDS.items()}


def classify_text(text: str, base_themes=()) -> list[str]:
    """Return the sorted list of themes for a piece of text."""
    themes = set(base_themes)
    for theme, matcher in _MATCHERS.items():
        if matcher.contains_any(text):
            themes.add(theme)
    return sorted(themes)


def classify_article(article: dict) -> dict:
    text = f"{article['title']} {article.get('excerpt', '')}"
    article["themes"] = classify_text(text, article.get("themes", []))
    return article
