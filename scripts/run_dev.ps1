# Start the FastAPI backend and Streamlit UI for local development.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$python = Join-Path $Root ".venv\Scripts\python.exe"
$uvicorn = Join-Path $Root ".venv\Scripts\uvicorn.exe"
$streamlit = Join-Path $Root ".venv\Scripts\streamlit.exe"

if (-not (Test-Path $python)) {
    Write-Error "Virtual environment not found. Run: python -m venv .venv; pip install -e ."
}

# Pick up PATH changes (e.g. ffmpeg installed via winget) in child processes.
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

$apiHost = if ($env:API_HOST) { $env:API_HOST } else { "127.0.0.1" }
$apiPort = if ($env:API_PORT) { $env:API_PORT } else { "8000" }
$uiPort = if ($env:STREAMLIT_PORT) { $env:STREAMLIT_PORT } else { "8501" }

Write-Host "Starting API on http://${apiHost}:${apiPort} ..."
$apiProcess = Start-Process `
    -FilePath $uvicorn `
    -ArgumentList @("backend.main:app", "--reload", "--host", $apiHost, "--port", $apiPort) `
    -PassThru `
    -WindowStyle Minimized

Start-Sleep -Seconds 2

Write-Host "Starting Streamlit UI on http://localhost:${uiPort} ..."
Write-Host "Press Ctrl+C to stop the UI. The API will keep running in the background."
Write-Host ""

try {
    & $streamlit run ui/streamlit_app.py --server.port $uiPort --server.address localhost
}
finally {
    if (-not $apiProcess.HasExited) {
        Write-Host "Stopping API process ..."
        Stop-Process -Id $apiProcess.Id -Force
    }
}
