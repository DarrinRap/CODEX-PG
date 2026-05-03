param(
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8788,
  [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic -ErrorAction SilentlyContinue

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$StartScript = Join-Path $Root "CODEX_start_panda_collaborator.ps1"
$Url = "http://$HostAddress`:$Port/"
$IsRunning = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1

function Invoke-PandaCollaboratorRefresh {
  try {
    $body = @{ source = "panda-collaborator-launcher" } | ConvertTo-Json -Compress
    $response = Invoke-RestMethod -Uri "$($Url)api/launch-refresh/request" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 2
    if (-not $response.ok -or [int]$response.active_clients -lt 1) {
      return $false
    }
    $token = [string]$response.token
    for ($i = 0; $i -lt 30; $i++) {
      Start-Sleep -Milliseconds 150
      $state = Invoke-RestMethod -Uri "$($Url)api/launch-refresh/state" -TimeoutSec 2
      if ([string]$state.token -eq $token -and [int]$state.foreground_ack_clients -gt 0) {
        return $true
      }
    }
  } catch {
    return $false
  }

  return $false
}

function Open-PandaCollaborator {
  if (Invoke-PandaCollaboratorRefresh) {
    return
  }

  Start-Process $Url
}

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

Open-PandaCollaborator
