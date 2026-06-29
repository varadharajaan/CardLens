<#
.SYNOPSIS
    Generate local dev certs for mTLS into the gitignored certs/ folder (mkcert preferred, openssl fallback).
#>
[CmdletBinding()]
param([string]$Dir = 'certs')
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $Dir | Out-Null
if (Get-Command mkcert -EA SilentlyContinue) {
    mkcert -install
    mkcert -cert-file "$Dir/server.crt" -key-file "$Dir/server.key" localhost 127.0.0.1
    Write-Host "[certs] mkcert generated server cert in $Dir"
} elseif (Get-Command openssl -EA SilentlyContinue) {
    openssl req -x509 -newkey rsa:2048 -nodes -keyout "$Dir/server.key" -out "$Dir/server.crt" -days 365 -subj "/CN=localhost"
    Write-Host "[certs] openssl self-signed cert in $Dir"
} else {
    Write-Host '[certs] install mkcert or openssl first'; exit 1
}
Write-Host 'Set CARDLENS_MTLS_ENABLED=true and CARDLENS_MTLS_SERVER_CERT/KEY to enforce.'
