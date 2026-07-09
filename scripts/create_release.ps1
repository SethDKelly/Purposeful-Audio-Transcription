# Create the v0.2.0 GitHub Release (run after: gh auth login)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Invoke-Gh {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $gh @Args
        return $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prev
    }
}

$gh = (Get-Command gh -ErrorAction SilentlyContinue).Source
if (-not $gh) {
    $candidates = @(
        "C:\Program Files\GitHub CLI\gh.exe",
        (Join-Path $Root ".tools\gh\bin\gh.exe")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            $gh = $candidate
            break
        }
    }
}

if (-not $gh) {
    Write-Error "gh not found. Run scripts\setup_gh.ps1 or install GitHub CLI."
}

& $gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Error "gh is not authenticated. Run: gh auth login --hostname github.com --git-protocol https --web"
}

if ((Invoke-Gh release view v0.2.0) -eq 0) {
    Write-Host "Release v0.2.0 already exists."
    & $gh release view v0.2.0 --web
    exit 0
}

$notesFile = Join-Path $Root "doc\releases\v0.2.0.md"
& $gh release create v0.2.0 --title "v0.2.0 - RRE MVP" --notes-file $notesFile
Write-Host "Release created."
& $gh release view v0.2.0 --web
