<#
.SYNOPSIS
    Boot the backend, verify liveness and readiness, then shut it down.
.DESCRIPTION
    Starts uvicorn on an isolated port, polls /healthz until it responds, checks /readyz reports the
    database is up, and exits non-zero if either probe fails. Used as a pre-push boot gate.
#>
[CmdletBinding()]
param(
    [int]$Port = 8011
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. "$RepoRoot\.venv\Scripts\Activate.ps1"
$env:PYTHONPATH = "$RepoRoot\backend"

$logDir = Join-Path $RepoRoot 'logs\local'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$outLog = Join-Path $logDir 'verify-boot.out'
$errLog = Join-Path $logDir 'verify-boot.err'

$proc = Start-Process -FilePath 'python' `
    -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', "$Port" `
    -WorkingDirectory "$RepoRoot\backend" -PassThru -NoNewWindow `
    -RedirectStandardOutput $outLog -RedirectStandardError $errLog

try {
    $healthy = $false
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 500
        try {
            $h = Invoke-RestMethod "http://127.0.0.1:$Port/healthz" -TimeoutSec 2
            if ($h.status -eq 'ok') { $healthy = $true; break }
        } catch { }
    }
    if (-not $healthy) {
        Write-Host '[verify_boot] FAIL: /healthz never became available' -ForegroundColor Red
        if (Test-Path $errLog) { Get-Content $errLog -Tail 20 }
        exit 1
    }
    $r = Invoke-RestMethod "http://127.0.0.1:$Port/readyz" -TimeoutSec 5
    Write-Host "[verify_boot] healthz=ok readyz=$($r.status) database=$($r.database)"
    if ($r.status -ne 'ready') {
        Write-Host '[verify_boot] FAIL: /readyz not ready' -ForegroundColor Red
        exit 1
    }
    Write-Host '[verify_boot] PASS' -ForegroundColor Green
    exit 0
}
finally {
    if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
}
