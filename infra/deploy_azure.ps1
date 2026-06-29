<#
.SYNOPSIS
    Deploy CardLens to Azure Container Apps (cheapest, scale-to-zero), build images in the cloud.
.DESCRIPTION
    No local Docker needed: images build via ACR/cloud from the infra/ Dockerfiles. Backend first
    (so the frontend can be built against its URL), then frontend. Consumption plan with min-replicas
    0 keeps idle cost near zero. Run infra/teardown_azure.ps1 to delete everything.
.PARAMETER ResourceGroup
    Resource group (default rg-cardlens).
.PARAMETER Location
    Azure region (default centralindia).
#>
[CmdletBinding()]
param(
    [string]$ResourceGroup = 'rg-cardlens',
    [string]$Location = 'centralindia',
    [string]$Env = 'cardlens-env'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host '[deploy] ensuring containerapp extension...'
az extension add --name containerapp --upgrade --only-show-errors | Out-Null
az provider register -n Microsoft.App --wait | Out-Null
az provider register -n Microsoft.OperationalInsights --wait | Out-Null
az provider register -n Microsoft.ContainerRegistry --wait | Out-Null

Write-Host "[deploy] resource group $ResourceGroup in $Location"
az group create -n $ResourceGroup -l $Location --only-show-errors | Out-Null

Write-Host '[deploy] backend (cloud build, a few minutes)...'
az containerapp up --name cardlens-api --resource-group $ResourceGroup --location $Location `
    --environment $Env --source "$RepoRoot" --ingress external --target-port 8000
az containerapp update -n cardlens-api -g $ResourceGroup --min-replicas 0 --max-replicas 2 --only-show-errors | Out-Null
$api = az containerapp show -n cardlens-api -g $ResourceGroup --query properties.configuration.ingress.fqdn -o tsv

$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 4
    try { if ((Invoke-RestMethod "https://$api/healthz" -TimeoutSec 6).status -eq 'ok') { $ok = $true; break } } catch {}
}
Write-Host ''
Write-Host '================ CardLens PROD ================'
Write-Host "API: https://$api/healthz   docs: https://$api/docs"
Write-Host ("Health: {0}" -f $(if ($ok) { 'OK' } else { 'not-ready' }))
Write-Host 'Teardown: infra/teardown_azure.ps1'
Write-Host '=============================================='
