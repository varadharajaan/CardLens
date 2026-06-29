<#
.SYNOPSIS
    Run the backend over HTTPS with client certificates required (mTLS) on 8443.
#>
[CmdletBinding()]
param([int]$Port = 8443)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$certDir = Join-Path $Root 'certs'
if (-not (Test-Path (Join-Path $certDir 'server.crt'))) { & "$Root\scripts\gen_certs.ps1" }
. "$Root\.venv\Scripts\Activate.ps1"
$env:PYTHONPATH = "$Root\backend"
$env:CARDLENS_MTLS_ENABLED = 'true'
$env:CARDLENS_MTLS_CA_CERT = Join-Path $certDir 'ca.crt'
$env:CARDLENS_MTLS_SERVER_CERT = Join-Path $certDir 'server.crt'
$env:CARDLENS_MTLS_SERVER_KEY = Join-Path $certDir 'server.key'
Push-Location "$Root\backend"
try {
    alembic upgrade head | Out-Null
    python -m uvicorn app.main:app --host 127.0.0.1 --port $Port --ssl-certfile $env:CARDLENS_MTLS_SERVER_CERT --ssl-keyfile $env:CARDLENS_MTLS_SERVER_KEY --ssl-ca-certs $env:CARDLENS_MTLS_CA_CERT --ssl-cert-reqs 2
} finally {
    Pop-Location
}