# CODEX_relay_health_check.ps1
# Relay protocol health checker.
# Default mode is read-only. With -UpdateCache, this script writes only the
# ignored local cache file under CODEX Agent Hub/CODEX state.
# It must not delete files, commit, push, install software, call the network,
# or mutate project/source state.

[CmdletBinding()]
param(
    [string]$CodexRoot = "C:\CODEX PG",
    [int]$StaleHours = 24,
    [int]$MailLookback = 16,
    [switch]$Json,
    [switch]$NoFail,
    [switch]$UpdateCache,
    [switch]$NoCache
)

$ErrorActionPreference = "Stop"

$MailboxRoot = Join-Path $CodexRoot "CODEX Claude Codex Mailbox"
$CodexInbox = Join-Path $MailboxRoot "CODEX Inbox"
$ClaudeInbox = Join-Path $MailboxRoot "CLAUDE Inbox"
$ClaudeCodeInbox = Join-Path $MailboxRoot "CODEX_CLAUDE_CODE Inbox"
$ActiveIndex = Join-Path $MailboxRoot "CODEX_ACTIVE_DISPATCH_INDEX.md"
$CurrentAuthority = Join-Path $MailboxRoot "CODEX_CURRENT_AUTHORITY.md"
$StateDir = Join-Path $CodexRoot "CODEX Agent Hub\CODEX state"
$ReadStatePath = Join-Path $StateDir "CODEX_read_state.local.json"
$RelayCachePath = Join-Path $StateDir "CODEX_relay_health_cache.local.json"

$AllowedStates = @(
    "new",
    "in_progress",
    "blocked",
    "delivered",
    "waiting_review",
    "accepted",
    "superseded",
    "paused_by_darrin"
)

$Findings = New-Object System.Collections.Generic.List[object]
$CacheEnabled = -not $NoCache
$Cache = $null
$CacheExists = Test-Path -LiteralPath $RelayCachePath
$CacheHits = 0
$CacheMisses = 0
$MailIndexForCache = [ordered]@{}

function Add-Finding {
    param(
        [Parameter(Mandatory=$true)][ValidateSet("error", "warn", "info")][string]$Severity,
        [Parameter(Mandatory=$true)][string]$Code,
        [Parameter(Mandatory=$true)][string]$Message,
        [string]$Path = "",
        [string]$Detail = ""
    )
    $Findings.Add([pscustomobject]@{
        severity = $Severity
        code = $Code
        message = $Message
        path = $Path
        detail = $Detail
    }) | Out-Null
}

function Get-FileText {
    param([Parameter(Mandatory=$true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return ""
    }
    return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8)
}

function Get-BacktickPath {
    param([string]$Text)
    if ($Text -match '`([^`]+)`') {
        return $Matches[1]
    }
    return ""
}

function Convert-ObjectToHashtable {
    param($Object)
    $table = @{}
    if (-not $Object) {
        return $table
    }
    if ($Object -is [hashtable]) {
        foreach ($key in $Object.Keys) {
            $table[$key] = $Object[$key]
        }
        return $table
    }
    foreach ($property in $Object.PSObject.Properties) {
        $table[$property.Name] = $property.Value
    }
    return $table
}

function Get-RelayCache {
    param([string]$Path)
    if (-not $CacheEnabled -or -not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    try {
        return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json)
    } catch {
        Add-Finding -Severity "warn" -Code "relay_cache_parse_failed" -Message "Relay health cache could not be parsed; continuing with a cold scan." -Path $Path -Detail $_.Exception.Message
        return $null
    }
}

function Get-CacheMailEntry {
    param(
        $CacheData,
        [string]$Path
    )
    if (-not $CacheEnabled -or -not $CacheData -or -not $CacheData.mail_index) {
        return $null
    }
    $property = $CacheData.mail_index.PSObject.Properties[$Path]
    if ($property) {
        return $property.Value
    }
    return $null
}

function Get-IsoTimestampText {
    param($Value)
    if ($Value -is [datetime]) {
        return $Value.ToUniversalTime().ToString("o")
    }
    return [string]$Value
}

function Get-FileSignature {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{
            path = $Path
            exists = $false
            last_write_time_utc = ""
            length = 0
        }
    }
    $item = Get-Item -LiteralPath $Path
    return [pscustomobject]@{
        path = $Path
        exists = $true
        last_write_time_utc = $item.LastWriteTimeUtc.ToString("o")
        length = $item.Length
    }
}

