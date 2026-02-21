# Install

Run one command from this folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Remote bootstrap install (download from GitHub then install):

```powershell
powershell -ExecutionPolicy Bypass -Command "iwr https://raw.githubusercontent.com/sevecol/memory-manager-plugin/main/bootstrap-install.ps1 -UseBasicParsing | iex"
```

Start Codex with auto memory sync on exit:

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\.codex\skills\memory-manager\start-codex-with-memory.ps1" -ProjectDir "C:\path\to\project"
```

Behavior:

- auto enable memory mode for the project (`on`)
- start Codex CLI in that project
- when Codex exits, parse latest `~/.codex/sessions/*.jsonl`
- extract user/assistant dialog and run `sync`

Default install target:

- `%CODEX_HOME%\skills\memory-manager` if `CODEX_HOME` is set
- otherwise `~/.codex/skills/memory-manager`

Optional custom target:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -TargetSkillsDir "C:\path\to\skills"
```

Uninstall:

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1
```

Remote bootstrap options:

```powershell
powershell -ExecutionPolicy Bypass -Command "$p=Join-Path $env:TEMP 'bootstrap-install.ps1'; iwr https://raw.githubusercontent.com/sevecol/memory-manager-plugin/main/bootstrap-install.ps1 -UseBasicParsing -OutFile $p; powershell -ExecutionPolicy Bypass -File $p -RepoUrl 'https://github.com/sevecol/memory-manager-plugin.git' -Ref 'main'; Remove-Item $p -Force"
```
