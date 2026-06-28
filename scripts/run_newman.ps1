<#
.SYNOPSIS
    Run the CardLens Postman collection with Newman against a running API.
.DESCRIPTION
    Executes the committed Postman collection with --bail and a JUnit report under logs/local.
    Installs the pinned Newman (gitignored node_modules) on first use. Does NOT boot the server;
    use scripts/smoke.ps1 for the full boot + Newman + teardown gate.
.PARAMETER Environment
    Postman environment to use: local (default), staging, or prod.
.PARAMETER BaseUrl
    Optional override for the base_url environment variable (e.g. an ephemeral smoke port).
#>
[CmdletBinding()]
param(
    [ValidateSet('local', 'staging', 'prod')]
    [string]$Environment = 'local',
    [string]$BaseUrl
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$collection = Join-Path $RepoRoot 'postman\cardlens.postman_collection.json'
$envFile = Join-Path $RepoRoot "postman\cardlens.postman_environment_$Environment.json"
$newman = Join-Path $RepoRoot 'node_modules\.bin\newman.cmd'

if (-not (Test-Path $newman)) {
    Write-Host '[run_newman] Newman not found; installing pinned version from package.json...'
    Push-Location $RepoRoot
    try { npm install --no-audit --no-fund | Out-Null } finally { Pop-Location }
}

$reportDir = Join-Path $RepoRoot 'logs\local'
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$junit = Join-Path $reportDir 'newman-results.xml'

$newmanArgs = @(
    'run', $collection,
    '-e', $envFile,
    '--reporters', 'cli,junit',
    '--reporter-junit-export', $junit,
    '--bail'
)
if ($BaseUrl) { $newmanArgs += @('--env-var', "base_url=$BaseUrl") }

Write-Host "[run_newman] environment=$Environment baseUrl=$(if ($BaseUrl) { $BaseUrl } else { '(env default)' })"
& $newman @newmanArgs
exit $LASTEXITCODE