function Get-SectionTableRows {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Heading
    )
    $rows = New-Object System.Collections.Generic.List[object]
    if (-not (Test-Path -LiteralPath $Path)) {
        return $rows
    }

    $lines = Get-Content -LiteralPath $Path -Encoding UTF8
    $inSection = $false
    $headers = @()
    $headingPattern = "^##\s+" + [regex]::Escape($Heading) + "\s*$"

    foreach ($line in $lines) {
        if ($line -match $headingPattern) {
            $inSection = $true
            continue
        }
        if ($inSection -and $line -match "^##\s+") {
            break
        }
        if (-not $inSection -or $line -notmatch "^\|") {
            continue
        }

        $cells = $line.Trim().Trim("|").Split("|") | ForEach-Object { $_.Trim() }
        if ($cells.Count -eq 0) {
            continue
        }
        if ($cells[0] -match "^-+$") {
            continue
        }
        if ($headers.Count -eq 0) {
            $headers = $cells
            continue
        }

        $row = [ordered]@{}
        for ($i = 0; $i -lt $headers.Count; $i++) {
            $key = $headers[$i]
            $value = if ($i -lt $cells.Count) { $cells[$i] } else { "" }
            $row[$key] = $value
        }
        $rows.Add([pscustomobject]$row) | Out-Null
    }
    return $rows
}

function Get-FrontMatter {
    param([Parameter(Mandatory=$true)][string]$Path)
    $data = @{}
    if (-not (Test-Path -LiteralPath $Path)) {
        return $data
    }
    $lines = Get-Content -LiteralPath $Path -Encoding UTF8 -TotalCount 120
    if ($lines.Count -eq 0 -or $lines[0].Trim() -ne "---") {
        return $data
    }
    for ($i = 1; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line.Trim() -eq "---") {
            break
        }
        if ($line -match "^([A-Za-z0-9_]+):\s*(.*)$") {
            $key = $Matches[1].Trim().ToLowerInvariant()
            $value = $Matches[2].Trim()
            $value = $value.Trim("'").Trim('"')
            $data[$key] = $value
        }
    }
    return $data
}

function Get-ReadStateRecords {
    param([string]$Path)
    $records = @{}
    if (-not (Test-Path -LiteralPath $Path)) {
        return $records
    }
    try {
        $state = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($state.items) {
            foreach ($property in $state.items.PSObject.Properties) {
                $records[$property.Name] = $property.Value
            }
        }
    } catch {
        Add-Finding -Severity "warn" -Code "read_state_parse_failed" -Message "Read-state JSON could not be parsed." -Path $Path -Detail $_.Exception.Message
    }
    return $records
}

function Test-MessageIsRead {
    param(
        [Parameter(Mandatory=$true)][System.IO.FileInfo]$File,
        [hashtable]$ReadRecords,
        [hashtable]$Meta
    )
    $record = $ReadRecords[$File.FullName]
    if (-not $record -and $Meta.ContainsKey("id")) {
        foreach ($candidate in $ReadRecords.Values) {
            if ($candidate.message_id -and [string]$candidate.message_id -eq [string]$Meta["id"]) {
                $record = $candidate
                break
            }
        }
    }
    return ($record -and [string]$record.state -eq "read")
}

function Test-DarrinGate {
    param([hashtable]$Meta)
    $requires = ([string]($Meta["requires_darrin_decision"])).ToLowerInvariant()
    $threadStatus = ([string]($Meta["thread_status"])).ToLowerInvariant()
    $boundary = ([string]($Meta["approval_boundary"])).ToLowerInvariant()
    return (
        $requires -eq "true" -or
        $threadStatus -eq "waiting_on_darrin" -or
        $boundary -match "darrin"
    )
}

