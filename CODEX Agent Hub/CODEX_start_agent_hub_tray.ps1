param(
    [int]$Port = 8765,
    [int]$PollSeconds = 15,
    [int]$AlertCooldownMinutes = 60,
    [switch]$NoServer
)

$ErrorActionPreference = 'Stop'

if ([Threading.Thread]::CurrentThread.ApartmentState -ne 'STA') {
    $argsList = @(
        '-NoProfile',
        '-STA',
        '-ExecutionPolicy',
        'Bypass',
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

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$App = Join-Path $ScriptRoot 'CODEX_agent_hub.py'
$Logs = Join-Path $ScriptRoot 'CODEX logs'
$Notifications = Join-Path $ScriptRoot 'CODEX notifications'
$StartupShortcut = Join-Path ([Environment]::GetFolderPath('Startup')) 'PANDA Agent Hub Tray.lnk'
New-Item -ItemType Directory -Force -Path $Logs | Out-Null
New-Item -ItemType Directory -Force -Path $Notifications | Out-Null

$Stdout = Join-Path $Logs 'CODEX_agent_hub_tray_stdout.log'
$Stderr = Join-Path $Logs 'CODEX_agent_hub_tray_stderr.log'
$NotificationLog = Join-Path $Notifications 'CODEX_notification_log.jsonl'
Remove-Item -LiteralPath $Stdout -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $Stderr -Force -ErrorAction SilentlyContinue

$script:Url = "http://127.0.0.1:$Port"
$script:Process = $null
$script:StartedServer = $false
$script:RestartAttempts = 0
$script:LastAlertKey = ''
$script:LastStaleUnread = -1
$script:LastAlertAt = [datetime]::MinValue
$script:AlertsEnabled = $false
$script:SnoozeUntil = [datetime]::MaxValue
$script:NotificationLogPopupsEnabled = $false
$script:NotificationPosition = 0

function Limit-Text {
    param([string]$Text, [int]$Max = 60)
    if ([string]::IsNullOrWhiteSpace($Text)) { return 'PANDA Agent Hub' }
    if ($Text.Length -le $Max) { return $Text }
    return $Text.Substring(0, [Math]::Max(0, $Max - 3)) + '...'
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
    $status = Invoke-PahJson '/api/tray-status'
    return $null -ne $status -and $status.ok
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
        '--no-browser'
    )
    $script:Process = Start-Process -FilePath python -ArgumentList $arguments -WindowStyle Hidden -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr -PassThru
    $script:StartedServer = $true
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
    $NotifyIcon.BalloonTipTitle = (Limit-Text $Title 63)
    $NotifyIcon.BalloonTipText = (Limit-Text $Message 255)
    $NotifyIcon.ShowBalloonTip($Ms)
}

function Alert-CooldownElapsed {
    return ((Get-Date) - $script:LastAlertAt).TotalMinutes -ge $AlertCooldownMinutes
}

function Alerts-AreActive {
    return $script:AlertsEnabled -and (Get-Date) -ge $script:SnoozeUntil
}

function Update-AlertMenuText {
    if (-not $script:AlertsEnabled) {
        $AlertsToggleItem.Text = 'Overdue popups: Off'
        $SnoozeItem.Text = 'Snooze overdue popups'
        return
    }
    if ((Get-Date) -lt $script:SnoozeUntil) {
        $remaining = [Math]::Max(1, [int][Math]::Ceiling(($script:SnoozeUntil - (Get-Date)).TotalMinutes))
        $AlertsToggleItem.Text = "Overdue popups: Snoozed ${remaining}m"
        $SnoozeItem.Text = 'Snooze overdue popups'
        return
    }
    $AlertsToggleItem.Text = "Overdue popups: On, ${AlertCooldownMinutes}m cooldown"
    $SnoozeItem.Text = 'Snooze overdue popups for 2 hours'
}

function Update-NotificationMenuText {
    if ($script:NotificationLogPopupsEnabled) {
        $NotificationToggleItem.Text = 'Notification-log popups: On'
        return
    }
    $NotificationToggleItem.Text = 'Notification-log popups: Off'
}

function Set-TrayMenuStatus {
    param($Status)
    if ($null -eq $Status) {
        $StatusItem.Text = 'Status: offline'
        $UnreadItem.Text = 'Unread: unknown'
        $DecisionItem.Text = 'Decisions: unknown'
        $DiagnosticItem.Text = 'Diagnostics: unknown'
        $NotifyIcon.Text = 'PAH offline'
        return
    }
    $counts = $Status.counts
    $StatusItem.Text = "Status: $($Status.title)"
    $UnreadItem.Text = "Unread: $($counts.unread), overdue: $($counts.stale_unread)"
    $DecisionItem.Text = "Decisions: $($counts.decisions_needed)"
    $DiagnosticItem.Text = "Diagnostics: $($counts.diagnostic_problems)"
    $NotifyIcon.Text = Limit-Text $Status.tooltip 63
}

function Update-TrayStatus {
    $status = Invoke-PahJson '/api/tray-status'
    Set-TrayMenuStatus $status
    if ($null -eq $status) {
        if ($script:StartedServer -and $script:Process -and $script:Process.HasExited -and $script:RestartAttempts -lt 3) {
            $script:RestartAttempts += 1
            Show-PahBalloon 'PANDA Agent Hub restarted' 'The local PAH server stopped, so the tray is starting it again.' 6000
            Start-PahServer
        }
        return
    }

    $stale = [int]$status.counts.stale_unread
    $alertKey = "$($status.level)|$stale"
    if (
        $stale -gt 0 -and
        (Alerts-AreActive) -and
        (Alert-CooldownElapsed) -and
        ($script:LastAlertKey -ne $alertKey -or $stale -gt $script:LastStaleUnread)
    ) {
        Show-PahBalloon $status.title $status.body 10000
        $script:LastAlertAt = Get-Date
    }
    $script:LastAlertKey = $alertKey
    $script:LastStaleUnread = $stale
    Update-AlertMenuText
}

function Install-StartupShortcut {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($StartupShortcut)
    $shortcut.TargetPath = 'powershell.exe'
    $shortcut.Arguments = "-NoProfile -STA -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Port $Port -PollSeconds $PollSeconds -AlertCooldownMinutes $AlertCooldownMinutes"
    $shortcut.WorkingDirectory = $ScriptRoot
    $shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,44"
    $shortcut.Save()
}

function Remove-StartupShortcut {
    Remove-Item -LiteralPath $StartupShortcut -Force -ErrorAction SilentlyContinue
}

if (-not (Test-PahServer)) {
    Start-PahServer
}

$NotifyIcon = New-Object System.Windows.Forms.NotifyIcon
$NotifyIcon.Icon = [System.Drawing.SystemIcons]::Application
$NotifyIcon.Text = 'PANDA Agent Hub'
$NotifyIcon.Visible = $true

$Menu = New-Object System.Windows.Forms.ContextMenuStrip
$OpenItem = $Menu.Items.Add('Open Dashboard')
$OpenItem.Add_Click({ Start-Process $script:Url })

$RefreshItem = $Menu.Items.Add('Refresh Status')
$RefreshItem.Add_Click({ Update-TrayStatus })

$AlertsToggleItem = $Menu.Items.Add('Overdue popups: Off')
$AlertsToggleItem.Add_Click({
    $script:AlertsEnabled = -not $script:AlertsEnabled
    if ($script:AlertsEnabled) {
        $script:SnoozeUntil = [datetime]::MinValue
        $script:LastAlertAt = Get-Date
        Show-PahBalloon 'PANDA Agent Hub' "Overdue popups enabled with a ${AlertCooldownMinutes} minute cooldown." 5000
    }
    else {
        $script:SnoozeUntil = [datetime]::MaxValue
    }
    Update-AlertMenuText
})

$SnoozeItem = $Menu.Items.Add('Snooze overdue popups')
$SnoozeItem.Add_Click({
    $script:AlertsEnabled = $true
    $script:SnoozeUntil = (Get-Date).AddHours(2)
    Update-AlertMenuText
    Show-PahBalloon 'PANDA Agent Hub' 'Overdue popups snoozed for 2 hours.' 4000
})

$NotificationToggleItem = $Menu.Items.Add('Notification-log popups: Off')
$NotificationToggleItem.Add_Click({
    $script:NotificationLogPopupsEnabled = -not $script:NotificationLogPopupsEnabled
    Update-NotificationMenuText
    if ($script:NotificationLogPopupsEnabled) {
        Show-PahBalloon 'PANDA Agent Hub' 'Notification-log popups enabled.' 4000
    }
})

$StatusItem = $Menu.Items.Add('Status: starting')
$StatusItem.Enabled = $false
$UnreadItem = $Menu.Items.Add('Unread: checking')
$UnreadItem.Enabled = $false
$DecisionItem = $Menu.Items.Add('Decisions: checking')
$DecisionItem.Enabled = $false
$DiagnosticItem = $Menu.Items.Add('Diagnostics: checking')
$DiagnosticItem.Enabled = $false

$Menu.Items.Add('-') | Out-Null

$FolderItem = $Menu.Items.Add('Open PAH Folder')
$FolderItem.Add_Click({ Start-Process $ScriptRoot })

$LogsItem = $Menu.Items.Add('Open Logs')
$LogsItem.Add_Click({ Start-Process $Logs })

$InstallStartupItem = $Menu.Items.Add('Install at Windows Startup')
$InstallStartupItem.Add_Click({
    Install-StartupShortcut
    Show-PahBalloon 'PANDA Agent Hub' 'Tray startup shortcut installed.' 5000
})

$RemoveStartupItem = $Menu.Items.Add('Remove Windows Startup')
$RemoveStartupItem.Add_Click({
    Remove-StartupShortcut
    Show-PahBalloon 'PANDA Agent Hub' 'Tray startup shortcut removed.' 5000
})

$Menu.Items.Add('-') | Out-Null

$ExitItem = $Menu.Items.Add('Exit PANDA Agent Hub')
$ExitItem.Add_Click({
    if ($StatusTimer) { $StatusTimer.Stop() }
    if ($NotificationTimer) { $NotificationTimer.Stop() }
    $NotifyIcon.Visible = $false
    if ($script:StartedServer -and $script:Process -and -not $script:Process.HasExited) {
        $script:Process.Kill()
        $script:Process.WaitForExit()
    }
    [System.Windows.Forms.Application]::Exit()
})

$NotifyIcon.ContextMenuStrip = $Menu
$NotifyIcon.Add_DoubleClick({ Start-Process $script:Url })
$NotifyIcon.Text = 'PANDA Agent Hub'

if (Test-Path -LiteralPath $NotificationLog) {
    $script:NotificationPosition = (Get-Item -LiteralPath $NotificationLog).Length
}

$StatusTimer = New-Object System.Windows.Forms.Timer
$StatusTimer.Interval = [Math]::Max(5, $PollSeconds) * 1000
$StatusTimer.Add_Tick({ Update-TrayStatus })
$StatusTimer.Start()

$NotificationTimer = New-Object System.Windows.Forms.Timer
$NotificationTimer.Interval = 5000
$NotificationTimer.Add_Tick({
    if (-not (Test-Path -LiteralPath $NotificationLog)) {
        return
    }
    $file = Get-Item -LiteralPath $NotificationLog
    if ($file.Length -lt $script:NotificationPosition) {
        $script:NotificationPosition = 0
    }
    if ($file.Length -le $script:NotificationPosition) {
        return
    }

    $stream = [System.IO.File]::Open($NotificationLog, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    try {
        $stream.Seek($script:NotificationPosition, [System.IO.SeekOrigin]::Begin) | Out-Null
        $reader = New-Object System.IO.StreamReader($stream)
        $newText = $reader.ReadToEnd()
        $script:NotificationPosition = $stream.Position
    }
    finally {
        if ($reader) { $reader.Dispose() }
        $stream.Dispose()
    }

    if (-not $script:NotificationLogPopupsEnabled) {
        return
    }

    foreach ($line in ($newText -split "`r?`n")) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        try {
            $entry = $line | ConvertFrom-Json
            $title = 'PANDA Agent Hub'
            $message = 'Notification event recorded.'
            if ($entry.event) {
                $title = [string]$entry.event.subject
                $message = [string]$entry.event.body
            }
            elseif ($entry.manual_test) {
                $title = 'PANDA Agent Hub test'
                $message = 'Notification test completed.'
            }
            Show-PahBalloon $title $message 8000
        }
        catch {
            Show-PahBalloon 'PANDA Agent Hub' 'New notification log entry.' 5000
        }
    }
})
$NotificationTimer.Start()

Update-TrayStatus
Update-AlertMenuText
Update-NotificationMenuText
[System.Windows.Forms.Application]::Run()
