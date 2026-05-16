# CODEX_mailbox_stable_check.ps1
# Read-only stable mailbox checker for Claude/CC/Codex lanes.
# This script must not write files, delete files, archive files, commit, push,
# call the network, or mutate repo/mailbox state.

[CmdletBinding()]
param(
    [int]$Passes = 3,
    [int]$DelayMilliseconds = 1000
)

$ErrorActionPreference = "Stop"

if ($Passes -lt 2) {
    throw "Passes must be 2 or greater so stability can be measured."
}

if ($DelayMilliseconds -lt 0) {
    throw "DelayMilliseconds must be 0 or greater."
}

$CanonicalMailboxes = @(
    [pscustomobject]@{
        Label = "CODEX Inbox"
        Role = "CD/Codex -> Codex"
        Path = "C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Inbox"
        ExpectedCleanFiles = @()
    },
    [pscustomobject]@{
        Label = "Direct CLAUDE Inbox"
        Role = "Codex -> CD"
        Path = "C:\CODEX PG\CODEX Claude Codex Mailbox\CLAUDE Inbox"
        ExpectedCleanFiles = @()
    },
    [pscustomobject]@{
        Label = "Project CC Inbox"
        Role = "CD -> CC"
        Path = "C:\panda-gallery\workflows\cc_mailbox\CC Inbox"
        ExpectedCleanFiles = @()
    },
    [pscustomobject]@{
        Label = "Project CLAUDE Inbox"
        Role = "CC -> CD"
        Path = "C:\panda-gallery\workflows\cc_mailbox\CLAUDE Inbox"
        ExpectedCleanFiles = @()
    }
)

$LegacyMailboxes = @(
    [pscustomobject]@{
        Label = "Legacy CODEX_CLAUDE_CODE Inbox"
        Role = "Legacy inactive"
        Path = "C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX_CLAUDE_CODE Inbox"
        ExpectedCleanFiles = @("README_DO_NOT_USE_FOR_NEW_DISPATCH.md")
    },
    [pscustomobject]@{
        Label = "Legacy CODEX Claude Code Inbox"
        Role = "Legacy inactive"
        Path = "C:\CODEX PG\CODEX Claude Codex Mailbox\CODEX Claude Code Inbox"
        ExpectedCleanFiles = @("README_DO_NOT_USE_FOR_NEW_DISPATCH.md")
    }
)

function Get-MailboxFileSnapshot {
    param(
        [Parameter(Mandatory=$true)][pscustomobject]$Mailbox
    )

    if (-not (Test-Path -LiteralPath $Mailbox.Path)) {
        return [pscustomobject]@{
            Label = $Mailbox.Label
            Role = $Mailbox.Role
            Path = $Mailbox.Path
            Exists = $false
            Files = @()
            Signature = "MISSING|$($Mailbox.Path)"
            UnexpectedFiles = @()
        }
    }

    $files = Get-ChildItem -Force -LiteralPath $Mailbox.Path -File |
        Sort-Object FullName |
        ForEach-Object {
            [pscustomobject]@{
                Name = $_.Name
                FullName = $_.FullName
                Length = $_.Length
                LastWriteTimeUtc = $_.LastWriteTimeUtc.ToString("o")
            }
        }

    $expected = @($Mailbox.ExpectedCleanFiles)
    $unexpected = @($files | Where-Object { $expected -notcontains $_.Name })
    $signatureParts = @($files | ForEach-Object {
        "$($_.Name)|$($_.Length)|$($_.LastWriteTimeUtc)"
    })

    return [pscustomobject]@{
        Label = $Mailbox.Label
        Role = $Mailbox.Role
        Path = $Mailbox.Path
        Exists = $true
        Files = @($files)
        Signature = ($signatureParts -join "`n")
        UnexpectedFiles = @($unexpected)
    }
}

function Get-AllMailboxSnapshot {
    param(
        [Parameter(Mandatory=$true)][int]$PassNumber
    )

    $mailboxes = @($CanonicalMailboxes + $LegacyMailboxes)
    $snapshots = @($mailboxes | ForEach-Object { Get-MailboxFileSnapshot -Mailbox $_ })
    $combinedSignature = @($snapshots | ForEach-Object {
        "$($_.Label)`n$($_.Path)`n$($_.Signature)"
    }) -join "`n---`n"

    return [pscustomobject]@{
        Pass = $PassNumber
        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff zzz")
        Mailboxes = $snapshots
        Signature = $combinedSignature
    }
}

function Write-MailboxRows {
    param(
        [Parameter(Mandatory=$true)][array]$Snapshots
    )

    foreach ($snapshot in $Snapshots) {
        Write-Output ""
        Write-Output "Pass $($snapshot.Pass) at $($snapshot.Timestamp)"
        foreach ($mailbox in $snapshot.Mailboxes) {
            $fileCount = @($mailbox.Files).Count
            $unexpectedCount = @($mailbox.UnexpectedFiles).Count
            Write-Output "  [$($mailbox.Label)] files=$fileCount unexpected=$unexpectedCount path=$($mailbox.Path)"
            foreach ($file in $mailbox.Files) {
                Write-Output "    - $($file.Name) | bytes=$($file.Length) | mtime_utc=$($file.LastWriteTimeUtc)"
            }
        }
    }
}

$snapshots = @()
for ($i = 1; $i -le $Passes; $i++) {
    $snapshots += Get-AllMailboxSnapshot -PassNumber $i
    if ($i -lt $Passes -and $DelayMilliseconds -gt 0) {
        Start-Sleep -Milliseconds $DelayMilliseconds
    }
}

$firstSignature = $snapshots[0].Signature
$stable = -not @($snapshots | Where-Object { $_.Signature -ne $firstSignature })
$dirty = $false
$missing = $false

foreach ($mailbox in $snapshots[-1].Mailboxes) {
    if (-not $mailbox.Exists) {
        $missing = $true
    }
    if (@($mailbox.UnexpectedFiles).Count -gt 0) {
        $dirty = $true
    }
}

if (-not $stable) {
    $status = "UNSTABLE_RACING"
} elseif ($missing) {
    $status = "STABLE_ERROR"
} elseif ($dirty) {
    $status = "STABLE_DIRTY"
} else {
    $status = "STABLE_CLEAN"
}

Write-Output "CODEX stable mailbox check"
Write-Output "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
Write-Output "Mode: read-only"
Write-Output "Passes: $Passes"
Write-Output "DelayMilliseconds: $DelayMilliseconds"
Write-Output "Status: $status"

if (-not $stable) {
    Write-Output ""
    Write-Output "Racing evidence: at least one pass returned a different file list, size, or mtime."
}

Write-MailboxRows -Snapshots $snapshots

if ($status -eq "STABLE_CLEAN") {
    exit 0
}

if ($status -eq "STABLE_DIRTY") {
    exit 1
}

if ($status -eq "UNSTABLE_RACING") {
    exit 2
}

exit 3
