from __future__ import annotations

from pathlib import Path
from typing import Any

from keyword_extract import extract_keywords


def recall(index_data: dict[str, Any], query: str, max_results: int = 5) -> list[dict[str, Any]]:
    terms = set(extract_keywords(query, limit=10))
    if not terms:
        terms = {query.strip().lower()}
    scored = []
    entries_by_id = {entry["id"]: entry for entry in index_data.get("entries", [])}
    keyword_map = index_data.get("keywords", {})
    seen = set()
    for term in terms:
        for entry_id in keyword_map.get(term, []):
            if entry_id in seen or entry_id not in entries_by_id:
                continue
            entry = entries_by_id[entry_id]
            overlap = len(terms.intersection(set(entry.get("keywords", []))))
            scored.append((overlap, entry))
            seen.add(entry_id)
    # Fallback: fuzzy text match over topic and summary when keyword index misses.
    if not scored:
        for entry in index_data.get("entries", []):
            haystack = f"{entry.get('topic', '')} {entry.get('summary', '')}".lower()
            score = sum(1 for term in terms if term in haystack)
            if score > 0:
                scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:max_results]]


def render_recall_result(project_root: Path, entries: list[dict[str, Any]]) -> str:
    if not entries:
        return "No memory details found for this query."
    lines = []
    for item in entries:
        rel_path = item.get("detail_path", "")
        detail_path = project_root / rel_path if rel_path else None
        excerpt = item.get("summary", "")
        if detail_path and detail_path.exists():
            text = detail_path.read_text(encoding="utf-8")
            excerpt = " ".join(text.split())[:180]
        lines.append(
            f"- id: {item.get('id')} | topic: {item.get('topic')} | "
            f"keywords: {', '.join(item.get('keywords', []))} | detail: {rel_path} | excerpt: {excerpt}"
        )
    return "\n".join(lines)
