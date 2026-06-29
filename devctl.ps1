# devctl.ps1 - CardLens dev controller. Backend (:8000) from repo; frontend (:3000) from a LOCAL-disk
# mirror (C:\cl-web) so OneDrive never locks Next.js .next builds. Node 20 portable auto-added to PATH.
#   .\devctl.ps1 start|stop|restart|status|seed   [all|api|web]
[CmdletBinding()]
param([Parameter(Position=0)][string]$Action='status', [Parameter(Position=1)][string]$Target='all')

$ErrorActionPreference='Stop'
$Root=$PSScriptRoot
$ApiPort=8000; $WebPort=3000
$Mirror='C:\cl-web'
$Node=(Get-ChildItem (Join-Path $env:LOCALAPPDATA 'node20') -Directory -EA SilentlyContinue | Select-Object -First 1).FullName
function NodePath { if($Node){ $env:Path="$Node;$env:Path" } }
function PidOnPort([int]$p){ (netstat -aon 2>$null | Select-String ":$p\s.*LISTEN" | ForEach-Object { ($_ -split '\s+')[-1] } | Select-Object -First 1) }
function KillPort([int]$p){ $id=PidOnPort $p; if($id){ Stop-Process -Id $id -Force -EA SilentlyContinue; Write-Host "  stopped pid $id on :$p" } }

function StartApi {
  . "$Root\.venv\Scripts\Activate.ps1"; $env:PYTHONPATH="$Root\backend"; Remove-Item Env:CARDLENS_DATABASE_URL -EA SilentlyContinue
  Push-Location "$Root\backend"; alembic upgrade head | Out-Null; Pop-Location
  Start-Process python -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port',"$ApiPort" -WorkingDirectory "$Root\backend" -WindowStyle Hidden
  Write-Host "  API  -> http://localhost:$ApiPort"
}
function StartWeb {
  NodePath
  robocopy "$Root\frontend" $Mirror /E /XD node_modules .next /XF .env.local /NFL /NDL /NJH /NJS | Out-Null
  Push-Location $Mirror; if(-not(Test-Path node_modules)){ npm ci | Out-Null }; $env:NEXT_PUBLIC_API_BASE="http://localhost:$ApiPort"
  Start-Process npm -ArgumentList 'run','dev','--','--port',"$WebPort" -WorkingDirectory $Mirror -WindowStyle Hidden; Pop-Location
  Write-Host "  WEB  -> http://localhost:$WebPort  (mirror $Mirror)"
}
switch($Action){
  'start'   { if($Target -in 'all','api'){StartApi}; if($Target -in 'all','web'){StartWeb} }
  'stop'    { if($Target -in 'all','web'){KillPort $WebPort}; if($Target -in 'all','api'){KillPort $ApiPort} }
  'restart' { KillPort $WebPort; KillPort $ApiPort; if($Target -in 'all','api'){StartApi}; if($Target -in 'all','web'){StartWeb} }
  'seed'    { & "$Root\scripts\seed_sample_data.ps1" }
  default   { "API :$ApiPort pid $(PidOnPort $ApiPort)"; "WEB :$WebPort pid $(PidOnPort $WebPort)" }
}
