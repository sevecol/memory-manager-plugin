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
    "http",
    "https",
    "www",
    "com",
    "org",
    "net",
    "file",
    "files",
    "path",
    "paths",
    "use",
    "users",
    "user",
    "skill",
    "skills",
    "instructions",
    "description",
    "docs",
    "codex",
    "github",
    "session",
    "install",
    "list",
    "only",
    "when",
    "can",
}


def extract_keywords(text: str, limit: int = 8) -> list[str]:
    # English-like tokens
    en_tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
    en_filtered = [t for t in en_tokens if t not in _STOPWORDS and not t.isdigit()]

    # Chinese runs (2+ chars). For long runs, split by common particles.
    zh_runs = re.findall(r"[\u4e00-\u9fff]{2,24}", text)
    zh_tokens: list[str] = []
    for run in zh_runs:
        if 2 <= len(run) <= 6:
            zh_tokens.append(run)
            continue
        parts = re.split(r"[的了在是有和与及并对把将就都而我你他她它们很也还这那个吗呢吧啊]", run)
        for part in parts:
            if 2 <= len(part) <= 6:
                zh_tokens.append(part)

    counts = Counter(en_filtered + zh_tokens)
    return [word for word, _ in counts.most_common(limit)]
