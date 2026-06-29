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
$env:PYTHONUTF8 = '1'
try { chcp 65001 | Out-Null } catch {}
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host '[deploy] ensuring containerapp extension...'
az extension add --name containerapp --upgrade --only-show-errors | Out-Null
az provider register -n Microsoft.App --wait | Out-Null
az provider register -n Microsoft.OperationalInsights --wait | Out-Null
az provider register -n Microsoft.ContainerRegistry --wait | Out-Null

Write-Host "[deploy] resource group $ResourceGroup in $Location"
az group create -n $ResourceGroup -l $Location --only-show-errors | Out-Null

Write-Host '[deploy] backend (ACR build + Container App, a few minutes)...'
$acr = (az acr list -g $ResourceGroup --query "[0].name" -o tsv)
if (-not $acr) { $acr = "cardlensacr$((Get-Random -Maximum 99999))"; az acr create -n $acr -g $ResourceGroup --sku Basic --admin-enabled true --only-show-errors | Out-Null }
az acr update -n $acr --admin-enabled true --only-show-errors | Out-Null
az acr build -r $acr -t "cardlens-api:v1" -f Dockerfile "$RepoRoot" | Out-Null
$loginServer = az acr show -n $acr --query loginServer -o tsv
$acrUser = az acr credential show -n $acr --query username -o tsv
$acrPass = az acr credential show -n $acr --query "passwords[0].value" -o tsv
az containerapp create --name cardlens-api --resource-group $ResourceGroup --environment $Env `
    --image "$loginServer/cardlens-api:v1" --registry-server $loginServer `
    --registry-username $acrUser --registry-password $acrPass `
    --ingress external --target-port 8000 --min-replicas 0 --max-replicas 2 --only-show-errors | Out-Null
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
