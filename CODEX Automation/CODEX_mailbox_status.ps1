# CODEX_mailbox_status.ps1
# Read-only helper for fast Claude/CC/Codex mailbox orientation.
# This script must not write files, delete files, commit, push, install software,
# call the network, or mutate repo state.

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$CodexRoot = "C:\CODEX PG"
$PandaRoot = "C:\panda-gallery"
$MailboxRoot = Join-Path $CodexRoot "CODEX Claude Codex Mailbox"
$CodexInbox = Join-Path $MailboxRoot "CODEX Inbox"
$ClaudeInbox = Join-Path $MailboxRoot "CLAUDE Inbox"
$ActiveIndex = Join-Path $MailboxRoot "CODEX_ACTIVE_DISPATCH_INDEX.md"
$CurrentAuthority = Join-Path $MailboxRoot "CODEX_CURRENT_AUTHORITY.md"
$RelayInventory = Join-Path $CodexRoot "CODEX Relay Mockups\CODEX_RELAY_MOCKUP_DELIVERY_INVENTORY.md"

function Write-Section {
    param([Parameter(Mandatory=$true)][string]$Title)
    Write-Output ""
    Write-Output "## $Title"
}

function Show-ExistingFile {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [int]$MaxLines = 80
    )
    if (Test-Path -LiteralPath $Path) {
        Write-Output "Path: $Path"
        Get-Content -LiteralPath $Path -TotalCount $MaxLines
    } else {
        Write-Output "Missing: $Path"
    }
}

function Show-NewestMarkdown {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [int]$Count = 8
    )
    if (Test-Path -LiteralPath $Path) {
        Get-ChildItem -LiteralPath $Path -Filter "*.md" -File |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First $Count Name, LastWriteTime, Length |
            Format-Table -AutoSize | Out-String -Width 240
    } else {
        Write-Output "Missing: $Path"
    }
}

function Show-GitStatus {
    param(
        [Parameter(Mandatory=$true)][string]$Repo,
        [string]$Pathspec = ""
    )
    if (-not (Test-Path -LiteralPath $Repo)) {
        Write-Output "Missing repo path: $Repo"
        return
    }

    try {
        if ([string]::IsNullOrWhiteSpace($Pathspec)) {
            git -C $Repo status --short --branch
        } else {
            git -C $Repo status --short -- $Pathspec
        }
    } catch {
        Write-Output "git status failed for ${Repo}: $($_.Exception.Message)"
    }
}

Write-Output "CODEX mailbox/status snapshot"
Write-Output "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
Write-Output "Mode: read-only"

Write-Section "Active Dispatch Index"
Show-ExistingFile -Path $ActiveIndex -MaxLines 120

Write-Section "Current Authority Snapshot"
Show-ExistingFile -Path $CurrentAuthority -MaxLines 120

Write-Section "Relay Delivery Inventory"
Show-ExistingFile -Path $RelayInventory -MaxLines 120

Write-Section "Newest CODEX Inbox Mail"
Show-NewestMarkdown -Path $CodexInbox -Count 8

Write-Section "Newest CLAUDE Inbox Mail"
Show-NewestMarkdown -Path $ClaudeInbox -Count 8

Write-Section "CODEX PG Git Status"
Show-GitStatus -Repo $CodexRoot

Write-Section "Panda Gallery Relay Mockup Status"
Show-GitStatus -Repo $PandaRoot -Pathspec "workflows/design/pg_general_mockups"
