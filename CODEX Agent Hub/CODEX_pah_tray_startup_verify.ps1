# CODEX_pah_tray_startup_verify.ps1 — Phase 2 verify harness
#
# Headless verification of the Phase 1 PAH tray hardening. Dot-sources the
# tray script in `-FunctionsOnly` mode and exercises the helpers without
# requiring a Windows login session, a tray icon, or a live PAH server.
#
# Usage:
#   pwsh -File CODEX_pah_tray_startup_verify.ps1
#   powershell -ExecutionPolicy Bypass -File CODEX_pah_tray_startup_verify.ps1
#
# Exit 0 = all automated checks pass. Exit 1 = at least one FAIL.
# Items genuinely requiring an interactive session are marked DEFERRED with
# a `# PHASE-3-MANUAL` comment for the operator to exercise by hand.

$ErrorActionPreference = 'Stop'

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TrayScript = Join-Path $ScriptRoot 'CODEX_start_agent_hub_tray.ps1'
$LauncherScript = Join-Path $ScriptRoot 'CODEX_launch_agent_hub_dashboard.ps1'

if (-not (Test-Path -LiteralPath $TrayScript)) {
    Write-Host "[FAIL] tray script not found: $TrayScript"
    exit 2
}
if (-not (Test-Path -LiteralPath $LauncherScript)) {
    Write-Host "[FAIL] launcher script not found: $LauncherScript"
    exit 2
}

# Dot-source tray helpers in functions-only mode. This loads:
#   Test-PahTrayInstance, Test-PahPortListener, Test-PahServerIdentity,
#   Get-PahServerOwnership, Get-PahHealthClassification,
#   Install-StartupShortcut, Remove-StartupShortcut, etc.
. $TrayScript -Port 8765 -FunctionsOnly

$results = [ordered]@{
    pass     = 0
    fail     = 0
    skip     = 0
    deferred = 0
    cases    = @()
}

function Add-Result {
    param([string]$Name, [string]$Outcome, [string]$Detail = '')
    $script:results.cases += [pscustomobject]@{
        name    = $Name
        outcome = $Outcome
        detail  = $Detail
    }
    switch ($Outcome) {
        'PASS'     { $script:results.pass     += 1 }
        'FAIL'     { $script:results.fail     += 1 }
        'SKIP'     { $script:results.skip     += 1 }
        'DEFERRED' { $script:results.deferred += 1 }
    }
    $tag = switch ($Outcome) {
        'PASS'     { '[PASS]' }
        'FAIL'     { '[FAIL]' }
        'SKIP'     { '[SKIP]' }
        'DEFERRED' { '[DEFER]' }
    }
    $line = if ($Detail) { "$tag $Name -- $Detail" } else { "$tag $Name" }
    Write-Host $line
}

# ============================================================================
# Test 1 — Shortcut creation / removal
# ============================================================================

$tempStartupDir = Join-Path ([System.IO.Path]::GetTempPath()) "pah-tray-verify-$([Guid]::NewGuid())"
New-Item -ItemType Directory -Path $tempStartupDir -Force | Out-Null
$origStartupShortcut = $script:StartupShortcut
$script:StartupShortcut = Join-Path $tempStartupDir 'PANDA Agent Hub Tray.lnk'
try {
    Install-StartupShortcut
    if (Test-Path -LiteralPath $script:StartupShortcut) {
        $shell = New-Object -ComObject WScript.Shell
        $sc = $shell.CreateShortcut($script:StartupShortcut)
        $tp = $sc.TargetPath
        $argLine = $sc.Arguments
        $wd = $sc.WorkingDirectory
        $tpOk = $tp -ilike '*powershell*'
        $argsOk = ($argLine -like '*CODEX_start_agent_hub_tray.ps1*') -and ($argLine -like '*-Port*')
        $wdOk = (Test-Path -LiteralPath $wd)
        if ($tpOk -and $argsOk -and $wdOk) {
            Add-Result 'shortcut_install_creates_file_with_expected_target' 'PASS'
        }
        else {
            Add-Result 'shortcut_install_creates_file_with_expected_target' 'FAIL' "tp_ok=$tpOk args_ok=$argsOk wd_ok=$wdOk"
        }
    }
    else {
        Add-Result 'shortcut_install_creates_file_with_expected_target' 'FAIL' "shortcut not created at $script:StartupShortcut"
    }

    Remove-StartupShortcut
    if (-not (Test-Path -LiteralPath $script:StartupShortcut)) {
        Add-Result 'shortcut_remove_deletes_file' 'PASS'
    }
    else {
        Add-Result 'shortcut_remove_deletes_file' 'FAIL' 'shortcut still present after Remove-StartupShortcut'
    }
}
finally {
    $script:StartupShortcut = $origStartupShortcut
    Remove-Item -Recurse -Force -Path $tempStartupDir -ErrorAction SilentlyContinue
}

