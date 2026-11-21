"""Small helper to find words and phrases in text.

Rule used everywhere (classification and glossary detection):
- a phrase written in lowercase matches in any case ("inflation" matches "Inflation");
- a phrase that contains a capital letter matches that exact case only
  ("Fed" matches "Fed" but not "fed up"; "US" does not match "us").
Matches never start or end inside a word ("rate" does not match "pirate").
"""

from __future__ import annotations

import re


def phrase_pattern(phrase: str) -> re.Pattern:
    flags = 0 if any(c.isupper() for c in phrase) else re.IGNORECASE
    # Spaces in a phrase match any run of whitespace.
    body = r"\s+".join(re.escape(part) for part in phrase.split())
    return re.compile(rf"(?<![\w]){body}(?![\w])", flags)


class PhraseMatcher:
    """Find which phrases of a list occur in a text."""

    def __init__(self, phrases):
        # Longest phrases first so that "yield curve inversion" wins over "yield curve".
        self.phrases = sorted(set(phrases), key=len, reverse=True)
        self.patterns = [(p, phrase_pattern(p)) for p in self.phrases]

    def contains_any(self, text: str) -> bool:
        return any(pattern.search(text) for _, pattern in self.patterns)

    def find_all(self, text: str) -> list[tuple[int, int, str]]:
        """Return non-overlapping (start, end, phrase) matches, in text order.

        Longer phrases take priority over shorter ones that overlap them.
        """
        taken: list[tuple[int, int, str]] = []
        for phrase, pattern in self.patterns:
            for m in pattern.finditer(text):
                if all(m.end() <= s or m.start() >= e for s, e, _ in taken):
                    taken.append((m.start(), m.end(), phrase))
        return sorted(taken)
