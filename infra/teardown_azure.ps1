<#
.SYNOPSIS
    Delete all CardLens Azure resources (the whole resource group). Stops every cost.
#>
[CmdletBinding()]
param([string]$ResourceGroup = 'rg-cardlens')
$ErrorActionPreference = 'Stop'
Write-Host "[teardown] deleting resource group $ResourceGroup..."
az group delete -n $ResourceGroup --yes --no-wait
Write-Host '[teardown] delete requested (running in background).'