function Get-MailRows {
    param(
        [Parameter(Mandatory=$true)][string]$Folder,
        [Parameter(Mandatory=$true)][string]$Label,
        [int]$Count = 16,
        [hashtable]$ReadRecords = @{},
        $CacheData = $null
    )
    if (-not (Test-Path -LiteralPath $Folder)) {
        Add-Finding -Severity "error" -Code "missing_mailbox_folder" -Message "$Label mailbox folder is missing." -Path $Folder
        return @()
    }
    $rows = New-Object System.Collections.Generic.List[object]
    Get-ChildItem -LiteralPath $Folder -Filter "*.md" -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First $Count |
        ForEach-Object {
            $stamp = $_.LastWriteTimeUtc.ToString("o")
            $cacheEntry = Get-CacheMailEntry -CacheData $CacheData -Path $_.FullName
            $cacheFresh = $false
            if ($cacheEntry) {
                $cacheFresh = (
                    (Get-IsoTimestampText -Value $cacheEntry.last_write_time_utc) -eq $stamp -and
                    [int64]$cacheEntry.length -eq [int64]$_.Length
                )
            }
            if ($cacheFresh) {
                $script:CacheHits += 1
                $meta = Convert-ObjectToHashtable -Object $cacheEntry.frontmatter
            } else {
                $script:CacheMisses += 1
                $meta = Get-FrontMatter -Path $_.FullName
            }
            $script:MailIndexForCache[$_.FullName] = [ordered]@{
                folder = $Label
                path = $_.FullName
                name = $_.Name
                last_write_time_utc = $stamp
                length = $_.Length
                frontmatter = $meta
            }
            $rows.Add([pscustomobject]@{
                folder = $Label
                path = $_.FullName
                name = $_.Name
                last_write_time = $_.LastWriteTime
                id = [string]$meta["id"]
                thread_id = [string]$meta["thread_id"]
                from = [string]$meta["from"]
                to = [string]$meta["to"]
                status = [string]$meta["status"]
                thread_status = [string]$meta["thread_status"]
                requires_darrin_decision = [string]$meta["requires_darrin_decision"]
                approval_boundary = [string]$meta["approval_boundary"]
                is_read = (Test-MessageIsRead -File $_ -ReadRecords $ReadRecords -Meta $meta)
                darrin_gate = (Test-DarrinGate -Meta $meta)
            }) | Out-Null
        }
    return $rows
}

$generatedAt = Get-Date
$Cache = Get-RelayCache -Path $RelayCachePath
$activeText = Get-FileText -Path $ActiveIndex
$authorityText = Get-FileText -Path $CurrentAuthority

if (-not (Test-Path -LiteralPath $ActiveIndex)) {
    Add-Finding -Severity "error" -Code "missing_active_index" -Message "Active dispatch index is missing." -Path $ActiveIndex
}
if (-not (Test-Path -LiteralPath $CurrentAuthority)) {
    Add-Finding -Severity "error" -Code "missing_current_authority" -Message "Current authority snapshot is missing." -Path $CurrentAuthority
}
if ($authorityText -and $authorityText -notmatch "Dispatch Delta Convention") {
    Add-Finding -Severity "warn" -Code "missing_delta_convention" -Message "Current authority does not mention the dispatch delta convention." -Path $CurrentAuthority
}
if ($authorityText -and $authorityText -notmatch "Safe Read Permission Pattern") {
    Add-Finding -Severity "warn" -Code "missing_safe_read_pattern" -Message "Current authority does not mention the safe read permission pattern." -Path $CurrentAuthority
}

$activeRows = Get-SectionTableRows -Path $ActiveIndex -Heading "Active Queue"
$threadCounts = @{}
$activeDetails = New-Object System.Collections.Generic.List[object]

