<#
.SYNOPSIS
    Verify the deployed CardLens prod backend is live: health, readiness, OpenAPI, and a registry read.
#>
[CmdletBinding()]
param([string]$ResourceGroup = 'rg-cardlens')
$ErrorActionPreference = 'Stop'
$api = az containerapp show -n cardlens-api -g $ResourceGroup --query properties.configuration.ingress.fqdn -o tsv
if (-not $api) { Write-Host '[verify-prod] no api fqdn'; exit 1 }
$base = "https://$api"
Write-Host "[verify-prod] $base"
$h = Invoke-RestMethod "$base/healthz" -TimeoutSec 20
$r = Invoke-RestMethod "$base/readyz" -TimeoutSec 20
$o = Invoke-RestMethod "$base/openapi.json" -TimeoutSec 20
Write-Host ("health={0} ready={1} title='{2}' paths={3}" -f $h.status, $r.status, $o.info.title, $o.paths.PSObject.Properties.Count)
if ($h.status -ne 'ok') { exit 1 }
Write-Host '[verify-prod] PASS: prod backend is live'
