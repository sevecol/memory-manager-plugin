from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_index(index_path: Path) -> dict[str, Any]:
    if not index_path.exists():
        return {"entries": [], "keywords": {}}
    return json.loads(index_path.read_text(encoding="utf-8"))


def save_index(index_path: Path, index_data: dict[str, Any]) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(index_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add_entry(index_data: dict[str, Any], entry: dict[str, Any]) -> None:
    index_data.setdefault("entries", []).append(entry)
    keyword_map = index_data.setdefault("keywords", {})
    for keyword in entry.get("keywords", []):
        keyword_map.setdefault(keyword, []).append(entry["id"])

