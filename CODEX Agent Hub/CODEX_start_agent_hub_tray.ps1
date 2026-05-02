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
$script:LastUrgentCodex = -1
$script:LastAlertAt = [datetime]::MinValue
$script:AlertsEnabled = $false
$script:SnoozeUntil = [datetime]::MaxValue
$script:NotificationLogPopupsEnabled = $false
$script:NotificationPosition = 0
$script:TrayPopupsDisabled = $true

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
        '--no-port-fallback',
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
