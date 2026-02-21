from __future__ import annotations

import re
from collections import Counter

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "with",
    "then",
    "than",
    "you",
    "your",
    "we",
    "our",
    "they",
    "them",
}


def extract_keywords(text: str, limit: int = 8) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9_-]{3,}", text.lower())
    filtered = [t for t in tokens if t not in _STOPWORDS and not t.isdigit()]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(limit)]

