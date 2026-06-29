<#
.SYNOPSIS
    Frontend gate: type-check, lint, and production-build the Next.js app.
.DESCRIPTION
    Mirrors the backend gate for the UI. Ensures the portable Node 20 runtime is on PATH (falls back
    to a system Node if present), installs dependencies when missing, then runs the Next.js build which
    type-checks and lints. Non-zero exit on any failure so this can gate a push.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Frontend = Join-Path $RepoRoot 'frontend'

$nodeRoot = Join-Path $env:LOCALAPPDATA 'node20'
if (Test-Path $nodeRoot) {
    $dir = Get-ChildItem $nodeRoot -Directory | Select-Object -First 1
    if ($dir) { $env:Path = "$($dir.FullName);$env:Path" }
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host '[frontend] FAIL: Node.js not found on PATH' -ForegroundColor Red
    exit 1
}

Set-Location $Frontend
if (-not (Test-Path 'node_modules')) {
    Write-Host '[frontend] installing dependencies (npm ci)...'
    npm ci
}

Write-Host '[frontend] next build (type-check + lint + build)...'
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host '[frontend] FAIL: build error' -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host '[frontend] PASS: build green' -ForegroundColor Green
exit 0