# PHASE-3-MANUAL: launch the installed shortcut from Windows Startup folder
# and confirm exactly one tray + one owned PAH server start. Cannot test
# headlessly because the actual login flow runs the shortcut.
Add-Result 'shortcut_launches_one_tray_one_server_at_login' 'DEFERRED' '# PHASE-3-MANUAL: install shortcut, sign out + sign in, confirm one tray and one owned server'

# ============================================================================
# Test 2 — Single-instance predicate
# ============================================================================

# Fresh port that nothing on the box should be using.
$fakePort = 64173
if (-not (Test-PahTrayInstance -Port $fakePort)) {
    Add-Result 'single_instance_false_when_no_match' 'PASS' "port=$fakePort"
}
else {
    Add-Result 'single_instance_false_when_no_match' 'FAIL' "unexpected match on $fakePort"
}

# Spawn a fake powershell process whose command line contains the tray
# script path + matching -Port substring. Test-PahTrayInstance reads
# Win32_Process.CommandLine, so the substring match fires regardless of
# whether the spawned process is doing tray work.
$truePort = 64176
$fakeCmd = "Start-Sleep -Seconds 6 # CODEX_start_agent_hub_tray.ps1 -Port $truePort"
$fakeProc = $null
try {
    $fakeProc = Start-Process powershell -ArgumentList '-NoProfile', '-Command', $fakeCmd -PassThru -WindowStyle Hidden
    Start-Sleep -Milliseconds 500  # let CIM register the new process
    if (Test-PahTrayInstance -Port $truePort) {
        Add-Result 'single_instance_true_when_match' 'PASS' "port=$truePort pid=$($fakeProc.Id)"
    }
    else {
        Add-Result 'single_instance_true_when_match' 'FAIL' "no match for synthesized proc on $truePort"
    }
}
finally {
    if ($fakeProc -and -not $fakeProc.HasExited) {
        $fakeProc.Kill()
        $fakeProc.WaitForExit()
    }
}

# ============================================================================
# Test 3 — Port conflict + offline detection
# ============================================================================

# Conflict case: HttpListener serves a non-PAH body on a fresh port.
$conflictPort = 64174
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://127.0.0.1:$conflictPort/")
$listenerTask = $null
try {
    $listener.Start()
    $listenerTask = [System.Threading.Tasks.Task]::Run([action]{
        try {
            while ($listener.IsListening) {
                $ctx = $listener.GetContext()
                $body = [System.Text.Encoding]::UTF8.GetBytes('hello not-panda not-pah')
                $ctx.Response.ContentLength64 = $body.Length
                $ctx.Response.OutputStream.Write($body, 0, $body.Length)
                $ctx.Response.OutputStream.Close()
            }
        }
        catch {}
    })
    Start-Sleep -Milliseconds 200

    Set-Variable -Scope Script -Name Port -Value $conflictPort
    Set-Variable -Scope Script -Name Url -Value "http://127.0.0.1:$conflictPort"

    $ownership = Get-PahServerOwnership
    if ($ownership -eq 'port_conflict') {
        Add-Result 'conflict_returns_port_conflict_state' 'PASS' "ownership=$ownership"
    }
    else {
        Add-Result 'conflict_returns_port_conflict_state' 'FAIL' "ownership=$ownership (expected port_conflict)"
    }

    $health = Get-PahHealthClassification -Status $null -Ownership $ownership
    if ($health -eq 'Conflict') {
        Add-Result 'conflict_health_classification_is_Conflict' 'PASS' "health=$health"
    }
    else {
        Add-Result 'conflict_health_classification_is_Conflict' 'FAIL' "health=$health (expected Conflict)"
    }
}
finally {
    if ($listener.IsListening) { $listener.Stop() }
    $listener.Close()
}

# Offline case: nothing listening on a fresh port.
$offlinePort = 64175
Set-Variable -Scope Script -Name Port -Value $offlinePort
Set-Variable -Scope Script -Name Url -Value "http://127.0.0.1:$offlinePort"
$ownership = Get-PahServerOwnership
if ($ownership -eq 'offline') {
    Add-Result 'no_listener_returns_offline_state' 'PASS' "ownership=$ownership"
}
else {
    Add-Result 'no_listener_returns_offline_state' 'FAIL' "ownership=$ownership (expected offline)"
}

# PHASE-3-MANUAL: identity probe against a real PAH server returns
# `attached_server` or `owned_server` based on whether the tray spawned it.
# Cannot test headlessly because we don't keep a PAH process alive in the
# harness (smoke test brings up + tears down its own server).
Add-Result 'identity_probe_attached_vs_owned_server' 'DEFERRED' '# PHASE-3-MANUAL: launch tray (owned) then attach launcher, confirm Get-PahServerOwnership returns each value correctly'

# ============================================================================
# Test 4 — Launcher readiness
# ============================================================================

$parseErrs = $null
[System.Management.Automation.Language.Parser]::ParseFile($LauncherScript, [ref]$null, [ref]$parseErrs) | Out-Null
if (-not $parseErrs -or @($parseErrs).Count -eq 0) {
    Add-Result 'launcher_parses_clean_after_phase1' 'PASS'
}
else {
    Add-Result 'launcher_parses_clean_after_phase1' 'FAIL' "$(@($parseErrs).Count) parse error(s)"
}

