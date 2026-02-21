from __future__ import annotations

from datetime import datetime
from pathlib import Path


def brief_summary(text: str, max_chars: int = 220) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3] + "..."


def update_main_memory(
    main_path: Path,
    *,
    topic: str,
    keywords: list[str],
    detail_path: str,
    summary_text: str,
) -> None:
    main_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = (
        f"- {timestamp} | {topic} | keywords: {', '.join(keywords)} | "
        f"detail: {detail_path} | summary: {summary_text}\n"
    )
    if not main_path.exists():
        header = "# Main Memory\n\nShort, stable memory records. Full details live in docs/memory/detail.\n\n"
        main_path.write_text(header + line, encoding="utf-8")
        return
    with main_path.open("a", encoding="utf-8") as f:
        f.write(line)

