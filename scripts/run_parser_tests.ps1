<#
.SYNOPSIS
    Focused runner for the statement parser tests (fast iteration on profiles and the engine).
.DESCRIPTION
    Runs only the parser unit tests against synthetic statement fixtures. The full gate
    (scripts/run_all_tests.ps1) still runs these plus everything else.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. "$RepoRoot\.venv\Scripts\Activate.ps1"
$env:PYTHONPATH = "$RepoRoot\backend"
Set-Location $RepoRoot

Write-Host '[parser-tests] running statement parser tests...'
python -m pytest backend/tests/test_parsers.py -q
exit $LASTEXITCODE
