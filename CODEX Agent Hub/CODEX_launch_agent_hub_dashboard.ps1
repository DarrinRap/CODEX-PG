param(
    [int]$Port = 8765
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TrayScript = Join-Path $ScriptRoot 'CODEX_start_agent_hub_tray.ps1'
$Url = "http://127.0.0.1:$Port"

function Test-PahServer {
    try {
        $status = Invoke-RestMethod -Uri "$Url/api/status" -Method Get -TimeoutSec 2
        return $null -ne $status
    }
    catch {
        return $false
    }
}

function Test-PahTrayRunning {
    $escaped = [WildcardPattern]::Escape($TrayScript)
    $matches = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*$escaped*" }
    return $null -ne $matches
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
    if (Test-PahServer) {
        Start-Process $Url
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
