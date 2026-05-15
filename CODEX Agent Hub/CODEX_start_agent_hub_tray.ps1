param(
    [int]$Port = 8765,
    [int]$PollSeconds = 15,
    [int]$AlertCooldownMinutes = 60,
    [int]$RestartMaxAttempts = 3,
    [int]$RestartCooldownMinutes = 10,
    [switch]$NoServer,
    [switch]$FunctionsOnly  # Phase 1: dot-source mode for the launcher; defines helpers and returns without starting a tray.
)

$ErrorActionPreference = 'Stop'

function Enable-PahDpiAwareRendering {
    $typeName = 'PahTrayDpiNative'
    if (-not ($typeName -as [type])) {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class PahTrayDpiNative {
    [DllImport("user32.dll")]
    public static extern bool SetProcessDPIAware();

    [DllImport("user32.dll", EntryPoint="SetProcessDpiAwarenessContext")]
    public static extern bool SetProcessDpiAwarenessContext(IntPtr dpiContext);
}
"@
    }

    try {
        # PER_MONITOR_AWARE_V2 keeps WinForms tray menus crisp on scaled displays.
        [PahTrayDpiNative]::SetProcessDpiAwarenessContext([IntPtr](-4)) | Out-Null
        return
    }
    catch {
    }

    try {
        [PahTrayDpiNative]::SetProcessDPIAware() | Out-Null
    }
    catch {
    }
}

