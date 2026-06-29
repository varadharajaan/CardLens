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

Write-Host "[deploy] resource group $ResourceGroup in $Location"
az group create -n $ResourceGroup -l $Location --only-show-errors | Out-Null

Write-Host '[deploy] backend (build in cloud, scale-to-zero)...'
az containerapp up `
    --name cardlens-api --resource-group $ResourceGroup --location $Location --environment $Env `
    --source "$RepoRoot" --dockerfile 'infra/backend.Dockerfile' `
    --ingress external --target-port 8000 --min-replicas 0 --only-show-errors
$api = az containerapp show -n cardlens-api -g $ResourceGroup --query properties.configuration.ingress.fqdn -o tsv
Write-Host "[deploy] backend live: https://$api"

Write-Host '[deploy] frontend (built against the live API)...'
az containerapp up `
    --name cardlens-web --resource-group $ResourceGroup --location $Location --environment $Env `
    --source "$RepoRoot\frontend" --dockerfile 'Dockerfile' `
    --build-env-vars "NEXT_PUBLIC_API_BASE=https://$api" `
    --ingress external --target-port 3000 --min-replicas 0 --only-show-errors
$web = az containerapp show -n cardlens-web -g $ResourceGroup --query properties.configuration.ingress.fqdn -o tsv

Write-Host ''
Write-Host '================ CardLens PROD ================'
Write-Host "API: https://$api/healthz   docs: https://$api/docs"
Write-Host "Web: https://$web"
Write-Host 'Teardown: infra/teardown_azure.ps1'
Write-Host '=============================================='
