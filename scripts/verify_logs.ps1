<#
.SYNOPSIS
    Verify structured logs are produced and contain no obvious secret leaks.
.DESCRIPTION
    Confirms logs/local/app.log exists, has at least one parseable JSON line, and that no unmasked
    password, token, or secret value appears in the recent log tail.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $RepoRoot 'logs\local'
$appLog = Join-Path $logDir 'app.log'

if (-not (Test-Path $appLog)) {
    Write-Host "[verify_logs] FAIL: $appLog not found" -ForegroundColor Red
    exit 1
}

$lines = Get-Content $appLog -Tail 100
if (-not $lines) {
    Write-Host '[verify_logs] FAIL: app.log is empty' -ForegroundColor Red
    exit 1
}

$jsonOk = $false
foreach ($line in $lines) {
    try { $null = $line | ConvertFrom-Json; $jsonOk = $true; break } catch { }
}
if (-not $jsonOk) {
    Write-Host '[verify_logs] FAIL: no parseable JSON log line found' -ForegroundColor Red
    exit 1
}

$leakPattern = '"(password|refresh_token|access_token|jwt_secret|client_secret|pdf_password)"\s*:\s*"(?!\*\*\*)[^"]+'
$leaks = Select-String -Path $appLog -Pattern $leakPattern
if ($leaks) {
    Write-Host '[verify_logs] FAIL: potential secret found in logs' -ForegroundColor Red
    $leaks | Select-Object -First 3 | ForEach-Object { Write-Host $_.Line }
    exit 1
}

Write-Host '[verify_logs] PASS: app.log present, JSON valid, no obvious secret leaks' -ForegroundColor Green
exit 0