# Skip the STA re-invoke when used as a helper library — the launcher just
# needs the function definitions, not a running tray.
if (-not $FunctionsOnly -and [Threading.Thread]::CurrentThread.ApartmentState -ne 'STA') {
    $argsList = @(
        '-NoProfile',
        '-STA',
        '-ExecutionPolicy',
        'Bypass',
        '-WindowStyle',
        'Hidden',
        '-File',
        "`"$PSCommandPath`"",
        '-Port',
        "$Port",
        '-PollSeconds',
        "$PollSeconds",
        '-AlertCooldownMinutes',
        "$AlertCooldownMinutes"
    )
    if ($NoServer) {
        $argsList += '-NoServer'
    }
    Start-Process -FilePath powershell.exe -ArgumentList $argsList -WindowStyle Hidden
    exit
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName Microsoft.VisualBasic -ErrorAction SilentlyContinue

if (-not $FunctionsOnly) {
    Enable-PahDpiAwareRendering
    [System.Windows.Forms.Application]::EnableVisualStyles()
    [System.Windows.Forms.Application]::SetCompatibleTextRenderingDefault($false)
}

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$App = Join-Path $ScriptRoot 'CODEX_agent_hub.py'
$Logs = Join-Path $ScriptRoot 'CODEX logs'
$Config = Join-Path $ScriptRoot 'CODEX config'
$Assets = Join-Path $ScriptRoot 'CODEX assets'
$Notifications = Join-Path $ScriptRoot 'CODEX notifications'
$StartupShortcut = Join-Path ([Environment]::GetFolderPath('Startup')) 'PANDA Agent Hub Tray.lnk'
$TrayIconPath = Join-Path $Assets 'PANDA_Agent_Hub_panda_tray.ico'
New-Item -ItemType Directory -Force -Path $Logs | Out-Null
New-Item -ItemType Directory -Force -Path $Config | Out-Null
New-Item -ItemType Directory -Force -Path $Assets | Out-Null
New-Item -ItemType Directory -Force -Path $Notifications | Out-Null

$Stdout = Join-Path $Logs 'CODEX_agent_hub_tray_stdout.log'
$Stderr = Join-Path $Logs 'CODEX_agent_hub_tray_stderr.log'
$NotificationLog = Join-Path $Notifications 'CODEX_notification_log.jsonl'
$TrayLifecycleLog = Join-Path $Logs 'CODEX_pah_tray_lifecycle.jsonl'
$ServerLifecycleLog = Join-Path $Logs 'CODEX_pah_server_lifecycle.jsonl'
$HealthTransitionLog = Join-Path $Logs 'CODEX_pah_health_transitions.jsonl'
$TrayConfigPath = Join-Path $Config 'CODEX_pah_tray_config.json'
# Functions-only callers (e.g. the launcher) must not clobber a running
# tray's stdout/stderr capture.
if (-not $FunctionsOnly) {
    Remove-Item -LiteralPath $Stdout -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $Stderr -Force -ErrorAction SilentlyContinue
}

$script:Url = "http://127.0.0.1:$Port"
$script:Process = $null
$script:StartedServer = $false
$script:OwnershipState = 'offline'   # offline | owned_server | attached_server | port_conflict
$script:DisplayState = 'starting'    # Running | Warn | Starting | Down | Conflict | Restarting
$script:LastDisplayState = ''
$script:ReadinessFailures = 0
$script:RestartTimestamps = @()      # list of [datetime] of recent restart attempts (sliding window)
$script:RestartAttempts = 0
$script:LastObservedServerExitPid = $null
$script:LastAlertKey = ''
$script:LastStaleUnread = -1
$script:LastUrgentCodex = -1
$script:LastAlertAt = [datetime]::MinValue
$script:AlertsEnabled = $false
$script:SnoozeUntil = [datetime]::MaxValue
$script:NotificationLogPopupsEnabled = $false
$script:NotificationPosition = 0
$script:TrayPopupsDisabled = $true
$script:SuppressPahStartupMessage = $false

function New-PahLaunchUrl {
    return $script:Url
}

function Invoke-PahDashboardRefresh {
    try {
        $body = @{ source = 'pah-tray-open' } | ConvertTo-Json -Compress
        $response = Invoke-RestMethod -Uri "$script:Url/api/launch-refresh/request" -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 2
        if (-not $response.ok -or [int]$response.active_clients -lt 1) {
            return $false
        }
        $token = [string]$response.token
        for ($i = 0; $i -lt 30; $i++) {
            Start-Sleep -Milliseconds 150
            $state = Invoke-RestMethod -Uri "$script:Url/api/launch-refresh/state" -TimeoutSec 2
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
    if (Invoke-PahDashboardRefresh) {
        return
    }

    Start-Process (New-PahLaunchUrl)
}

function Limit-Text {
    param([string]$Text, [int]$Max = 60)
    if ([string]::IsNullOrWhiteSpace($Text)) { return 'PANDA Agent Hub' }
    if ($Text.Length -le $Max) { return $Text }
    return $Text.Substring(0, [Math]::Max(0, $Max - 3)) + '...'
}

function Get-PahTrayIcon {
    if (Test-Path -LiteralPath $TrayIconPath) {
        try {
            return New-Object System.Drawing.Icon $TrayIconPath
        }
        catch {
        }
    }
    return [System.Drawing.SystemIcons]::Application
}

function Invoke-PahJson {
    param([string]$Path)
    $uri = "$script:Url$Path"
    try {
        return Invoke-RestMethod -Uri $uri -Method Get -TimeoutSec 4
    }
    catch {
        return $null
    }
}

function Test-PahServer {
    # Backward-compatible port-listener probe. Public — callers (incl.
    # CODEX_launch_agent_hub_dashboard.ps1) depend on this name. Phase 1
    # introduces ownership-aware variants below; this one stays simple.
    return Test-PahPortListener -Port $Port
}

# ==========================================================================
#  Phase 1 hardening — config, ownership, health, restart, logging
# ==========================================================================

function Get-PahTrayConfig {
    if (Test-Path -LiteralPath $TrayConfigPath) {
        try {
            return Get-Content -LiteralPath $TrayConfigPath -Raw | ConvertFrom-Json
        }
        catch {
        }
    }
    $defaults = [pscustomobject]@{
        port = $Port
        poll_seconds = $PollSeconds
        alert_popups_enabled = $false
        auto_open_dashboard_at_login = $false
        restart_max_attempts = $RestartMaxAttempts
        restart_cooldown_minutes = $RestartCooldownMinutes
    }
    try {
        $defaults | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $TrayConfigPath -Encoding UTF8
    }
    catch {
    }
    return $defaults
}

function Write-PahJsonlEvent {
    param([string]$LogPath, [hashtable]$Payload)
    $Payload['timestamp'] = (Get-Date).ToString('o')
    try {
        $line = $Payload | ConvertTo-Json -Compress -Depth 6
        Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
    }
    catch {
    }
}

function Write-PahLifecycleEvent {
    param([string]$Event, [hashtable]$Extra = @{})
    $payload = @{
        event = $Event
        port = $Port
        ownership_state = $script:OwnershipState
        startup_shortcut_installed = (Test-Path -LiteralPath $StartupShortcut)
    }
    foreach ($k in $Extra.Keys) { $payload[$k] = $Extra[$k] }
    Write-PahJsonlEvent -LogPath $TrayLifecycleLog -Payload $payload
}

function Write-PahServerLifecycle {
    param([string]$Event, [hashtable]$Extra = @{})
    $procPid = if ($script:Process) { $script:Process.Id } else { $null }
    $payload = @{
        event = $Event
        port = $Port
        pid = $procPid
        stdout_log = $Stdout
        stderr_log = $Stderr
    }
    foreach ($k in $Extra.Keys) { $payload[$k] = $Extra[$k] }
    Write-PahJsonlEvent -LogPath $ServerLifecycleLog -Payload $payload
}

function Write-PahHealthTransition {
    param([string]$From, [string]$To, [hashtable]$Extra = @{})
    $payload = @{
        event = 'health_state_transition'
        from_state = $From
        to_state = $To
        ownership_state = $script:OwnershipState
        port = $Port
    }
    foreach ($k in $Extra.Keys) { $payload[$k] = $Extra[$k] }
    Write-PahJsonlEvent -LogPath $HealthTransitionLog -Payload $payload
}

function Test-PahTrayInstance {
    # Single-instance helper. Callable from launcher via dot-source.
    # Returns $true if another tray process is bound to the same port,
    # excluding the calling process.
    param([int]$Port = 8765)
    $self = $PID
    $matches = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -like '*CODEX_start_agent_hub_tray.ps1*' -and
            $_.CommandLine -like "*-Port $Port*" -and
            $_.ProcessId -ne $self
        }
    return $null -ne $matches
}

function Test-PahPortListener {
    param([int]$Port, [int]$TimeoutMs = 800)
    $client = $null
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $connect = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $connect.AsyncWaitHandle.WaitOne($TimeoutMs)) {
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

function Test-PahServerIdentity {
    # /api/ping is the cheap PAH-identity probe. A non-PAH listener on the
    # same port either won't expose /api/ping or will return non-PAH content.
    try {
        $response = Invoke-WebRequest -Uri "$script:Url/api/ping" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -ne 200) { return $false }
        $body = [string]$response.Content
        return ($body -like '*panda*' -or $body -like '*pah*' -or $body -like '*"ok"*')
    }
    catch {
        return $false
    }
}

function Get-PahServerOwnership {
    if (-not (Test-PahPortListener -Port $Port)) {
        return 'offline'
    }
    if (-not (Test-PahServerIdentity)) {
        return 'port_conflict'
    }
    if ($script:Process -and -not $script:Process.HasExited) {
        return 'owned_server'
    }
    return 'attached_server'
}

function Get-PahHealthClassification {
    param($Status, [string]$Ownership)
    if ($Ownership -eq 'port_conflict') { return 'Conflict' }
    if ($Ownership -eq 'offline') {
        if ($script:Process -and -not $script:Process.HasExited) {
            return 'Starting'
        }
        return 'Down'
    }
    if ($null -eq $Status) { return 'Warn' }
    if ($Status.level -and $Status.level -match 'warn') { return 'Warn' }
    return 'Running'
}

function Update-PahDisplayState {
    param([string]$NewState, [hashtable]$Extra = @{})
    if ($script:LastDisplayState -eq $NewState) { return }
    Write-PahHealthTransition -From $script:LastDisplayState -To $NewState -Extra $Extra
    $script:LastDisplayState = $NewState
    $script:DisplayState = $NewState
}

function Reset-RestartWindow {
    $cutoff = (Get-Date).AddMinutes(-$RestartCooldownMinutes)
    $script:RestartTimestamps = @($script:RestartTimestamps | Where-Object { $_ -ge $cutoff })
    $script:RestartAttempts = $script:RestartTimestamps.Count
}

function Invoke-PahBoundedRestart {
    # Bounded restart per spec §4.5. Only allowed for owned_server (Q6 ruling).
    # Returns $true if a restart attempt was made.
    $ownedExitedServer = (
        $script:StartedServer -and
        $script:Process -and
        $script:Process.HasExited -and
        $script:OwnershipState -eq 'offline'
    )
    if ($script:OwnershipState -ne 'owned_server' -and -not $ownedExitedServer) {
        Write-PahServerLifecycle -Event 'restart_skipped' -Extra @{
            reason = 'not_owned_server'
            ownership_state = $script:OwnershipState
        }
        return $false
    }
    Reset-RestartWindow
    if ($script:RestartAttempts -ge $RestartMaxAttempts) {
        Write-PahServerLifecycle -Event 'restart_blocked' -Extra @{
            reason = 'max_attempts_in_window'
            attempts = $script:RestartAttempts
            window_minutes = $RestartCooldownMinutes
        }
        return $false
    }
    $script:RestartTimestamps += (Get-Date)
    $script:RestartAttempts = $script:RestartTimestamps.Count
    Write-PahServerLifecycle -Event 'restart_attempt' -Extra @{
        attempt = $script:RestartAttempts
        max_attempts = $RestartMaxAttempts
        readiness_failures = $script:ReadinessFailures
        owned_exited_server = [bool]$ownedExitedServer
    }
    Update-PahDisplayState -NewState 'Restarting' -Extra @{ attempt = $script:RestartAttempts }
    Start-PahServer
    return $true
}

function Invoke-PahHealthCheck {
    # Bounded local check (spec §4.7). Does NOT spawn a temp server.
    $results = [ordered]@{
        ping = $null
        ready = $null
        tray_status = $null
        health = $null
    }
    foreach ($endpoint in @('ping', 'ready', 'tray-status', 'health')) {
        try {
            $response = Invoke-WebRequest -Uri "$script:Url/api/$endpoint" -UseBasicParsing -TimeoutSec 4
            $key = ($endpoint -replace '-', '_')
            $results[$key] = [int]$response.StatusCode
        }
        catch {
            $key = ($endpoint -replace '-', '_')
            $results[$key] = $null
        }
    }
    Write-PahJsonlEvent -LogPath $HealthTransitionLog -Payload @{
        event = 'health_check_result'
        port = $Port
        ownership_state = $script:OwnershipState
        ping = $results.ping
        ready = $results.ready
        tray_status = $results.tray_status
        health = $results.health
    }
    return $results
}

function Copy-PahStatusSummary {
    $status = Invoke-PahJson '/api/tray-status'
    $lines = @(
        'PANDA Agent Hub — tray status',
        "URL: $script:Url",
        "Ownership: $script:OwnershipState",
        "Display: $script:DisplayState",
        "Port: $Port",
        "Captured: $((Get-Date).ToString('o'))"
    )
    if ($status) {
        $lines += "Title: $($status.title)"
        $lines += "Unread: $($status.counts.unread)  overdue: $($status.counts.stale_unread)  urgent: $($status.counts.urgent_codex_requests)"
        $lines += "Decisions: $($status.counts.decisions_needed)  diagnostics: $($status.counts.diagnostic_problems)"
    }
    else {
        $lines += 'Status: <unreachable>'
    }
    $text = $lines -join [Environment]::NewLine
    try {
        Set-Clipboard -Value $text
    }
    catch {
    }
}

function Read-ServerUrlFromLog {
    if (-not (Test-Path -LiteralPath $Stdout)) {
        return $null
    }
    $line = Get-Content -LiteralPath $Stdout -ErrorAction SilentlyContinue |
        Select-String -Pattern 'PANDA Agent Hub running at ' |
        Select-Object -Last 1
    if ($line) {
        return ($line.Line -replace '^.*PANDA Agent Hub running at ', '').Trim()
    }
    return $null
}

function Get-PahServerPythonExecutable {
    # Prefer pythonw.exe for tray-owned server launches so the background
    # server cannot create a blank console window. Avoid WindowsApps shim
    # launchers because they can spawn a real child process and leave the tray
    # tracking the wrapper PID instead of the server listener.
    foreach ($candidate in @(
        "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\pythonw.exe",
        "$env:LOCALAPPDATA\Python\pythoncore-3.13-64\pythonw.exe",
        "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\pythonw.exe",
        "$env:ProgramFiles\Python314\pythonw.exe",
        "$env:ProgramFiles\Python313\pythonw.exe",
        "$env:ProgramFiles\Python312\pythonw.exe"
    )) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python -and $python.Source) {
        $siblingPythonw = Join-Path (Split-Path -Parent $python.Source) 'pythonw.exe'
        if ((Test-Path -LiteralPath $siblingPythonw) -and $siblingPythonw -notlike '*\WindowsApps\*') {
            return $siblingPythonw
        }
    }
    $pythonw = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($pythonw -and $pythonw.Source -and $pythonw.Source -notlike '*\WindowsApps\*') {
        return $pythonw.Source
    }
    if ($python -and $python.Source) {
        return $python.Source
    }
    return 'python'
}

function Start-PahServer {
    if ($NoServer) {
        return
    }
    $arguments = @(
        "`"$App`"",
        '--host',
        '127.0.0.1',
        '--port',
        "$Port",
        '--no-port-fallback',
        '--no-browser'
    )
    $serverPython = Get-PahServerPythonExecutable
    $script:Process = Start-Process -FilePath $serverPython -ArgumentList $arguments -WindowStyle Hidden -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr -PassThru
    $script:StartedServer = $true
    $script:OwnershipState = 'owned_server'
    $script:LastObservedServerExitPid = $null
    Write-PahServerLifecycle -Event 'server_started' -Extra @{
        cmd = "$serverPython $($arguments -join ' ')"
        url = $script:Url
    }
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 250
        $fromLog = Read-ServerUrlFromLog
        if ($fromLog) {
            $script:Url = $fromLog
            return
        }
    }
}

