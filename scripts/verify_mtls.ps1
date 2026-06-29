<#
.SYNOPSIS
    Verify mTLS: no client certificate must fail, client certificate must pass.
#>
[CmdletBinding()]
param([string]$BaseUrl = 'https://localhost:8443')

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$certDir = Join-Path $Root 'certs'
$ca = Join-Path $certDir 'ca.crt'
$cert = Join-Path $certDir 'client.crt'
$key = Join-Path $certDir 'client.key'
if (-not (Test-Path $cert)) { & "$Root\scripts\gen_certs.ps1" }
$hostPort = $BaseUrl -replace '^https://', ''
$request = "GET /healthz HTTP/1.1`r`nHost: localhost`r`nConnection: close`r`n`r`n"
$withoutClient = ($request | openssl s_client -connect $hostPort -CAfile $ca -quiet 2>&1) -join "`n"
if ($withoutClient -match '"status"\s*:\s*"ok"') {
    Write-Host '[mtls] FAIL: request without client cert unexpectedly succeeded' -ForegroundColor Red
    exit 1
}
$withClient = ($request | openssl s_client -connect $hostPort -cert $cert -key $key -CAfile $ca -quiet 2>&1) -join "`n"
if ($withClient -notmatch '"status"\s*:\s*"ok"') {
    Write-Host '[mtls] FAIL: request with client cert failed' -ForegroundColor Red
    Write-Host $withClient
    exit 1
}
Write-Host '[mtls] PASS: client certificate is required and valid client succeeds'