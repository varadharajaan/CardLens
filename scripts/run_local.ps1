<#
.SYNOPSIS
    Run the full CardLens stack locally: the backend API and the Next.js frontend together.
.DESCRIPTION
    Applies migrations against the dev database, starts the FastAPI backend as a child process, then
    runs the Next.js frontend in the foreground pointed at that backend. Press Ctrl+C to stop the
    frontend; the backend child process is stopped automatically on exit. Seed demo data first with
    scripts/seed_sample_data.ps1, then sign in with the demo account.
.PARAMETER ApiPort
    Backend port (default 8000).
.PARAMETER WebPort
    Frontend port (default 3000).
#>
[CmdletBinding()]
param(
    [int]$ApiPort = 8000,
    [int]$WebPort = 3000
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. "$RepoRoot\.venv\Scripts\Activate.ps1"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    $nodeRoot = Join-Path $env:LOCALAPPDATA 'node20'
    if (Test-Path $nodeRoot) {
        $dir = Get-ChildItem $nodeRoot -Directory | Select-Object -First 1
        if ($dir) { $env:Path = "$($dir.FullName);$env:Path" }
    }
}

$env:PYTHONPATH = "$RepoRoot\backend"
$devDb = Join-Path "$RepoRoot\backend" 'cardlens.db'
$env:CARDLENS_DATABASE_URL = 'sqlite:///' + ($devDb -replace '\\', '/')
$env:CARDLENS_ENV = 'local'

Write-Host '[run_local] applying migrations...'
Push-Location "$RepoRoot\backend"
try { alembic upgrade head | Out-Null } finally { Pop-Location }

Write-Host "[run_local] starting backend on http://127.0.0.1:$ApiPort"
$api = Start-Process -FilePath 'python' `
    -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', "$ApiPort" `
    -WorkingDirectory "$RepoRoot\backend" -PassThru -NoNewWindow

try {
    $env:NEXT_PUBLIC_API_BASE = "http://localhost:$ApiPort"
    Set-Location "$RepoRoot\frontend"
    if (-not (Test-Path 'node_modules')) {
        Write-Host '[run_local] installing frontend dependencies...'
        npm ci
    }
    Write-Host "[run_local] starting frontend on http://localhost:$WebPort (Ctrl+C to stop)"
    npm run dev -- --port $WebPort
}
finally {
    if ($api -and -not $api.HasExited) { Stop-Process -Id $api.Id -Force }
}