function Show-PahBalloon {
    param([string]$Title, [string]$Message, [int]$Ms = 8000)
    if ($script:TrayPopupsDisabled) {
        return
    }
    return
}

function Alert-CooldownElapsed {
    return ((Get-Date) - $script:LastAlertAt).TotalMinutes -ge $AlertCooldownMinutes
}

function Alerts-AreActive {
    return $script:AlertsEnabled -and (Get-Date) -ge $script:SnoozeUntil
}

function Update-AlertMenuText {
    $AlertsToggleItem.Text = 'Overdue popups: Disabled'
    $SnoozeItem.Text = 'Snooze overdue popups (disabled)'
}

function Update-NotificationMenuText {
    $NotificationToggleItem.Text = 'Notification-log popups: Disabled'
}

function Set-NotificationPositionToEnd {
    if (Test-Path -LiteralPath $NotificationLog) {
        $script:NotificationPosition = (Get-Item -LiteralPath $NotificationLog).Length
        return
    }
    $script:NotificationPosition = 0
}

function Dismiss-CurrentAlerts {
    $status = Invoke-PahJson '/api/tray-status'
    if ($null -ne $status) {
        $stale = [int]$status.counts.stale_unread
        $urgent = [int]$status.counts.urgent_codex_requests
        $script:LastAlertKey = "$($status.level)|$stale|$urgent"
        $script:LastStaleUnread = $stale
        $script:LastUrgentCodex = $urgent
    }
    $script:LastAlertAt = Get-Date
    $script:AlertsEnabled = $false
    $script:SnoozeUntil = [datetime]::MaxValue
    $script:NotificationLogPopupsEnabled = $false
    Set-NotificationPositionToEnd
    Update-AlertMenuText
    Update-NotificationMenuText
}