foreach ($row in $activeRows) {
    $thread = [string]$row.Thread
    $state = ([string]$row.State).Trim()
    $owner = [string]$row.Owner
    $sourcePath = Get-BacktickPath -Text ([string]$row."Source Mail")
    $completionPath = Get-BacktickPath -Text ([string]$row."Completion / Ack")
    if ([string]::IsNullOrWhiteSpace($thread)) {
        Add-Finding -Severity "error" -Code "blank_active_thread" -Message "Active queue contains a blank thread row." -Path $ActiveIndex
        continue
    }

    $threadCounts[$thread] = 1 + [int]($threadCounts[$thread])

    if ($AllowedStates -notcontains $state) {
        Add-Finding -Severity "error" -Code "invalid_active_state" -Message "Active queue row has unsupported state '$state'." -Path $ActiveIndex -Detail $thread
    }
    if ([string]::IsNullOrWhiteSpace($owner)) {
        Add-Finding -Severity "warn" -Code "missing_owner" -Message "Active queue row is missing owner." -Path $ActiveIndex -Detail $thread
    }
    if ([string]::IsNullOrWhiteSpace($sourcePath)) {
        Add-Finding -Severity "error" -Code "missing_source_reference" -Message "Active queue row has no source mail path." -Path $ActiveIndex -Detail $thread
    } elseif (-not (Test-Path -LiteralPath $sourcePath)) {
        Add-Finding -Severity "error" -Code "source_missing_on_disk" -Message "Source mail path does not exist." -Path $sourcePath -Detail $thread
    }
    if ($state -in @("delivered", "waiting_review", "accepted") -and [string]::IsNullOrWhiteSpace($completionPath)) {
        Add-Finding -Severity "warn" -Code "missing_completion_reference" -Message "Delivered/review row has no completion or ack path." -Path $ActiveIndex -Detail $thread
    } elseif (-not [string]::IsNullOrWhiteSpace($completionPath) -and -not (Test-Path -LiteralPath $completionPath)) {
        Add-Finding -Severity "error" -Code "completion_missing_on_disk" -Message "Completion/ack path does not exist." -Path $completionPath -Detail $thread
    }

    $ageHours = $null
    if ($sourcePath -and (Test-Path -LiteralPath $sourcePath)) {
        $ageHours = [math]::Round(((Get-Date) - (Get-Item -LiteralPath $sourcePath).LastWriteTime).TotalHours, 1)
        if ($state -in @("new", "in_progress", "blocked") -and $ageHours -ge $StaleHours) {
            Add-Finding -Severity "warn" -Code "stale_active_dispatch" -Message "Active dispatch is older than $StaleHours hours." -Path $sourcePath -Detail "$thread ($state, ${ageHours}h)"
        }
    }

    $activeDetails.Add([pscustomobject]@{
        thread = $thread
        state = $state
        owner = $owner
        source_mail = $sourcePath
        completion_or_ack = $completionPath
        source_age_hours = $ageHours
    }) | Out-Null
}

foreach ($thread in $threadCounts.Keys) {
    if ([int]$threadCounts[$thread] -gt 1) {
        Add-Finding -Severity "error" -Code "duplicate_active_thread" -Message "Active queue has duplicate rows for one thread." -Path $ActiveIndex -Detail $thread
    }
}

$readRecords = Get-ReadStateRecords -Path $ReadStatePath
$mailRows = @()
$mailRows += Get-MailRows -Folder $CodexInbox -Label "CODEX Inbox" -Count $MailLookback -ReadRecords $readRecords -CacheData $Cache
$mailRows += Get-MailRows -Folder $ClaudeInbox -Label "CLAUDE Inbox" -Count $MailLookback -ReadRecords $readRecords -CacheData $Cache
$mailRows += Get-MailRows -Folder $ClaudeCodeInbox -Label "CODEX_CLAUDE_CODE Inbox" -Count $MailLookback -ReadRecords $readRecords -CacheData $Cache

