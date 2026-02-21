param(
  [string]$ProjectDir = "",
  [string]$CodexCmd = "codex.cmd",
  [string[]]$CodexArgs = @(),
  [string]$InitialPrompt = "",
  [string]$Topic = "session-auto",
  [int]$PreloadMaxChars = 6000,
  [switch]$DisableAutoEnable,
  [switch]$DisableAutoSync,
  [switch]$DisablePreloadMain
)

$ErrorActionPreference = "Stop"

function Resolve-ProjectDir {
  param([string]$InputPath)
  if ($InputPath -and $InputPath.Trim().Length -gt 0) {
    return (Resolve-Path -LiteralPath $InputPath).Path
  }
  return (Get-Location).Path
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$memoryManager = Join-Path $scriptRoot "scripts\memory_manager.py"
$autoSync = Join-Path $scriptRoot "scripts\auto_sync_from_sessions.py"

if (-not (Test-Path -LiteralPath $memoryManager)) {
  throw "memory_manager.py not found: $memoryManager"
}
if (-not (Test-Path -LiteralPath $autoSync)) {
  throw "auto_sync_from_sessions.py not found: $autoSync"
}

$project = Resolve-ProjectDir -InputPath $ProjectDir
$sessionStart = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

if (-not $DisableAutoEnable) {
  & python $memoryManager --project $project on | Out-Host
}

$preloadPrompt = ""
if (-not $DisablePreloadMain) {
  $mainPath = Join-Path $project "docs\memory\main.md"
  if (Test-Path -LiteralPath $mainPath) {
    $mainText = Get-Content -LiteralPath $mainPath -Raw -Encoding utf8
    if ($mainText.Length -gt $PreloadMaxChars) {
      $mainText = $mainText.Substring($mainText.Length - $PreloadMaxChars)
    }
    $preloadPrompt = @"
Read and retain this project memory summary for follow-up questions. Do not summarize it now; wait for my next request.
[MEMORY_MAIN_BEGIN]
$mainText
[MEMORY_MAIN_END]
"@
  }
}

if ($InitialPrompt -and $InitialPrompt.Trim().Length -gt 0) {
  if ($preloadPrompt) {
    $preloadPrompt = $preloadPrompt + "`n`n" + $InitialPrompt
  } else {
    $preloadPrompt = $InitialPrompt
  }
}

Write-Host "Starting Codex in project: $project"
$launchArgs = @("-C", $project) + $CodexArgs
if ($preloadPrompt) {
  $launchArgs += $preloadPrompt
}
& $CodexCmd @launchArgs
$codexExit = $LASTEXITCODE

if (-not $DisableAutoSync) {
  Write-Host "Auto-syncing memory from latest session log..."
  & python $autoSync --project $project --since-epoch $sessionStart --topic $Topic | Out-Host
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Auto-sync did not find a valid dialog. You can run manual sync later."
  }
}

exit $codexExit
