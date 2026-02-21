from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class SessionCandidate:
    path: Path
    mtime: float


def _normalize_path(path: str) -> str:
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


def _iter_session_files(sessions_root: Path) -> Iterable[SessionCandidate]:
    if not sessions_root.exists():
        return []
    files = [p for p in sessions_root.rglob("*.jsonl") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [SessionCandidate(path=p, mtime=p.stat().st_mtime) for p in files]


def _load_lines(path: Path) -> list[dict]:
    lines: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                lines.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
    return lines


def _session_cwd(lines: list[dict]) -> str | None:
    for item in lines[:5]:
        if item.get("type") == "session_meta":
            payload = item.get("payload", {})
            return payload.get("cwd")
    return None


def _extract_message_text(content: list[dict], role: str) -> str:
    text_chunks: list[str] = []
    for part in content:
        ptype = part.get("type")
        if role == "user" and ptype == "input_text":
            text_chunks.append(part.get("text", ""))
        if role == "assistant" and ptype == "output_text":
            text_chunks.append(part.get("text", ""))
    return "\n".join([c for c in text_chunks if c]).strip()


def _extract_dialog(lines: list[dict], max_messages: int) -> list[tuple[str, str]]:
    dialog: list[tuple[str, str]] = []
    for item in lines:
        if item.get("type") != "response_item":
            continue
        payload = item.get("payload", {})
        if payload.get("type") != "message":
            continue
        role = payload.get("role")
        if role not in {"user", "assistant"}:
            continue
        text = _extract_message_text(payload.get("content", []), role)
        if text:
            dialog.append((role, text))
    if max_messages > 0 and len(dialog) > max_messages:
        return dialog[-max_messages:]
    return dialog


def _build_note(dialog: list[tuple[str, str]], max_chars: int) -> str:
    if not dialog:
        return ""
    lines = ["# Session Transcript", ""]
    for role, text in dialog:
        title = "User" if role == "user" else "Assistant"
        lines.append(f"## {title}")
        lines.append("")
        lines.append(text.strip())
        lines.append("")
    note = "\n".join(lines).strip()
    if len(note) > max_chars:
        return note[: max_chars - 3] + "..."
    return note


def _find_latest_session(
    sessions_root: Path,
    project: Path,
    since_epoch: float,
) -> Path | None:
    project_norm = _normalize_path(str(project))
    for candidate in _iter_session_files(sessions_root):
        if candidate.mtime + 5 < since_epoch:
            continue
        lines = _load_lines(candidate.path)
        cwd = _session_cwd(lines)
        if not cwd:
            continue
        if _normalize_path(cwd) == project_norm:
            return candidate.path
    return None


def _run_sync(
    script_dir: Path,
    project: Path,
    topic: str,
    note: str,
    keyword_limit: int,
) -> int:
    manager = script_dir / "memory_manager.py"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write(note)
        tmp_path = tmp.name
    try:
        cmd = [
            sys.executable,
            str(manager),
            "--project",
            str(project),
            "sync",
            "--topic",
            topic,
            "--from-file",
            tmp_path,
            "--keyword-limit",
            str(keyword_limit),
        ]
        return subprocess.call(cmd)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract latest Codex session and sync memory")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--since-epoch", type=float, required=True, help="Session start epoch seconds")
    parser.add_argument("--topic", default="session-auto", help="Memory topic")
    parser.add_argument("--sessions-root", help="Override Codex sessions directory")
    parser.add_argument("--max-messages", type=int, default=80)
    parser.add_argument("--max-chars", type=int, default=12000)
    parser.add_argument("--keyword-limit", type=int, default=24)
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if args.sessions_root:
        sessions_root = Path(args.sessions_root).resolve()
    else:
        sessions_root = Path.home() / ".codex" / "sessions"

    target = _find_latest_session(sessions_root, project, args.since_epoch)
    if not target:
        print("No matching session log found for auto sync.")
        return 1

    lines = _load_lines(target)
    dialog = _extract_dialog(lines, max_messages=args.max_messages)
    note = _build_note(dialog, max_chars=args.max_chars)
    if not note:
        print("Session log found but no user/assistant dialog to sync.")
        return 1

    script_dir = Path(__file__).resolve().parent
    code = _run_sync(script_dir, project, args.topic, note, args.keyword_limit)
    if code == 0:
        print(f"Auto-synced from session: {target}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