function Set-TrayMenuStatus {
    param($Status)
    if ($null -eq $Status) {
        $StatusItem.Text = 'Status: offline'
        $UnreadItem.Text = 'Unread: unknown'
        $UrgentItem.Text = 'Urgent: unknown'
        $DecisionItem.Text = 'Decisions: unknown'
        $DiagnosticItem.Text = 'Diagnostics: unknown'
        $NotifyIcon.Text = 'PAH offline'
        return
    }
    $counts = $Status.counts
    $StatusItem.Text = "Status: $($Status.title)"
    $UnreadItem.Text = "Unread: $($counts.unread), overdue: $($counts.stale_unread)"
    $UrgentItem.Text = "Urgent: $($counts.urgent_codex_requests)"
    $DecisionItem.Text = "Decisions: $($counts.decisions_needed)"
    $DiagnosticItem.Text = "Diagnostics: $($counts.diagnostic_problems)"
    $NotifyIcon.Text = Limit-Text $Status.tooltip 63
}

function Update-TrayStatus {
    # Refresh ownership classification + display state on every poll. Bounded
    # restart fires only when ownership is owned_server AND readiness has
    # failed twice in a row (spec §4.5 + Q6 ruling).
    $ownedChildExited = (
        $script:StartedServer -and
        $script:Process -and
        $script:Process.HasExited
    )
    if ($ownedChildExited -and $script:LastObservedServerExitPid -ne $script:Process.Id) {
        try { $script:Process.Refresh() } catch {}
        Write-PahServerLifecycle -Event 'owned_server_exited' -Extra @{
            exit_code = $script:Process.ExitCode
            prior_ownership_state = $script:OwnershipState
        }
        $script:LastObservedServerExitPid = $script:Process.Id
    }

    $script:OwnershipState = Get-PahServerOwnership
    $status = Invoke-PahJson '/api/tray-status'
    Set-TrayMenuStatus $status
    Update-RestartMenuItem
    Update-StartupMenuItems

    $newDisplay = Get-PahHealthClassification -Status $status -Ownership $script:OwnershipState
    Update-PahDisplayState -NewState $newDisplay

    if ($null -eq $status) {
        $script:ReadinessFailures += 1
        if ($ownedChildExited -and
            $script:OwnershipState -eq 'offline' -and
            -not (Test-PahPortListener -Port $Port) -and
            $script:ReadinessFailures -ge 2) {
            $attempted = Invoke-PahBoundedRestart
            if ($attempted) {
                $script:ReadinessFailures = 0
            }
        }
        return
    }
    $script:ReadinessFailures = 0

    $stale = [int]$status.counts.stale_unread
    $urgent = [int]$status.counts.urgent_codex_requests
    $alertKey = "$($status.level)|$stale|$urgent"
    if (
        ($stale -gt 0 -or $urgent -gt 0) -and
        (Alerts-AreActive) -and
        (Alert-CooldownElapsed) -and
        ($script:LastAlertKey -ne $alertKey -or $stale -gt $script:LastStaleUnread -or $urgent -gt $script:LastUrgentCodex)
    ) {
        Show-PahBalloon $status.title $status.body 10000
        $script:LastAlertAt = Get-Date
    }
    $script:LastAlertKey = $alertKey
    $script:LastStaleUnread = $stale
    $script:LastUrgentCodex = $urgent
    Update-AlertMenuText
}

