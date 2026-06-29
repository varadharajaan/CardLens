<#
.SYNOPSIS
    Live pull-scan proof: authenticate, connect Gmail (dry-run if OAuth creds absent), run scan, verify dashboard data.
#>
[CmdletBinding()]
param(
    [string]$BaseUrl = 'http://127.0.0.1:8000',
    [string]$Email = 'demo@example.com',
    [string]$Password = 'Sup3rSecret!'
)
$ErrorActionPreference = 'Stop'
function Invoke-Json($Method, $Path, $Body, $Token) {
    $h = @{ Accept = 'application/json' }
    if ($Token) { $h.Authorization = "Bearer $Token" }
    $p = @{ Method = $Method; Uri = "$BaseUrl$Path"; Headers = $h; TimeoutSec = 30 }
    if ($Body) { $p.ContentType = 'application/json'; $p.Body = ($Body | ConvertTo-Json -Depth 6) }
    Invoke-RestMethod @p
}
try {
    $auth = Invoke-Json POST '/api/v1/auth/register' @{ email=$Email; password=$Password; full_name='Demo User' } $null
} catch {
    $auth = Invoke-Json POST '/api/v1/auth/login' @{ email=$Email; password=$Password } $null
}
$token = $auth.access_token
$connect = Invoke-Json POST '/api/v1/mail/accounts/connect' $null $token
$scan = Invoke-Json POST '/api/v1/ingestion/scan' $null $token
$overview = Invoke-Json GET '/api/v1/dashboard/overview' $null $token
Write-Host ("connect_dry_run={0} scanned={1} ingested={2} statements={3} rewards={4}" -f $connect.dry_run, $scan.scanned, $scan.statements_ingested, $overview.counts.statements, $overview.total_reward_points)
if ($scan.scanned -lt 1) { exit 1 }
if ($overview.counts.statements -lt 1) { exit 1 }
Write-Host '[scan-mailbox] PASS'
