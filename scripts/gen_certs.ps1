<#
.SYNOPSIS
    Generate local mTLS certs into gitignored certs/: CA, server, and client.
.DESCRIPTION
    Uses OpenSSL. The server cert includes localhost/127.0.0.1 SANs. The client cert is used by
    scripts/verify_mtls.ps1 to prove client-certificate enforcement.
#>
[CmdletBinding()]
param([string]$Dir = 'certs')

$ErrorActionPreference = 'Stop'
if (-not (Get-Command openssl -EA SilentlyContinue)) { Write-Host '[certs] OpenSSL is required'; exit 1 }
$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not [System.IO.Path]::IsPathRooted($Dir)) { $Dir = Join-Path $RepoRoot $Dir }
New-Item -ItemType Directory -Force -Path $Dir | Out-Null

$caKey = Join-Path $Dir 'ca.key'
$caCrt = Join-Path $Dir 'ca.crt'
$serverKey = Join-Path $Dir 'server.key'
$serverCsr = Join-Path $Dir 'server.csr'
$serverCrt = Join-Path $Dir 'server.crt'
$clientKey = Join-Path $Dir 'client.key'
$clientCsr = Join-Path $Dir 'client.csr'
$clientCrt = Join-Path $Dir 'client.crt'
$clientPfx = Join-Path $Dir 'client.pfx'
$san = Join-Path $Dir 'server.ext'
$cfg = Join-Path $Dir 'openssl.cnf'

function Invoke-OpenSsl {
    param([string[]] $OpenSslArgs)
    & openssl @OpenSslArgs
    if ($LASTEXITCODE -ne 0) { throw "openssl failed: $($OpenSslArgs -join ' ')" }
}

@'
[req]
distinguished_name = dn
prompt = no
[dn]
CN = CardLens Local
[v3_ca]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
basicConstraints=critical,CA:true
keyUsage=critical,keyCertSign,cRLSign
[v3_server]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:false
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:localhost,IP:127.0.0.1
[v3_client]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:false
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=clientAuth
'@ | Out-File -Encoding ascii $cfg
Copy-Item $cfg $san -Force

Invoke-OpenSsl @('genrsa', '-out', $caKey, '4096') | Out-Null
Invoke-OpenSsl @('req', '-x509', '-new', '-nodes', '-key', $caKey, '-sha256', '-days', '3650', '-out', $caCrt, '-subj', '/CN=CardLens Local CA', '-config', $cfg, '-extensions', 'v3_ca') | Out-Null
Invoke-OpenSsl @('genrsa', '-out', $serverKey, '2048') | Out-Null
Invoke-OpenSsl @('req', '-new', '-key', $serverKey, '-out', $serverCsr, '-subj', '/CN=localhost', '-config', $cfg) | Out-Null
Invoke-OpenSsl @('x509', '-req', '-in', $serverCsr, '-CA', $caCrt, '-CAkey', $caKey, '-CAcreateserial', '-out', $serverCrt, '-days', '825', '-sha256', '-extfile', $cfg, '-extensions', 'v3_server') | Out-Null
Invoke-OpenSsl @('genrsa', '-out', $clientKey, '2048') | Out-Null
Invoke-OpenSsl @('req', '-new', '-key', $clientKey, '-out', $clientCsr, '-subj', '/CN=cardlens-local-client', '-config', $cfg) | Out-Null
Invoke-OpenSsl @('x509', '-req', '-in', $clientCsr, '-CA', $caCrt, '-CAkey', $caKey, '-CAcreateserial', '-out', $clientCrt, '-days', '825', '-sha256', '-extfile', $cfg, '-extensions', 'v3_client') | Out-Null
Invoke-OpenSsl @('pkcs12', '-export', '-out', $clientPfx, '-inkey', $clientKey, '-in', $clientCrt, '-certfile', $caCrt, '-passout', 'pass:') | Out-Null

Write-Host "[certs] generated CA/server/client certs in $Dir"
Write-Host "[certs] server=$serverCrt key=$serverKey ca=$caCrt client=$clientCrt pfx=$clientPfx"
