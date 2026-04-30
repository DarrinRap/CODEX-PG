param(
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8788
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$StartScript = Join-Path $Root "CODEX_start_panda_collaborator.ps1"
$Url = "http://$HostAddress`:$Port/"

& $StartScript -HostAddress $HostAddress -Port $Port
Start-Process $Url
