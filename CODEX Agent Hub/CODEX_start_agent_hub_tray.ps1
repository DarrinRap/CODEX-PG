param(
    [int]$Port = 8765
)

$ErrorActionPreference = 'Stop'

if ([Threading.Thread]::CurrentThread.ApartmentState -ne 'STA') {
    Start-Process -FilePath powershell.exe -ArgumentList @(
        '-NoProfile',
        '-STA',
        '-ExecutionPolicy',
        'Bypass',
        '-File',
        "`"$PSCommandPath`"",
        '-Port',
        "$Port"
    ) -WindowStyle Hidden
    exit
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$App = Join-Path $ScriptRoot 'CODEX_agent_hub.py'
$Logs = Join-Path $ScriptRoot 'CODEX logs'
$Notifications = Join-Path $ScriptRoot 'CODEX notifications'
New-Item -ItemType Directory -Force -Path $Logs | Out-Null
New-Item -ItemType Directory -Force -Path $Notifications | Out-Null

$Stdout = Join-Path $Logs 'CODEX_agent_hub_tray_stdout.log'
$Stderr = Join-Path $Logs 'CODEX_agent_hub_tray_stderr.log'
$NotificationLog = Join-Path $Notifications 'CODEX_notification_log.jsonl'
Remove-Item -LiteralPath $Stdout -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $Stderr -Force -ErrorAction SilentlyContinue

$Arguments = @(
    "`"$App`"",
    '--host',
    '127.0.0.1',
    '--port',
    "$Port",
    '--no-browser'
)

$Process = Start-Process -FilePath python -ArgumentList $Arguments -WindowStyle Hidden -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr -PassThru

$script:Url = "http://127.0.0.1:$Port"
for ($i = 0; $i -lt 40; $i++) {
    Start-Sleep -Milliseconds 250
    if (Test-Path -LiteralPath $Stdout) {
        $line = Get-Content -LiteralPath $Stdout -ErrorAction SilentlyContinue | Select-String -Pattern 'PANDA Agent Hub running at ' | Select-Object -Last 1
        if ($line) {
            $script:Url = ($line.Line -replace '^.*PANDA Agent Hub running at ', '').Trim()
            break
        }
    }
}

$NotifyIcon = New-Object System.Windows.Forms.NotifyIcon
$NotifyIcon.Icon = [System.Drawing.SystemIcons]::Application
$NotifyIcon.Text = 'PANDA Agent Hub'
$NotifyIcon.Visible = $true

$Menu = New-Object System.Windows.Forms.ContextMenuStrip

$OpenItem = $Menu.Items.Add('Open Dashboard')
$OpenItem.Add_Click({ Start-Process $script:Url })

$FolderItem = $Menu.Items.Add('Open PAH Folder')
$FolderItem.Add_Click({ Start-Process $ScriptRoot })

$LogsItem = $Menu.Items.Add('Open Logs')
$LogsItem.Add_Click({ Start-Process $Logs })

$Menu.Items.Add('-') | Out-Null

$ExitItem = $Menu.Items.Add('Exit PANDA Agent Hub')
$ExitItem.Add_Click({
    if ($NotificationTimer) {
        $NotificationTimer.Stop()
    }
    $NotifyIcon.Visible = $false
    if ($Process -and -not $Process.HasExited) {
        $Process.Kill()
        $Process.WaitForExit()
    }
    [System.Windows.Forms.Application]::Exit()
})

$NotifyIcon.ContextMenuStrip = $Menu
$NotifyIcon.Add_DoubleClick({ Start-Process $script:Url })
$NotifyIcon.BalloonTipTitle = 'PANDA Agent Hub'
$NotifyIcon.BalloonTipText = "Running at $script:Url"
$NotifyIcon.ShowBalloonTip(5000)

$script:NotificationPosition = 0
if (Test-Path -LiteralPath $NotificationLog) {
    $script:NotificationPosition = (Get-Item -LiteralPath $NotificationLog).Length
}

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
            $NotifyIcon.BalloonTipTitle = $title
            $NotifyIcon.BalloonTipText = $message
            $NotifyIcon.ShowBalloonTip(8000)
        }
        catch {
            $NotifyIcon.BalloonTipTitle = 'PANDA Agent Hub'
            $NotifyIcon.BalloonTipText = 'New notification log entry.'
            $NotifyIcon.ShowBalloonTip(5000)
        }
    }
})
$NotificationTimer.Start()

[System.Windows.Forms.Application]::Run()
