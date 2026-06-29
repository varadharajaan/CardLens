<#
.SYNOPSIS
    Execute the same mailbox scan job body used by the 6-hour scheduler once against the local DB.
#>
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. "$RepoRoot\.venv\Scripts\Activate.ps1"
$env:PYTHONPATH = "$RepoRoot\backend"
Push-Location "$RepoRoot\backend"
try {
@'
import app.db_metadata  # noqa: F401 - register all ORM tables for standalone scheduler runs
from app.mail.scheduler import run_mail_scan_once
accounts, ingested = run_mail_scan_once()
print(f"scheduler_accounts={accounts} scheduler_ingested={ingested}")
'@ | python -
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}
Write-Host '[scheduler-once] PASS'