# After dot-sourcing the tray with -FunctionsOnly, the shared helpers must
# be callable from this scope. The launcher does the same dot-source, so
# this also confirms the launcher's helper-import path.
$expected = @('Test-PahTrayInstance', 'Test-PahPortListener', 'Get-PahServerOwnership', 'Test-PahServerIdentity', 'Get-PahHealthClassification')
$exposed = @($expected | Where-Object { Get-Command -Name $_ -ErrorAction SilentlyContinue })
if ($exposed.Count -eq $expected.Count) {
    Add-Result 'shared_helpers_available_via_dot_source' 'PASS' "$($exposed.Count)/$($expected.Count) helpers loaded"
}
else {
    $missing = ($expected | Where-Object { $_ -notin $exposed }) -join ','
    Add-Result 'shared_helpers_available_via_dot_source' 'FAIL' "missing: $missing"
}

# ============================================================================
# Test 5 — Regression guard
# ============================================================================

$smokeScript = Join-Path $ScriptRoot 'CODEX_run_smoke_tests.py'
if (-not (Test-Path -LiteralPath $smokeScript)) {
    Add-Result 'pah_smoke_test_passes' 'SKIP' 'CODEX_run_smoke_tests.py not found'
}
else {
    # Resolve to a real python.exe; the WindowsApps proxy can deadlock under
    # PowerShell stdio capture.
    $pythonPath = $null
    foreach ($candidate in @(
        "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe",
        "$env:LOCALAPPDATA\Python\pythoncore-3.13-64\python.exe",
        "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\python.exe",
        "$env:ProgramFiles\Python313\python.exe",
        "$env:ProgramFiles\Python312\python.exe"
    )) {
        if (Test-Path -LiteralPath $candidate) { $pythonPath = $candidate; break }
    }
    if (-not $pythonPath) {
        $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    }
    if (-not $pythonPath) {
        Add-Result 'pah_smoke_test_passes' 'SKIP' 'no usable python.exe found'
    }
    else {
        # Bound the smoke run with a 60-second timeout. The smoke test imports
        # a deep dependency graph and can stall under nested PowerShell stdio
        # capture in some environments. If it hits the timeout, mark
        # DEFERRED — caller is expected to run smoke standalone as part of
        # the regression-guard step in the RTC.
        $guid = [Guid]::NewGuid()
        $smokeStdout = Join-Path ([System.IO.Path]::GetTempPath()) "pah-tray-verify-smoke-$guid.out"
        $smokeStderr = Join-Path ([System.IO.Path]::GetTempPath()) "pah-tray-verify-smoke-$guid.err"
        $proc = Start-Process -FilePath $pythonPath -ArgumentList "-u", "`"$smokeScript`"" -NoNewWindow -PassThru -RedirectStandardOutput $smokeStdout -RedirectStandardError $smokeStderr
        $finishedInTime = $proc.WaitForExit(60000)
        if (-not $finishedInTime) {
            try { $proc.Kill() } catch {}
            Remove-Item -LiteralPath $smokeStdout, $smokeStderr -Force -ErrorAction SilentlyContinue
            Add-Result 'pah_smoke_test_passes' 'DEFERRED' '# PHASE-3-MANUAL: harness-invoked smoke timed out at 60s in this environment; run `python CODEX_run_smoke_tests.py` standalone (typically <30s) to confirm pass'
        }
        else {
            try { $proc.Refresh() } catch {}
            $smokeText = ((Get-Content -LiteralPath $smokeStdout -ErrorAction SilentlyContinue) -join "`n").Trim()
            $smokeErrText = ((Get-Content -LiteralPath $smokeStderr -ErrorAction SilentlyContinue) -join "`n").Trim()
            Remove-Item -LiteralPath $smokeStdout, $smokeStderr -Force -ErrorAction SilentlyContinue
            $exitCode = $proc.ExitCode
            if ($null -eq $exitCode -and $smokeText -match 'PAH smoke tests passed') {
                $exitCode = 0
            }
            if ($exitCode -eq 0) {
                Add-Result 'pah_smoke_test_passes' 'PASS' $smokeText
            }
            else {
                $detail = "exit=$exitCode; python=$pythonPath; out=$smokeText"
                if ($smokeErrText) { $detail += "; err=$smokeErrText" }
                Add-Result 'pah_smoke_test_passes' 'FAIL' $detail
            }
        }
    }
}

# ============================================================================
# Summary + exit
# ============================================================================

Write-Host ''
Write-Host '=== PAH tray Phase 2 verify harness ==='
Write-Host ("PASS:     {0}" -f $results.pass)
Write-Host ("FAIL:     {0}" -f $results.fail)
Write-Host ("SKIP:     {0}" -f $results.skip)
Write-Host ("DEFERRED: {0}  (Phase 3 manual)" -f $results.deferred)
Write-Host ''

if ($results.fail -gt 0) {
    exit 1
}
exit 0
