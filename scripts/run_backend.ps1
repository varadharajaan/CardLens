<#
.SYNOPSIS
    Run the CardLens backend API locally with uvicorn.
.PARAMETER Port
    Port to listen on (default 8000).
.PARAMETER Reload
    Enable auto-reload for development.
#>
[CmdletBinding()]
param(
    [int]$Port = 8000,
    [switch]$Reload
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. "$RepoRoot\.venv\Scripts\Activate.ps1"
Set-Location "$RepoRoot\backend"
$env:PYTHONPATH = "$RepoRoot\backend"

$uvicornArgs = @('app.main:app', '--host', '0.0.0.0', '--port', "$Port")
if ($Reload) { $uvicornArgs += '--reload' }

Write-Host "[run_backend] starting on http://localhost:$Port (docs at /docs)"
uvicorn @uvicornArgs
