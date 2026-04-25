<#
.SYNOPSIS
Automates the Codex PG handoff/checkpoint process.

.DESCRIPTION
This project-local shortcut updates a generated handoff snapshot, writes a
fresh-chat resume prompt, and optionally runs the GitHub backup script.
It only writes under C:\CODEX PG.
#>
[CmdletBinding()]
param(
    [ValidateSet("Handoff", "Checkpoint", "Backup", "ResumePrompt")]
    [string]$Mode = "Handoff",
    [string]$RepoRoot = "C:\CODEX PG"
)

$ErrorActionPreference = "Stop"

function Assert-CodexRoot {
    param([string]$Path)
    $resolved = (Resolve-Path -LiteralPath $Path).Path.TrimEnd('\')
    if ($resolved.ToLowerInvariant() -ne "c:\codex pg") {
        throw "Refusing unexpected repo root: $resolved"
    }
    return $resolved
}

function Invoke-GitText {
    param([string[]]$GitArgs, [string]$Fallback = "")
    $previous = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & git @GitArgs 2>&1
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previous
    }
    if ($code -ne 0) { return $Fallback }
    return (($output | ForEach-Object { "$_.".TrimEnd('.') }) -join "`n").Trim()
}

function Set-MarkedSection {
    param(
        [string]$Path,
        [string]$MarkerName,
        [string[]]$Lines
    )
    $start = "<!-- ${MarkerName}_START -->"
    $end = "<!-- ${MarkerName}_END -->"
    $block = @($start) + $Lines + @($end)
    $newText = ($block -join "`r`n") + "`r`n"
    if (Test-Path -LiteralPath $Path) {
        $oldText = Get-Content -LiteralPath $Path -Raw
        $pattern = [regex]::Escape($start) + ".*?" + [regex]::Escape($end) + "\s*"
        if ([regex]::IsMatch($oldText, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)) {
            $updated = [regex]::Replace($oldText, $pattern, $newText, [System.Text.RegularExpressions.RegexOptions]::Singleline)
        } else {
            $updated = $oldText.TrimEnd() + "`r`n`r`n" + $newText
        }
    } else {
        $updated = $newText
    }
    Set-Content -LiteralPath $Path -Value $updated -Encoding UTF8
}

$root = Assert-CodexRoot $RepoRoot
$docs = Join-Path $root "CODEX Docs"
$logs = Join-Path $root "CODEX Backup Logs"
$automation = Join-Path $root "CODEX Automation"
New-Item -ItemType Directory -Path $docs,$logs -Force | Out-Null

$now = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
$memoryPath = Join-Path $docs "CODEX_PROJECT_MEMORY.md"
$handoffPath = Join-Path $docs "CODEX_CURRENT_HANDOFF.md"
$resumePath = Join-Path $docs "CODEX_RESUME_PROMPT.txt"
$lastHandoffPath = Join-Path $docs "CODEX_LAST_AUTOMATED_HANDOFF.md"
$backupScript = Join-Path $automation "CODEX_backup_to_github.ps1"

Set-Location -LiteralPath $root

$branch = Invoke-GitText @("branch", "--show-current") "unknown"
$status = Invoke-GitText @("status", "--short", "--branch") "git status unavailable"
$remote = Invoke-GitText @("remote", "get-url", "origin") "no origin remote configured"
$latest = Invoke-GitText @("log", "--oneline", "-5") "no commits yet"
$fileCount = (Get-ChildItem -LiteralPath $root -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch "\\.git\\" }).Count

$resumeLines = @(
"CODEX RESUME PG",
"",
"Read these first:",
"C:\CODEX PG\CODEX Docs\CODEX_PROJECT_MEMORY.md",
"C:\CODEX PG\CODEX Docs\CODEX_CURRENT_HANDOFF.md",
"C:\CODEX PG\CODEX Docs\CODEX_LAST_AUTOMATED_HANDOFF.md",
"",
"Then check:",
"C:\CODEX PG git status",
"GitHub repo: https://github.com/DarrinRap/CODEX-PG.git",
"",
"Remember:",
"- All Codex files stay under C:\CODEX PG",
"- Every Codex folder starts with CODEX",
"- C:\panda-gallery is read-only reference only",
"- Continue from the latest handoff",
"",
"Latest automated handoff generated: $now"
)
$resumeLines | Set-Content -LiteralPath $resumePath -Encoding UTF8

$snapshotLines = @(
"# CODEX Last Automated Handoff",
"",
"Generated: $now",
"Mode: $Mode",
"",
"## Current Git State",
"",
'- Local repo: `C:\CODEX PG`',
'- GitHub repo: `https://github.com/DarrinRap/CODEX-PG.git`',
('- Branch: `{0}`' -f $branch),
('- Origin: `{0}`' -f $remote),
"- Indexed project file count, excluding .git: $fileCount",
"",
"## Git Status",
"",
'```text'
$status,
'```'
"",
"## Recent Commits",
"",
'```text'
$latest,
'```'
"",
"## Fresh Chat Resume Prompt",
"",
'```text'
) + $resumeLines + @(
'```'
"",
"## Trigger Words",
"",
"- `CODEX HANDOFF`: run full handoff plus GitHub backup.",
"- `CODEX CHECKPOINT`: save a progress checkpoint plus GitHub backup.",
"- `CODEX BACKUP`: run GitHub backup only.",
"- `CODEX RESUME PG`: start a new chat from memory and handoff files."
)
$snapshotLines | Set-Content -LiteralPath $lastHandoffPath -Encoding UTF8

$sectionLines = @(
"## Automated Handoff Snapshot",
"",
"Generated: $now",
('Mode: `{0}`' -f $Mode),
"",
'- Last automated handoff: `C:\CODEX PG\CODEX Docs\CODEX_LAST_AUTOMATED_HANDOFF.md`',
'- Fresh chat resume prompt: `C:\CODEX PG\CODEX Docs\CODEX_RESUME_PROMPT.txt`',
'- GitHub repo: `https://github.com/DarrinRap/CODEX-PG.git`',
('- Current branch: `{0}`' -f $branch),
('- Origin: `{0}`' -f $remote),
"",
'Use trigger word `CODEX RESUME PG` in a fresh chat and paste the contents of `CODEX_RESUME_PROMPT.txt` if needed.'
)
Set-MarkedSection -Path $handoffPath -MarkerName "CODEX_AUTOMATED_HANDOFF" -Lines $sectionLines

$memoryLines = @(
"## Handoff Automation",
"",
"Last generated: $now",
"",
'Project-local shortcut folder: `C:\CODEX PG\CODEX Handoff Automation`.',
"",
"Trigger words:",
"",
"- `CODEX HANDOFF`: update handoff snapshot, generate resume prompt, run GitHub backup.",
"- `CODEX CHECKPOINT`: same as handoff, used mid-project.",
"- `CODEX BACKUP`: run GitHub backup only.",
"- `CODEX RESUME PG`: fresh-chat startup instruction."
)
Set-MarkedSection -Path $memoryPath -MarkerName "CODEX_HANDOFF_AUTOMATION" -Lines $memoryLines

if ($Mode -in @("Handoff", "Checkpoint", "Backup")) {
    if (-not (Test-Path -LiteralPath $backupScript)) {
        throw "Backup script not found: $backupScript"
    }
    & $backupScript
}

Write-Host "CODEX handoff automation complete."
Write-Host "Mode: $Mode"
Write-Host "Resume prompt: $resumePath"
Write-Host "Last handoff: $lastHandoffPath"


