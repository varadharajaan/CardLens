<#
.SYNOPSIS
    Run the full backend quality gate: lint, format check, import boundaries, types, and tests.
.PARAMETER NoLint
    Skip lint/format/type/architecture checks and run only the test suite.
#>
[CmdletBinding()]
param(
    [switch]$NoLint
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. "$RepoRoot\.venv\Scripts\Activate.ps1"
Set-Location $RepoRoot
$env:PYTHONPATH = "$RepoRoot\backend"

if (-not $NoLint) {
    Write-Host '[tests] ruff check...'
    ruff check backend
    Write-Host '[tests] ruff format check...'
    ruff format --check backend
    Write-Host '[tests] import-linter (layer boundaries)...'
    lint-imports --config pyproject.toml
    Write-Host '[tests] mypy...'
    mypy backend/app
}

Write-Host '[tests] pytest with coverage...'
pytest --cov=backend/app --cov-report=term-missing