function Update-RestartMenuItem {
    if (-not $script:RestartItem) { return }
    $script:RestartItem.Enabled = ($script:OwnershipState -eq 'owned_server')
    $script:RestartItem.Text = if ($script:OwnershipState -eq 'owned_server') {
        'Restart PAH Server'
    }
    elseif ($script:OwnershipState -eq 'attached_server') {
        'Restart PAH Server (attached — use originator)'
    }
    elseif ($script:OwnershipState -eq 'port_conflict') {
        'Restart PAH Server (port in use by other process)'
    }
    else {
        'Restart PAH Server (offline)'
    }
}

function Update-StartupMenuItems {
    if (-not $script:InstallStartupItem -or -not $script:RemoveStartupItem) { return }
    $installed = Test-Path -LiteralPath $StartupShortcut
    $script:InstallStartupItem.Visible = -not $installed
    $script:RemoveStartupItem.Visible = $installed
}

function Install-StartupShortcut {
    # Disabled after the 2026-05-08 tray-start regression: Windows Startup
    # launches through PowerShell/wscript can surface blank terminal windows.
    # Keep startup opt-in unavailable until PAH has a proven no-console host.
    Remove-StartupShortcut
    if (-not $script:SuppressPahStartupMessage) {
        [System.Windows.Forms.MessageBox]::Show(
            'Windows Startup for PANDA Agent Hub is disabled until the tray launcher has a proven no-terminal start path.',
            'PANDA Agent Hub',
            'OK',
            'Information'
        ) | Out-Null
    }
}

