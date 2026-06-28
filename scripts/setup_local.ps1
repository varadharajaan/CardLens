<#
.SYNOPSIS
    One-command local setup for the CardLens backend.
.DESCRIPTION
    Ensures uv is available, creates the virtual environment, installs runtime and dev dependencies
    from requirements-dev.txt, and applies database migrations. Safe to re-run.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
Write-Host "[setup] repo root: $RepoRoot"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[setup] installing uv..."
    python -m pip install --quiet --upgrade uv
}

if (-not (Test-Path "$RepoRoot\.venv")) {
    Write-Host "[setup] creating virtual environment..."
    uv venv "$RepoRoot\.venv" --python 3.13
}

. "$RepoRoot\.venv\Scripts\Activate.ps1"

Write-Host "[setup] installing dependencies..."
uv pip install -r "$RepoRoot\requirements-dev.txt"

if (-not (Test-Path "$RepoRoot\.env")) {
    Write-Host "[setup] creating .env from .env.example"
    Copy-Item "$RepoRoot\.env.example" "$RepoRoot\.env"
}

Write-Host "[setup] applying migrations..."
Push-Location "$RepoRoot\backend"
$env:PYTHONPATH = "$RepoRoot\backend"
alembic upgrade head
Pop-Location

Write-Host "[setup] done."
