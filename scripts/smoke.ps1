<#
.SYNOPSIS
    Live API contract gate: boot the backend on an isolated DB, run Newman against it, tear down.
.DESCRIPTION
    This is the PART 26 pre-push gate adapted for CardLens (Python/FastAPI). Because this project
    runs no GitHub CI, this local gate is the only Newman gate and must be GREEN before every push
    that touches an HTTP surface.

    Steps: create a throwaway SQLite DB under logs/local, apply migrations, boot uvicorn on an
    isolated port, poll until healthy, run the committed Postman collection with Newman, then stop
    the server and report Newman's exit code. All artifacts are written under logs/local.
.PARAMETER Port
    Port for the ephemeral server (default 8012).
#>
[CmdletBinding()]
param(
    [int]$Port = 8012
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. "$RepoRoot\.venv\Scripts\Activate.ps1"
$env:PYTHONPATH = "$RepoRoot\backend"

$logDir = Join-Path $RepoRoot 'logs\local'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$smokeDb = Join-Path $logDir 'smoke.db'
if (Test-Path $smokeDb) { Remove-Item $smokeDb -Force }
$env:CARDLENS_DATABASE_URL = 'sqlite:///' + ($smokeDb -replace '\\', '/')
$env:CARDLENS_ENV = 'local'

Write-Host "[smoke] migrating isolated db: $smokeDb"
Push-Location "$RepoRoot\backend"
try { alembic upgrade head | Out-Null } finally { Pop-Location }

$outLog = Join-Path $logDir 'smoke-app.out'
$errLog = Join-Path $logDir 'smoke-app.err'
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
        Write-Host '[smoke] FAIL: server did not become healthy' -ForegroundColor Red
        if (Test-Path $errLog) { Get-Content $errLog -Tail 30 }
        exit 1
    }
    Write-Host "[smoke] server healthy on port $Port; running Newman against the live process..."
    & "$RepoRoot\scripts\run_newman.ps1" -Environment local -BaseUrl "http://127.0.0.1:$Port"
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Host "[smoke] FAIL: Newman exit $code" -ForegroundColor Red
        exit $code
    }
    Write-Host '[smoke] PASS: live boot + Newman green' -ForegroundColor Green
    exit 0
}
finally {
    if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
}
