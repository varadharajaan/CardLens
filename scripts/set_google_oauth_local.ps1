<#
.SYNOPSIS
    Prompt locally for Google OAuth client credentials and write them to gitignored .env.
.DESCRIPTION
    Secrets are typed into the terminal only; do not paste them into chat. Existing .env values are
    preserved except CARDLENS_GOOGLE_CLIENT_ID, CARDLENS_GOOGLE_CLIENT_SECRET, and CARDLENS_GMAIL_DRY_RUN.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $RepoRoot '.env'
$clientId = Read-Host 'Google OAuth client id'
$secret = Read-Host 'Google OAuth client secret' -AsSecureString
$secretPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret))
$lines = @()
if (Test-Path $envFile) {
    $lines = Get-Content $envFile | Where-Object { $_ -notmatch '^CARDLENS_GOOGLE_CLIENT_ID=' -and $_ -notmatch '^CARDLENS_GOOGLE_CLIENT_SECRET=' -and $_ -notmatch '^CARDLENS_GMAIL_DRY_RUN=' }
}
$lines += "CARDLENS_GOOGLE_CLIENT_ID=$clientId"
$lines += "CARDLENS_GOOGLE_CLIENT_SECRET=$secretPlain"
$lines += 'CARDLENS_GMAIL_DRY_RUN=false'
$lines | Out-File -Encoding ascii $envFile
Write-Host '[google-oauth] wrote Google OAuth config to gitignored .env (dry-run disabled). Restart backend.'
