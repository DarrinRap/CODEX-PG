$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$App = Join-Path $Root "panda_collaborator.py"
$Tests = Join-Path $Root "tests"

python -m py_compile $App
python -m unittest discover -s $Tests

try {
  $health = Invoke-RestMethod -Uri "http://127.0.0.1:8788/api/health" -TimeoutSec 5
  Write-Host "Live health: $($health.app) $($health.version) ok=$($health.ok)"
} catch {
  Write-Host "Live health: server not running on http://127.0.0.1:8788/"
}
