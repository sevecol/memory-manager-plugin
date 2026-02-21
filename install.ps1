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

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = $scriptRoot

$codexHomeResolved = Get-CodexHome -Override $CodexHome
if ($TargetSkillsDir -and $TargetSkillsDir.Trim().Length -gt 0) {
  $skillsDir = $TargetSkillsDir
} else {
  $skillsDir = Join-Path $codexHomeResolved "skills"
}

$dest = Join-Path $skillsDir $SkillName

New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
if (Test-Path -LiteralPath $dest) {
  Remove-Item -LiteralPath $dest -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$itemsToCopy = @(
  "SKILL.md",
  "agents",
  "assets",
  "references",
  "scripts",
  "start-codex-with-memory.ps1"
)

foreach ($item in $itemsToCopy) {
  $src = Join-Path $sourceRoot $item
  if (-not (Test-Path -LiteralPath $src)) {
    throw "Missing required source item: $item"
  }
  Copy-Item -LiteralPath $src -Destination $dest -Recurse -Force
}

Write-Host "Installed skill '$SkillName' to: $dest"
Write-Host "Use from project root:"
Write-Host "  python `"$dest\scripts\memory_manager.py`" on"