function Remove-StartupShortcut {
    Remove-Item -LiteralPath $StartupShortcut -Force -ErrorAction SilentlyContinue
}

# Functions-only callers stop here — the helpers above are now defined in
# the caller's scope without spawning a tray.
if ($FunctionsOnly) {
    return
}

# Single-instance check — refuse to start a second tray on the same port.
if (Test-PahTrayInstance -Port $Port) {
    Write-PahLifecycleEvent -Event 'tray_start_skipped' -Extra @{
        reason = 'duplicate_instance_on_port'
    }
    [System.Windows.Forms.MessageBox]::Show(
        "PANDA Agent Hub tray is already running on port $Port.",
        'PANDA Agent Hub',
        'OK',
        'Information'
    ) | Out-Null
    exit
}

# Load tray config (writes defaults on first run).
$null = Get-PahTrayConfig

# Classify any existing PAH listener BEFORE deciding to start a server.
$script:OwnershipState = Get-PahServerOwnership
if ($script:OwnershipState -eq 'offline') {
    Start-PahServer
    $script:OwnershipState = Get-PahServerOwnership
}
elseif ($script:OwnershipState -eq 'port_conflict') {
    Write-PahServerLifecycle -Event 'port_conflict_detected' -Extra @{
        url = $script:Url
    }
}
Write-PahLifecycleEvent -Event 'tray_started' -Extra @{
    no_server_flag = [bool]$NoServer
}

