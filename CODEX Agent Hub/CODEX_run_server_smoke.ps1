$ErrorActionPreference = 'Stop'

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$App = Join-Path $ScriptRoot 'CODEX_agent_hub.py'
$Logs = Join-Path $ScriptRoot 'CODEX logs'
New-Item -ItemType Directory -Force -Path $Logs | Out-Null

$Stdout = Join-Path $Logs 'CODEX_server_smoke_stdout.log'
$Stderr = Join-Path $Logs 'CODEX_server_smoke_stderr.log'
Remove-Item -LiteralPath $Stdout -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $Stderr -Force -ErrorAction SilentlyContinue

function Invoke-PahSmokeEndpoint {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Uri,
        [int]$TimeoutSec = 10
    )
    $Timer = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $Payload = Invoke-RestMethod -Uri $Uri -TimeoutSec $TimeoutSec
        $Timer.Stop()
        [pscustomobject]@{
            name = $Name
            ok = $true
            latency_ms = [int]$Timer.ElapsedMilliseconds
            timed_out = $false
            error = ''
            payload = $Payload
        }
    }
    catch {
        $Timer.Stop()
        [pscustomobject]@{
            name = $Name
            ok = $false
            latency_ms = [int]$Timer.ElapsedMilliseconds
            timed_out = $Timer.Elapsed.TotalSeconds -ge $TimeoutSec
            error = $_.Exception.Message
            payload = $null
        }
    }
}

function Select-PahEndpointSummary {
    param([Parameter(Mandatory = $true)]$Result)
    [pscustomobject]@{
        name = $Result.name
        ok = $Result.ok
        latency_ms = $Result.latency_ms
        timed_out = $Result.timed_out
        error = $Result.error
    }
}

$Process = Start-Process -FilePath python -ArgumentList @(
    "`"$App`"",
    '--host',
    '127.0.0.1',
    '--port',
    '8765',
    '--no-browser'
) -WindowStyle Hidden -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr -PassThru

try {
    $Url = $null
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 250
        if (Test-Path -LiteralPath $Stdout) {
            $line = Get-Content -LiteralPath $Stdout -ErrorAction SilentlyContinue | Select-String -Pattern 'PANDA Agent Hub running at ' | Select-Object -Last 1
            if ($line) {
                $Url = ($line.Line -replace '^.*PANDA Agent Hub running at ', '').Trim()
                break
            }
        }
    }
    if (-not $Url) {
        throw "PAH server did not print a startup URL."
    }

    $Ping = Invoke-PahSmokeEndpoint -Name 'ping' -Uri "$Url/api/ping" -TimeoutSec 15
    if (-not $Ping.ok) {
        throw "PAH server did not pass /api/ping readiness: $($Ping.error)"
    }
    $Ready = Invoke-PahSmokeEndpoint -Name 'ready' -Uri "$Url/api/ready" -TimeoutSec 5
    $Health = Invoke-PahSmokeEndpoint -Name 'health' -Uri "$Url/api/health" -TimeoutSec 35
    $Cockpit = Invoke-PahSmokeEndpoint -Name 'cockpit' -Uri "$Url/api/cockpit" -TimeoutSec 35
    $Status = if ($Cockpit.payload) { $Cockpit.payload } else { $null }
    $PerformanceOk = $Health.ok -and $Cockpit.ok -and $Health.latency_ms -lt 10000 -and $Cockpit.latency_ms -lt 10000
    [pscustomobject]@{
        url = $Url
        readiness_ok = $Ping.ok -and $Ready.ok
        performance_ok = $PerformanceOk
        messages = if ($Status) { $Status.cockpit_state.counts.messages } else { $null }
        threads = if ($Status) { $Status.cockpit_state.counts.threads_all } else { $null }
        decisions = if ($Status) { $Status.cockpit_state.counts.decisions_needed } else { $null }
        diagnostics_ok = if ($Status) { $Status.diagnostics.ok } else { $null }
        endpoints = @(
            Select-PahEndpointSummary $Ping
            Select-PahEndpointSummary $Ready
            Select-PahEndpointSummary $Health
            Select-PahEndpointSummary $Cockpit
        )
    } | ConvertTo-Json -Compress
}
finally {
    if ($Process -and -not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force
        $Process.WaitForExit()
    }
}
