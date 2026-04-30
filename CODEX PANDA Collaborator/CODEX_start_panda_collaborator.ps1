param(
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8788
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script = Join-Path $Root "panda_collaborator.py"
$OutLog = Join-Path $Root "server.out.log"
$ErrLog = Join-Path $Root "server.err.log"

function Resolve-PandaPython {
  $candidates = @(
    (Join-Path $env:LOCALAPPDATA "Python\bin\python.exe"),
    "python"
  )
  foreach ($candidate in $candidates) {
    try {
      $command = Get-Command $candidate -ErrorAction Stop
      return $command.Source
    } catch {
      continue
    }
  }
  throw "Python was not found."
}

$existing = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existing) {
  Write-Host "PANDA Collaborator is already listening on http://$HostAddress`:$Port/"
  exit 0
}

$python = Resolve-PandaPython
Remove-Item -Path $OutLog, $ErrLog -ErrorAction SilentlyContinue
Start-Process -FilePath $python `
  -ArgumentList @("`"$Script`"", "--host", $HostAddress, "--port", "$Port") `
  -WorkingDirectory $Root `
  -WindowStyle Hidden `
  -RedirectStandardOutput $OutLog `
  -RedirectStandardError $ErrLog

Start-Sleep -Seconds 2
$health = Invoke-RestMethod -Uri "http://$HostAddress`:$Port/api/health" -TimeoutSec 10
if (-not $health.ok) {
  throw "PANDA Collaborator started but health check failed."
}

Write-Host "PANDA Collaborator $($health.version) is running."
Write-Host "Open http://$HostAddress`:$Port/"
