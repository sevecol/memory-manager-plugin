from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from index_store import add_entry, load_index, save_index
from keyword_extract import extract_keywords
from recall_engine import recall, render_recall_result
from summarizer import brief_summary, update_main_memory


def _project_root(path: str | None) -> Path:
    return Path(path).resolve() if path else Path.cwd().resolve()


def _state_path(root: Path) -> Path:
    return root / ".codex" / "memory" / "state.json"


def _memory_paths(root: Path) -> dict[str, Path]:
    base = root / "docs" / "memory"
    return {
        "base": base,
        "main": base / "main.md",
        "index": base / "index.json",
        "detail_dir": base / "detail",
    }


def _default_state() -> dict:
    return {
        "enabled": False,
        "auto_load_main_on_start": True,
        "auto_save_on_quit": True,
        "auto_recall_keywords": True,
        "updated_at": None,
    }


def _load_state(path: Path) -> dict:
    if not path.exists():
        return _default_state()
    data = json.loads(path.read_text(encoding="utf-8"))
    merged = _default_state()
    merged.update(data)
    return merged


def _save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_on(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    paths = _memory_paths(root)
    paths["detail_dir"].mkdir(parents=True, exist_ok=True)
    state_path = _state_path(root)
    state = _load_state(state_path)
    state["enabled"] = True
    _save_state(state_path, state)
    print(f"Memory mode enabled for project: {root}")
    return 0


def cmd_off(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    state_path = _state_path(root)
    state = _load_state(state_path)
    state["enabled"] = False
    _save_state(state_path, state)
    print(f"Memory mode disabled for project: {root}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    state = _load_state(_state_path(root))
    paths = _memory_paths(root)
    print(json.dumps({"project": str(root), "state": state, "paths": {k: str(v) for k, v in paths.items()}}, ensure_ascii=False, indent=2))
    return 0


def _read_note(args: argparse.Namespace) -> str:
    if args.note:
        return args.note
    if args.from_file:
        return Path(args.from_file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        data = sys.stdin.read().strip()
        if data:
            return data
    raise ValueError("No note provided. Use --note, --from-file, or pipe stdin.")


def cmd_sync(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    state = _load_state(_state_path(root))
    if not state.get("enabled", False) and not args.force:
        print("Memory mode is off. Use 'on' first or pass --force.")
        return 1

    note_text = _read_note(args)
    paths = _memory_paths(root)
    paths["detail_dir"].mkdir(parents=True, exist_ok=True)
    topic = args.topic or "session-note"
    now = datetime.now()
    entry_id = now.strftime("%Y%m%d-%H%M%S") + "-" + uuid4().hex[:8]
    keywords = (
        [k.strip().lower() for k in args.keywords.split(",") if k.strip()]
        if args.keywords
        else extract_keywords(f"{topic} {note_text}", limit=args.keyword_limit)
    )
    summary = brief_summary(note_text, max_chars=args.summary_chars)
    detail_file = paths["detail_dir"] / f"{entry_id}-{topic.replace(' ', '-').lower()}.md"
    detail_rel = detail_file.relative_to(root).as_posix()
    detail_content = (
        f"# Detail Memory\n\n"
        f"- id: {entry_id}\n"
        f"- topic: {topic}\n"
        f"- timestamp: {now.isoformat(timespec='seconds')}\n"
        f"- keywords: {', '.join(keywords)}\n\n"
        f"## Full Detail\n\n{note_text}\n"
    )
    detail_file.write_text(detail_content, encoding="utf-8")

    index_data = load_index(paths["index"])
    entry = {
        "id": entry_id,
        "topic": topic,
        "timestamp": now.isoformat(timespec="seconds"),
        "keywords": keywords,
        "summary": summary,
        "detail_path": detail_rel,
    }
    add_entry(index_data, entry)
    save_index(paths["index"], index_data)
    update_main_memory(
        paths["main"],
        topic=topic,
        keywords=keywords,
        detail_path=detail_rel,
        summary_text=summary,
    )
    print(f"Synced memory entry: {entry_id}")
    print(f"Detail: {detail_rel}")
    return 0


def cmd_recall(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    paths = _memory_paths(root)
    index_data = load_index(paths["index"])
    entries = recall(index_data, args.query, max_results=args.max_results)
    print(render_recall_result(root, entries))
    return 0


def cmd_preload(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    state = _load_state(_state_path(root))
    if not state.get("enabled", False):
        print("Memory mode is disabled.")
        return 0
    main_path = _memory_paths(root)["main"]
    if not main_path.exists():
        print("Main memory file not found.")
        return 0
    print(main_path.read_text(encoding="utf-8"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project-scoped memory manager")
    parser.add_argument("--project", help="Target project root path")
    sub = parser.add_subparsers(dest="command", required=True)

    p_on = sub.add_parser("on", help="Enable memory mode for project")
    p_on.set_defaults(func=cmd_on)

    p_off = sub.add_parser("off", help="Disable memory mode for project")
    p_off.set_defaults(func=cmd_off)

    p_status = sub.add_parser("status", help="Show memory mode status")
    p_status.set_defaults(func=cmd_status)

    p_sync = sub.add_parser("sync", help="Save note to detail memory and index")
    p_sync.add_argument("--note", help="Inline note text")
    p_sync.add_argument("--from-file", help="Read note text from file")
    p_sync.add_argument("--topic", help="Topic label")
    p_sync.add_argument("--keywords", help="Comma separated keyword list")
    p_sync.add_argument("--keyword-limit", type=int, default=16)
    p_sync.add_argument("--summary-chars", type=int, default=220)
    p_sync.add_argument("--force", action="store_true", help="Sync even when memory mode is off")
    p_sync.set_defaults(func=cmd_sync)

    p_recall = sub.add_parser("recall", help="Recall detail notes by keyword query")
    p_recall.add_argument("--query", required=True, help="Query text")
    p_recall.add_argument("--max-results", type=int, default=5)
    p_recall.set_defaults(func=cmd_recall)

    p_preload = sub.add_parser("preload", help="Print main memory for startup preload")
    p_preload.set_defaults(func=cmd_preload)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