$indexWriteTime = if (Test-Path -LiteralPath $ActiveIndex) { (Get-Item -LiteralPath $ActiveIndex).LastWriteTime } else { [datetime]::MinValue }
$combinedRelayText = "$activeText`n$authorityText"
$unindexedRecent = $mailRows |
    Where-Object {
        $_.folder -eq "CODEX Inbox" -and
        $_.last_write_time -gt $indexWriteTime -and
        $combinedRelayText -notmatch [regex]::Escape($_.path) -and
        $combinedRelayText -notmatch [regex]::Escape($_.name)
    } |
    Select-Object -First $MailLookback

foreach ($item in $unindexedRecent) {
    Add-Finding -Severity "warn" -Code "unindexed_recent_codex_mail" -Message "Newer CODEX Inbox mail is not reflected in active index or authority snapshot." -Path $item.path -Detail $item.thread_id
}

$unreadIncoming = $mailRows |
    Where-Object { $_.folder -in @("CODEX Inbox", "CODEX_CLAUDE_CODE Inbox") -and -not $_.is_read } |
    Select-Object -First $MailLookback

if ($unreadIncoming.Count -gt 0) {
    Add-Finding -Severity "info" -Code "unread_recent_mail" -Message "$($unreadIncoming.Count) recent incoming mailbox item(s) are unread or absent from PAH read state." -Detail "Lookback: $MailLookback"
}

$darrinGates = $mailRows |
    Where-Object { $_.darrin_gate } |
    Select-Object -First $MailLookback

foreach ($item in $darrinGates) {
    Add-Finding -Severity "info" -Code "darrin_gate_mail" -Message "Recent mailbox item has a Darrin decision/approval gate." -Path $item.path -Detail $item.thread_id
}

$findingsArray = @($Findings.ToArray())
$activeRowsArray = @($activeRows)
$activeDetailsArray = @($activeDetails.ToArray())
$mailRowsArray = @($mailRows)
$unreadIncomingArray = @($unreadIncoming)
$darrinGatesArray = @($darrinGates)
$unindexedRecentArray = @($unindexedRecent)
$latestCursors = [ordered]@{}
foreach ($label in @("CODEX Inbox", "CLAUDE Inbox", "CODEX_CLAUDE_CODE Inbox")) {
    $latest = $mailRowsArray |
        Where-Object { $_.folder -eq $label } |
        Sort-Object last_write_time -Descending |
        Select-Object -First 1
    if ($latest) {
        $latestCursors[$label] = [ordered]@{
            name = $latest.name
            path = $latest.path
            thread_id = $latest.thread_id
            last_write_time = $latest.last_write_time.ToString("yyyy-MM-dd HH:mm:ss zzz")
            last_write_time_utc = $latest.last_write_time.ToUniversalTime().ToString("o")
        }
    } else {
        $latestCursors[$label] = [ordered]@{
            name = ""
            path = ""
            thread_id = ""
            last_write_time = ""
            last_write_time_utc = ""
        }
    }
}

$errorCount = @($findingsArray | Where-Object { $_.severity -eq "error" }).Count
$warnCount = @($findingsArray | Where-Object { $_.severity -eq "warn" }).Count
$infoCount = @($findingsArray | Where-Object { $_.severity -eq "info" }).Count
$overall = if ($errorCount) { "error" } elseif ($warnCount) { "warn" } else { "ok" }

$result = [pscustomobject]@{
    generated_at = $generatedAt.ToString("yyyy-MM-dd HH:mm:ss zzz")
    mode = if ($UpdateCache) { "cache-update" } else { "read-only" }
    status = $overall
    counts = [pscustomobject]@{
        active_rows = $activeRowsArray.Count
        errors = $errorCount
        warnings = $warnCount
        info = $infoCount
        recent_mail_scanned = $mailRowsArray.Count
        recent_unread_incoming = $unreadIncomingArray.Count
        recent_darrin_gates = $darrinGatesArray.Count
        unindexed_recent_codex_mail = $unindexedRecentArray.Count
    }
    files = [pscustomobject]@{
        active_index = $ActiveIndex
        current_authority = $CurrentAuthority
        read_state = $ReadStatePath
        relay_health_cache = $RelayCachePath
    }
    cache = [pscustomobject]@{
        enabled = $CacheEnabled
        exists = $CacheExists
        updated = $false
        path = $RelayCachePath
        hits = $CacheHits
        misses = $CacheMisses
        latest_cursors = $latestCursors
    }
    active_queue = $activeDetailsArray
    unread_incoming = @($unreadIncomingArray | Select-Object folder, name, thread_id, status, thread_status, path)
    darrin_gates = @($darrinGatesArray | Select-Object folder, name, thread_id, requires_darrin_decision, approval_boundary, path)
    findings = $findingsArray
}

