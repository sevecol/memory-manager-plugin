# Config

Project state file:

- `.codex/memory/state.json`

Generated memory files:

- `docs/memory/main.md` (short long-term summary)
- `docs/memory/index.json` (keyword to detail id mapping)
- `docs/memory/detail/*.md` (full detail entries)

Recommended defaults:

- `auto_load_main_on_start: true`
- `auto_save_on_quit: true`
- `auto_recall_keywords: true`

Operational notes:

- Keep `main.md` concise.
- Keep full details in `detail/`.
- Use `recall --query` to fetch only relevant details.