$NotifyIcon = New-Object System.Windows.Forms.NotifyIcon
$NotifyIcon.Icon = Get-PahTrayIcon
$NotifyIcon.Text = 'PANDA Agent Hub'
$NotifyIcon.Visible = $true

$Menu = New-Object System.Windows.Forms.ContextMenuStrip
$OpenItem = $Menu.Items.Add('Open Dashboard')
$OpenItem.Add_Click({ Open-PahDashboard })

$RefreshItem = $Menu.Items.Add('Refresh Status')
$RefreshItem.Add_Click({ Update-TrayStatus })

$HealthCheckItem = $Menu.Items.Add('Run Health Check')
$HealthCheckItem.Add_Click({
    $r = Invoke-PahHealthCheck
    [System.Windows.Forms.MessageBox]::Show(
        ("Health check at $script:Url`n" +
         "ping: $($r.ping)`n" +
         "ready: $($r.ready)`n" +
         "tray-status: $($r.tray_status)`n" +
         "health: $($r.health)`n" +
         "ownership: $script:OwnershipState"),
        'PANDA Agent Hub — Health Check',
        'OK',
        'Information'
    ) | Out-Null
})

$script:RestartItem = $Menu.Items.Add('Restart PAH Server')
$script:RestartItem.Enabled = $false
$script:RestartItem.Add_Click({
    $attempted = Invoke-PahBoundedRestart
    if (-not $attempted) {
        [System.Windows.Forms.MessageBox]::Show(
            'Restart not allowed: tray is not the owner of the running PAH server, or the bounded-restart window is exhausted. See server-lifecycle log for details.',
            'PANDA Agent Hub',
            'OK',
            'Information'
        ) | Out-Null
    }
})

$CopyStatusItem = $Menu.Items.Add('Copy Status Summary')
$CopyStatusItem.Add_Click({ Copy-PahStatusSummary })

$DismissItem = $Menu.Items.Add('Dismiss current alerts')
$DismissItem.Add_Click({ Dismiss-CurrentAlerts })

