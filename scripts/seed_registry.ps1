<#
.SYNOPSIS
    Apply database migrations, then seed the card registry table from versioned JSON files.
.DESCRIPTION
    Idempotent. Safe to re-run: registry entries are upserted by their stable key. Uses the
    repo-local virtual environment and the backend working directory so alembic resolves its
    configuration and the app package imports cleanly.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. "$RepoRoot\.venv\Scripts\Activate.ps1"
Set-Location "$RepoRoot\backend"
$env:PYTHONPATH = "$RepoRoot\backend"

Write-Host '[seed_registry] applying migrations (alembic upgrade head)...'
alembic upgrade head

Write-Host '[seed_registry] loading registry files...'
python -m app.registry.seed

Write-Host '[seed_registry] done.'
