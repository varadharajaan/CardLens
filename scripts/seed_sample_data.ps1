<#
.SYNOPSIS
    Seed a realistic sample portfolio (companion credit cards, a bank account with debit-card
    variants, and statements) into the dev database via the live API, then print the dashboard.
.DESCRIPTION
    Self-contained and idempotent. Boots uvicorn on the dev SQLite database, applies migrations,
    registers (or logs in) a demo user, and - only if that user has no cards yet - creates:
      - an ICICI MakeMyTrip companion account with Mastercard (primary) and RuPay variants;
      - a standalone Axis Atlas credit card;
      - an HDFC savings account with Visa (primary) and RuPay debit-card variants;
      - statements (one on the companion account, one on the standalone card) chosen to exercise
        the dashboard's due-soon and high-utilization anomaly rules.
    Finally it prints the dashboard overview, rewards summary, milestones, and anomalies, then
    stops the server. The seeded data persists in the dev database for the frontend to display.
.PARAMETER Port
    Port for the ephemeral seeding server (default 8021).
.PARAMETER Email
    Demo user email (default demo@example.com).
#>
[CmdletBinding()]
param(
    [int]$Port = 8021,
    [string]$Email = 'demo@example.com',
    [string]$Password = 'Sup3rSecret!'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. "$RepoRoot\.venv\Scripts\Activate.ps1"
$env:PYTHONPATH = "$RepoRoot\backend"

$devDb = Join-Path "$RepoRoot\backend" 'cardlens.db'
$env:CARDLENS_DATABASE_URL = 'sqlite:///' + ($devDb -replace '\\', '/')
$env:CARDLENS_ENV = 'local'
$base = "http://127.0.0.1:$Port"

Write-Host "[seed] applying migrations to dev db: $devDb"
Push-Location "$RepoRoot\backend"
try { alembic upgrade head | Out-Null } finally { Pop-Location }

$logDir = Join-Path $RepoRoot 'logs\local'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$proc = Start-Process -FilePath 'python' `
    -ArgumentList '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', "$Port" `
    -WorkingDirectory "$RepoRoot\backend" -PassThru -NoNewWindow `
    -RedirectStandardOutput (Join-Path $logDir 'seed-app.out') `
    -RedirectStandardError (Join-Path $logDir 'seed-app.err')

function Invoke-Api {
    param([string]$Method, [string]$Path, [object]$Body, [string]$Token)
    $headers = @{ 'Accept' = 'application/json' }
    if ($Token) { $headers['Authorization'] = "Bearer $Token" }
    $params = @{ Method = $Method; Uri = "$base$Path"; Headers = $headers; TimeoutSec = 15 }
    if ($Body) { $params['Body'] = ($Body | ConvertTo-Json -Depth 6); $params['ContentType'] = 'application/json' }
    return Invoke-RestMethod @params
}

try {
    $healthy = $false
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 500
        try {
            $h = Invoke-RestMethod "$base/healthz" -TimeoutSec 2
            if ($h.status -eq 'ok') { $healthy = $true; break }
        } catch { }
    }
    if (-not $healthy) {
        Write-Host '[seed] FAIL: server did not become healthy' -ForegroundColor Red
        Get-Content (Join-Path $logDir 'seed-app.err') -Tail 30
        exit 1
    }

    # Register the demo user, or log in if it already exists.
    try {
        $auth = Invoke-Api -Method POST -Path '/api/v1/auth/register' -Body @{ email = $Email; password = $Password; full_name = 'CardLens Demo' }
        Write-Host "[seed] registered demo user $Email"
    } catch {
        $auth = Invoke-Api -Method POST -Path '/api/v1/auth/login' -Body @{ email = $Email; password = $Password }
        Write-Host "[seed] demo user exists; logged in as $Email"
    }
    $token = $auth.access_token

    $existing = Invoke-Api -Method GET -Path '/api/v1/cards' -Token $token
    if ($existing.total -ge 1) {
        Write-Host "[seed] portfolio already present ($($existing.total) cards); skipping creation." -ForegroundColor Yellow
    } else {
        $dueSoon = (Get-Date).AddDays(3).ToString('yyyy-MM-dd')

        $account = Invoke-Api -Method POST -Path '/api/v1/card-accounts' -Token $token -Body @{
            bank = 'ICICI'; display_name = 'ICICI MakeMyTrip'; last4_primary = '9012'; credit_limit = 100000; statement_day = 5
        }
        Invoke-Api -Method POST -Path '/api/v1/cards' -Token $token -Body @{
            bank = 'ICICI'; card_name = 'MakeMyTrip Mastercard'; last4 = '9012'; network = 'MASTERCARD'; account_id = $account.id; is_primary = $true; reward_format = 'REWARD_POINTS'
        } | Out-Null
        Invoke-Api -Method POST -Path '/api/v1/cards' -Token $token -Body @{
            bank = 'ICICI'; card_name = 'MakeMyTrip RuPay'; last4 = '3456'; network = 'RUPAY'; account_id = $account.id; reward_format = 'CASHBACK'
        } | Out-Null
        $standalone = Invoke-Api -Method POST -Path '/api/v1/cards' -Token $token -Body @{
            bank = 'AXIS'; card_name = 'Axis Atlas'; last4 = '1111'; network = 'VISA'; reward_format = 'REWARD_POINTS'
        }

        $bank = Invoke-Api -Method POST -Path '/api/v1/bank-accounts' -Token $token -Body @{
            bank = 'HDFC'; account_type = 'SAVINGS'; display_name = 'HDFC Salary'; last4 = '7788'; balance = 125000.50
        }
        Invoke-Api -Method POST -Path '/api/v1/debit-cards' -Token $token -Body @{
            bank_account_id = $bank.id; card_name = 'HDFC Visa Debit'; last4 = '7788'; network = 'VISA'; is_primary = $true; reward_format = 'REWARD_POINTS'
        } | Out-Null
        Invoke-Api -Method POST -Path '/api/v1/debit-cards' -Token $token -Body @{
            bank_account_id = $bank.id; card_name = 'HDFC RuPay Debit'; last4 = '5566'; network = 'RUPAY'; reward_format = 'CASHBACK'
        } | Out-Null

        # Companion-account statement: due soon and at 85% of the limit (exercises both anomaly rules).
        Invoke-Api -Method POST -Path '/api/v1/statements' -Token $token -Body @{
            account_id = $account.id; bank = 'ICICI'; card_name = 'MakeMyTrip Mastercard'; last4 = '9012'
            statement_date = '2026-06-01'; due_date = $dueSoon; total_due = 85000; minimum_due = 4250
            reward_points_closing = 52000; reward_type = 'REWARD_POINTS'; reward_parse_status = 'FOUND'; reward_confidence = 0.96
        } | Out-Null
        # Standalone-card statement with cashback rewards.
        Invoke-Api -Method POST -Path '/api/v1/statements' -Token $token -Body @{
            card_id = $standalone.id; bank = 'AXIS'; card_name = 'Axis Atlas'; last4 = '1111'
            statement_date = '2026-06-02'; due_date = '2026-06-20'; total_due = 18000; minimum_due = 900
            cashback_earned = 1250; reward_type = 'CASHBACK'; reward_parse_status = 'FOUND'; reward_confidence = 0.93
        } | Out-Null

        Write-Host '[seed] created companion account, standalone card, bank account, debit cards, and statements.' -ForegroundColor Green
    }

    $overview = Invoke-Api -Method GET -Path '/api/v1/dashboard/overview' -Token $token
    $rewards = Invoke-Api -Method GET -Path '/api/v1/rewards/summary' -Token $token
    $milestones = Invoke-Api -Method GET -Path '/api/v1/milestones' -Token $token
    $anomalies = Invoke-Api -Method GET -Path '/api/v1/anomalies' -Token $token

    Write-Host ''
    Write-Host '================ CardLens dashboard (demo user) ================'
    Write-Host ("cards={0}  card_accounts={1}  bank_accounts={2}  debit_cards={3}  statements={4}" -f `
            $overview.counts.cards, $overview.counts.card_accounts, $overview.counts.bank_accounts, $overview.counts.debit_cards, $overview.counts.statements)
    Write-Host ("billing_groups={0}  outstanding_due=Rs {1}  minimum_due=Rs {2}  nearest_due={3}" -f `
            $overview.billing_groups, $overview.total_outstanding_due, $overview.total_minimum_due, $overview.nearest_due_date)
    Write-Host ("reward_points={0}  cashback=Rs {1}  estimated_value=Rs {2}" -f `
            $overview.total_reward_points, $overview.total_cashback, $rewards.estimated_value_inr)
    $achieved = ($milestones.items | Where-Object { $_.achieved } | ForEach-Object { $_.label }) -join ', '
    Write-Host ("milestones_achieved: {0}" -f ($(if ($achieved) { $achieved } else { 'none yet' })))
    Write-Host 'anomalies:'
    foreach ($a in $anomalies.items) { Write-Host ("  [{0}] {1}" -f $a.rule, $a.message) }
    Write-Host '==============================================================='
    Write-Host '[seed] done. Start the dev server (scripts/run_backend.ps1) and log in as the demo user.' -ForegroundColor Green
    exit 0
}
finally {
    if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force }
}
