---
name: memory-manager
description: Persistent project-scoped memory management for Codex sessions. Use when users want automatic or semi-automatic memory workflows, including turning memory mode on/off per directory, saving session details on quit, extracting keywords, maintaining a short main memory file, indexing detail notes, and recalling relevant detail by keyword during later conversations.
---

# Memory Manager

Use this skill to manage persistent memory files inside the active project.

## Commands

Run from the project root:

```powershell
python <skill-root>/scripts/memory_manager.py on
python <skill-root>/scripts/memory_manager.py off
python <skill-root>/scripts/memory_manager.py status
python <skill-root>/scripts/memory_manager.py sync --note "text to save"
python <skill-root>/scripts/memory_manager.py recall --query "keyword"
```

`on` enables project memory mode by writing `.codex/memory/state.json`.

`sync` writes:
- `docs/memory/detail/*.md` for full detail
- `docs/memory/index.json` for keyword index
- `docs/memory/main.md` for concise long-term memory

## Auto workflow guidance

If the host can run startup/quit hooks:

1. On startup: read state, then preload `docs/memory/main.md`.
2. During conversation: call `recall` on high-confidence keywords.
3. On quit: call `sync` with conversation summary text.

If hooks are unavailable, call the same commands manually.

