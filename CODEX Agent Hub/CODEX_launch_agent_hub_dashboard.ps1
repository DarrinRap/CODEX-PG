param(
    [int]$Port = 8765,
    [ValidateSet('Default', 'Edge', 'Chrome')]
    [string]$Browser = 'Default'
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic -ErrorAction SilentlyContinue

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TrayScript = Join-Path $ScriptRoot 'CODEX_start_agent_hub_tray.ps1'
$Url = "http://127.0.0.1:$Port"

function Test-PahServer {
    $client = $null
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $connect = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $connect.AsyncWaitHandle.WaitOne(800)) {
            return $false
        }
        $client.EndConnect($connect)
        return $true
    }
    catch {
        return $false
    }
    finally {
        if ($client) { $client.Close() }
    }
}

function Test-PahTrayRunning {
    $matches = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -like '*CODEX_start_agent_hub_tray.ps1*' -and
            $_.CommandLine -like "*-Port $Port*"
        }
    return $null -ne $matches
}

function Test-PahHttpReady {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
        return ($response.StatusCode -eq 200 -and $response.Content -like '*PANDA Agent Hub*')
    }
    catch {
        return $false
    }
}

function Invoke-PahDashboardRefresh {
    try {
        $body = @{ source = 'pah-dashboard-launcher' } | ConvertTo-Json -Compress
        $response = Invoke-RestMethod -Uri "$Url/api/launch-refresh/request" -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 2
        if (-not $response.ok -or [int]$response.active_clients -lt 1) {
            return $false
        }
        $token = [string]$response.token
        for ($i = 0; $i -lt 30; $i++) {
            Start-Sleep -Milliseconds 150
            $state = Invoke-RestMethod -Uri "$Url/api/launch-refresh/state" -TimeoutSec 2
            if ([string]$state.token -eq $token -and [int]$state.ack_clients -gt 0) {
                return $true
            }
        }
    }
    catch {
        return $false
    }

    return $false
}

function Open-PahDashboard {
    $edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    $chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

    if (Invoke-PahDashboardRefresh) {
        return
    }

    if ($Browser -eq 'Edge' -and (Test-Path -LiteralPath $edge)) {
        Start-Process -FilePath $edge -ArgumentList @($Url)
        return
    }
    if ($Browser -eq 'Chrome' -and (Test-Path -LiteralPath $chrome)) {
        Start-Process -FilePath $chrome -ArgumentList @($Url)
        return
    }
    if ($Browser -eq 'Default') {
        if (Test-Path -LiteralPath $edge) {
            Start-Process -FilePath $edge -ArgumentList @($Url)
            return
        }
        if (Test-Path -LiteralPath $chrome) {
            Start-Process -FilePath $chrome -ArgumentList @($Url)
            return
        }
    }

    Start-Process $Url
}

if (-not (Test-PahServer)) {
    Start-Process -FilePath "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -ArgumentList @(
        '-NoProfile',
        '-STA',
        '-ExecutionPolicy',
        'Bypass',
        '-WindowStyle',
        'Hidden',
        '-File',
        "`"$TrayScript`"",
        '-Port',
        "$Port"
    ) -WindowStyle Hidden
}
elseif ((Test-PahServer) -and -not (Test-PahTrayRunning)) {
    Start-Process -FilePath "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -ArgumentList @(
        '-NoProfile',
        '-STA',
        '-ExecutionPolicy',
        'Bypass',
        '-WindowStyle',
        'Hidden',
        '-File',
        "`"$TrayScript`"",
        '-Port',
        "$Port",
        '-NoServer'
    ) -WindowStyle Hidden
}

for ($i = 0; $i -lt 40; $i++) {
    if (Test-PahHttpReady) {
        Open-PahDashboard
        exit 0
    }
    Start-Sleep -Milliseconds 250
}

[System.Windows.Forms.MessageBox]::Show(
    "PANDA Agent Hub did not become ready at $Url. Try launching it from PowerShell or check PAH logs.",
    'PANDA Agent Hub',
    'OK',
    'Warning'
) | Out-Null
