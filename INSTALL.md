# Install

Run one command from this folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Default install target:

- `%CODEX_HOME%\skills\memory-manager` if `CODEX_HOME` is set
- otherwise `~/.codex/skills/memory-manager`

Optional custom target:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -TargetSkillsDir "C:\path\to\skills"
```

