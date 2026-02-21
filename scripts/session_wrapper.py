from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


def _script_dir() -> Path:
    return Path(__file__).resolve().parent


def _memory_manager_cmd(project: str | None, subcommand: list[str]) -> list[str]:
    cmd = [sys.executable, str(_script_dir() / "memory_manager.py")]
    if project:
        cmd.extend(["--project", project])
    cmd.extend(subcommand)
    return cmd


def cmd_start(args: argparse.Namespace) -> int:
    preload_cmd = _memory_manager_cmd(args.project, ["preload"])
    preload = subprocess.run(preload_cmd, capture_output=True, text=True)
    if preload.stdout.strip():
        print("=== MEMORY PRELOAD ===")
        print(preload.stdout.strip())
        print("======================")

    codex_cmd = shlex.split(args.codex_cmd)
    return subprocess.call(codex_cmd)


def cmd_quit_sync(args: argparse.Namespace) -> int:
    text = Path(args.from_file).read_text(encoding="utf-8") if args.from_file else args.note
    if not text:
        print("No text provided for quit sync.")
        return 1
    sync_cmd = _memory_manager_cmd(args.project, ["sync", "--topic", args.topic, "--note", text])
    return subprocess.call(sync_cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Session wrapper for memory manager")
    parser.add_argument("--project", help="Target project root path")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="Preload memory then launch Codex")
    p_start.add_argument("--codex-cmd", default="codex", help="Codex launch command")
    p_start.set_defaults(func=cmd_start)

    p_sync = sub.add_parser("quit-sync", help="Sync memory on session quit")
    p_sync.add_argument("--note", help="Session summary text")
    p_sync.add_argument("--from-file", help="Read summary from file")
    p_sync.add_argument("--topic", default="session-quit")
    p_sync.set_defaults(func=cmd_quit_sync)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

