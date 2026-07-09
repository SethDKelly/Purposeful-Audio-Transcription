# Add GitHub CLI (gh) to PATH for this session (and optionally persist).

param(
    [switch]$Persist
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

$candidates = @(
    "C:\Program Files\GitHub CLI",
    (Join-Path $Root ".tools\gh\bin")
)

$GhBin = $null
foreach ($candidate in $candidates) {
    if (Test-Path (Join-Path $candidate "gh.exe")) {
        $GhBin = $candidate
        break
    }
}

if (-not $GhBin) {
    Write-Error @"
GitHub CLI not found.

Install with winget:
  winget install --id GitHub.cli -e

Or download the portable build into .tools\gh\bin
"@
}

if ($env:Path -notlike "*$GhBin*") {
    $env:Path = "$GhBin;$env:Path"
}

if ($Persist) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$GhBin*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$GhBin", "User")
        Write-Host "Persisted gh path to user PATH: $GhBin"
    } else {
        Write-Host "gh path already present in user PATH."
    }
}

Write-Host "gh is available for this session ($GhBin):"
& gh --version
Write-Host ""
Write-Host "Next steps:"
Write-Host "  gh auth login --hostname github.com --git-protocol https --web"
Write-Host "  .\scripts\create_release.ps1"
