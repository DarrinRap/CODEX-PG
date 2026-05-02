param(
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8788,
  [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$StartScript = Join-Path $Root "CODEX_start_panda_collaborator.ps1"
$Url = "http://$HostAddress`:$Port/"
$IsRunning = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1

if ($IsRunning) {
  Write-Host "PANDA Collaborator is already listening on $Url"
} else {
  & $StartScript -HostAddress $HostAddress -Port $Port
}

if ($NoBrowser) {
  Write-Host "Browser launch skipped. Refresh the existing tab:"
  Write-Host $Url
  exit 0
}

Start-Process $Url