if ($UpdateCache) {
    try {
        if (-not (Test-Path -LiteralPath $StateDir)) {
            New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
        }
        $cachePayload = [pscustomobject]@{
            version = 1
            updated_at = $generatedAt.ToString("yyyy-MM-dd HH:mm:ss zzz")
            updated_at_utc = $generatedAt.ToUniversalTime().ToString("o")
            parameters = [pscustomobject]@{
                stale_hours = $StaleHours
                mail_lookback = $MailLookback
            }
            source_files = [pscustomobject]@{
                active_index = Get-FileSignature -Path $ActiveIndex
                current_authority = Get-FileSignature -Path $CurrentAuthority
                read_state = Get-FileSignature -Path $ReadStatePath
            }
            latest_cursors = $latestCursors
            mail_index = $MailIndexForCache
            last_result_counts = $result.counts
            last_result_status = $result.status
        }
        $cachePayload | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $RelayCachePath -Encoding UTF8
        $result.cache.updated = $true
        $result.cache.exists = $true
    } catch {
        Add-Finding -Severity "warn" -Code "relay_cache_write_failed" -Message "Relay health cache could not be written." -Path $RelayCachePath -Detail $_.Exception.Message
        $findingsArray = @($Findings.ToArray())
        $result.findings = $findingsArray
        $warnCount = @($findingsArray | Where-Object { $_.severity -eq "warn" }).Count
        $result.counts.warnings = $warnCount
        $result.counts.info = @($findingsArray | Where-Object { $_.severity -eq "info" }).Count
        if ($result.status -eq "ok") {
            $result.status = "warn"
        }
    }
}

if ($Json) {
    $result | ConvertTo-Json -Depth 8
} else {
    Write-Output "CODEX relay health check"
    Write-Output "Generated: $($result.generated_at)"
    Write-Output "Mode: $($result.mode)"
    Write-Output "Status: $($result.status.ToUpperInvariant())"
    Write-Output ""
    Write-Output "Summary:"
    Write-Output "- Active rows: $($result.counts.active_rows)"
    Write-Output "- Findings: $errorCount error(s), $warnCount warning(s), $infoCount info"
    Write-Output "- Recent mail scanned: $($result.counts.recent_mail_scanned)"
    Write-Output "- Recent unread incoming: $($result.counts.recent_unread_incoming)"
    Write-Output "- Recent Darrin gates: $($result.counts.recent_darrin_gates)"
    Write-Output "- Unindexed recent CODEX mail: $($result.counts.unindexed_recent_codex_mail)"
    Write-Output "- Cache: $($result.cache.hits) hit(s), $($result.cache.misses) miss(es), updated=$($result.cache.updated)"

    Write-Output ""
    Write-Output "Active Queue:"
    if ($activeDetailsArray.Count) {
        $activeDetailsArray | Select-Object thread, state, owner, source_age_hours | Format-Table -AutoSize | Out-String -Width 240
    } else {
        Write-Output "(none)"
    }

    Write-Output "Findings:"
    if ($findingsArray.Count) {
        foreach ($finding in $findingsArray) {
            $suffix = ""
            if ($finding.path) { $suffix += " path=$($finding.path)" }
            if ($finding.detail) { $suffix += " detail=$($finding.detail)" }
            Write-Output "[$($finding.severity.ToUpperInvariant())] $($finding.code): $($finding.message)$suffix"
        }
    } else {
        Write-Output "(none)"
    }
}

if ($errorCount -gt 0 -and -not $NoFail) {
    exit 1
}
