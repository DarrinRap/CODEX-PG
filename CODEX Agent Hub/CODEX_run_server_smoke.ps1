$ErrorActionPreference = 'Stop'

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$App = Join-Path $ScriptRoot 'CODEX_agent_hub.py'
$Logs = Join-Path $ScriptRoot 'CODEX logs'
New-Item -ItemType Directory -Force -Path $Logs | Out-Null

$Stdout = Join-Path $Logs 'CODEX_server_smoke_stdout.log'
$Stderr = Join-Path $Logs 'CODEX_server_smoke_stderr.log'
Remove-Item -LiteralPath $Stdout -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $Stderr -Force -ErrorAction SilentlyContinue

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

    $Status = Invoke-RestMethod -Uri "$Url/api/status" -TimeoutSec 10
    [pscustomobject]@{
        url = $Url
        messages = $Status.counts.messages
        threads = $Status.counts.threads
        decisions = $Status.counts.decisions
        diagnostics_ok = $Status.diagnostics.ok
    } | ConvertTo-Json -Compress
}
finally {
    if ($Process -and -not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force
        $Process.WaitForExit()
    }
}

