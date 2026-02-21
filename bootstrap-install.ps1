param(
  [string]$RepoUrl = "https://github.com/sevecol/memory-manager-plugin.git",
  [string]$Ref = "main",
  [string]$SkillName = "memory-manager",
  [string]$CodexHome = "",
  [string]$TargetSkillsDir = "",
  [string]$TempDir = ""
)

$ErrorActionPreference = "Stop"

function Remove-DirSafe {
  param([string]$PathToRemove)
  if ($PathToRemove -and (Test-Path -LiteralPath $PathToRemove)) {
    Remove-Item -LiteralPath $PathToRemove -Recurse -Force
  }
}

function Install-FromPath {
  param([string]$SourcePath)
  $installScript = Join-Path $SourcePath "install.ps1"
  if (-not (Test-Path -LiteralPath $installScript)) {
    throw "install.ps1 not found in: $SourcePath"
  }
  $args = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $installScript,
    "-SkillName", $SkillName
  )
  if ($CodexHome -and $CodexHome.Trim().Length -gt 0) {
    $args += @("-CodexHome", $CodexHome)
  }
  if ($TargetSkillsDir -and $TargetSkillsDir.Trim().Length -gt 0) {
    $args += @("-TargetSkillsDir", $TargetSkillsDir)
  }
  & powershell @args
}

$workRoot = if ($TempDir -and $TempDir.Trim().Length -gt 0) {
  New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
  (Resolve-Path -LiteralPath $TempDir).Path
} else {
  Join-Path ([System.IO.Path]::GetTempPath()) ("memory-manager-bootstrap-" + [guid]::NewGuid().ToString("N"))
}

New-Item -ItemType Directory -Force -Path $workRoot | Out-Null
$repoDir = Join-Path $workRoot "repo"
$zipPath = Join-Path $workRoot "repo.zip"
$extractDir = Join-Path $workRoot "extract"

try {
  $git = Get-Command git -ErrorAction SilentlyContinue
  if ($git) {
    Write-Host "Cloning repository..."
    & git clone --depth 1 --branch $Ref $RepoUrl $repoDir | Out-Host
    Install-FromPath -SourcePath $repoDir
  } else {
    $archiveUrl = $RepoUrl -replace "\.git$", ""
    $archiveUrl = "$archiveUrl/archive/refs/heads/$Ref.zip"
    Write-Host "Downloading archive..."
    Invoke-WebRequest -Uri $archiveUrl -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
    $candidate = Get-ChildItem -LiteralPath $extractDir -Directory | Select-Object -First 1
    if (-not $candidate) {
      throw "Could not find extracted repository directory."
    }
    Install-FromPath -SourcePath $candidate.FullName
  }
} finally {
  if (-not ($TempDir -and $TempDir.Trim().Length -gt 0)) {
    Remove-DirSafe -PathToRemove $workRoot
  }
}

Write-Host "Bootstrap install complete."

