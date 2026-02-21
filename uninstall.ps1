param(
  [string]$SkillName = "memory-manager",
  [string]$CodexHome = "",
  [string]$TargetSkillsDir = ""
)

$ErrorActionPreference = "Stop"

function Get-CodexHome {
  param([string]$Override)
  if ($Override -and $Override.Trim().Length -gt 0) {
    return (Resolve-Path -LiteralPath $Override).Path
  }
  if ($env:CODEX_HOME -and $env:CODEX_HOME.Trim().Length -gt 0) {
    return $env:CODEX_HOME
  }
  return (Join-Path $HOME ".codex")
}

$codexHomeResolved = Get-CodexHome -Override $CodexHome
if ($TargetSkillsDir -and $TargetSkillsDir.Trim().Length -gt 0) {
  $skillsDir = $TargetSkillsDir
} else {
  $skillsDir = Join-Path $codexHomeResolved "skills"
}

$dest = Join-Path $skillsDir $SkillName

if (-not (Test-Path -LiteralPath $dest)) {
  Write-Host "Skill '$SkillName' not found at: $dest"
  exit 0
}

Remove-Item -LiteralPath $dest -Recurse -Force
Write-Host "Uninstalled skill '$SkillName' from: $dest"