$AlertsToggleItem = $Menu.Items.Add('Overdue popups: Off')
$AlertsToggleItem.Enabled = $false
$AlertsToggleItem.Add_Click({
    $script:AlertsEnabled = $false
    $script:SnoozeUntil = [datetime]::MaxValue
    Update-AlertMenuText
})

$SnoozeItem = $Menu.Items.Add('Snooze overdue popups')
$SnoozeItem.Enabled = $false
$SnoozeItem.Add_Click({
    $script:AlertsEnabled = $false
    $script:SnoozeUntil = [datetime]::MaxValue
    Update-AlertMenuText
})

$NotificationToggleItem = $Menu.Items.Add('Notification-log popups: Off')
$NotificationToggleItem.Enabled = $false
$NotificationToggleItem.Add_Click({
    $script:NotificationLogPopupsEnabled = $false
    Update-NotificationMenuText
})

$StatusItem = $Menu.Items.Add('Status: starting')
$StatusItem.Enabled = $false
$UnreadItem = $Menu.Items.Add('Unread: checking')
$UnreadItem.Enabled = $false
$UrgentItem = $Menu.Items.Add('Urgent: checking')
$UrgentItem.Enabled = $false
$DecisionItem = $Menu.Items.Add('Decisions: checking')
$DecisionItem.Enabled = $false
$DiagnosticItem = $Menu.Items.Add('Diagnostics: checking')
$DiagnosticItem.Enabled = $false

$Menu.Items.Add('-') | Out-Null

$FolderItem = $Menu.Items.Add('Open PAH Folder')
$FolderItem.Add_Click({ Start-Process $ScriptRoot })

$LogsItem = $Menu.Items.Add('Open Logs')
$LogsItem.Add_Click({ Start-Process $Logs })

$script:InstallStartupItem = $Menu.Items.Add('Install at Windows Startup')
$script:InstallStartupItem.Add_Click({
    Install-StartupShortcut
    Write-PahLifecycleEvent -Event 'startup_shortcut_installed'
    Update-StartupMenuItems
    Show-PahBalloon 'PANDA Agent Hub' 'Tray startup shortcut installed.' 5000
})

$script:RemoveStartupItem = $Menu.Items.Add('Remove Windows Startup')
$script:RemoveStartupItem.Add_Click({
    Remove-StartupShortcut
    Write-PahLifecycleEvent -Event 'startup_shortcut_removed'
    Update-StartupMenuItems
    Show-PahBalloon 'PANDA Agent Hub' 'Tray startup shortcut removed.' 5000
})

$Menu.Items.Add('-') | Out-Null

$ExitItem = $Menu.Items.Add('Exit PANDA Agent Hub')
$ExitItem.Add_Click({
    if ($StatusTimer) { $StatusTimer.Stop() }
    if ($NotificationTimer) { $NotificationTimer.Stop() }
    $NotifyIcon.Visible = $false
    # Q6 ruling: only kill the server if WE started it (owned_server). An
    # attached server stays alive — the originator owns its lifecycle.
    if ($script:OwnershipState -eq 'owned_server' -and
        $script:Process -and -not $script:Process.HasExited) {
        Write-PahServerLifecycle -Event 'server_killed_on_tray_exit'
        $script:Process.Kill()
        $script:Process.WaitForExit()
    }
    Write-PahLifecycleEvent -Event 'tray_exited' -Extra @{
        reason = 'menu_exit'
    }
    [System.Windows.Forms.Application]::Exit()
})

$NotifyIcon.ContextMenuStrip = $Menu
$NotifyIcon.Add_DoubleClick({ Open-PahDashboard })
$NotifyIcon.Text = 'PANDA Agent Hub'

Set-NotificationPositionToEnd

$StatusTimer = New-Object System.Windows.Forms.Timer
$StatusTimer.Interval = [Math]::Max(5, $PollSeconds) * 1000
$StatusTimer.Add_Tick({ Update-TrayStatus })
$StatusTimer.Start()

$NotificationTimer = $null

Update-TrayStatus
Update-AlertMenuText
Update-NotificationMenuText
[System.Windows.Forms.Application]::Run()
