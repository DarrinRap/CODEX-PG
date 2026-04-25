<#
.SYNOPSIS
Creates a timestamped git backup for the Codex PG workspace and pushes to GitHub when an origin remote is configured.

.DESCRIPTION
This script is intentionally conservative. It only operates on C:\CODEX PG by default, initializes git if needed, stages all changes, commits when there are changes, and pushes to origin when a remote exists. If no GitHub remote exists yet, it leaves a clear log message and exits successfully after the local commit.
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = "C:\CODEX PG",
    [string]$RemoteUrl = "",
    [string]$Branch = "main",
    [switch]$SkipPush
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message)
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$stamp] $Message"
    Write-Host $line
    Add-Content -Path $script:LogPath -Value $line -Encoding UTF8
}

function Invoke-LoggedGit {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    Write-Log "git $($GitArgs -join ' ')"
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & git @GitArgs 2>&1
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    foreach ($line in $output) {
        if ($null -ne $line -and "$line".Length -gt 0) {
            Write-Log "  $line"
        }
    }
    if ($code -ne 0) {
        throw "git $($GitArgs -join ' ') failed with exit code $code"
    }
}

$resolvedRoot = (Resolve-Path -LiteralPath $RepoRoot).Path.TrimEnd('\')
$expectedRoot = "C:\CODEX PG"
if ($resolvedRoot.ToLowerInvariant() -ne $expectedRoot.ToLowerInvariant()) {
    throw "Refusing to back up unexpected path '$resolvedRoot'. Expected '$expectedRoot'."
}

$logDir = Join-Path $resolvedRoot "CODEX Backup Logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$script:LogPath = Join-Path $logDir ("CODEX_backup_{0}.log" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

Write-Log "Starting CODEX PG backup."
Write-Log "Repo root: $resolvedRoot"
Set-Location -LiteralPath $resolvedRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is not available on PATH. Install Git for Windows before running backup."
}

if (-not (Test-Path -LiteralPath (Join-Path $resolvedRoot ".git"))) {
    Write-Log "No git repository found. Initializing repository."
    $initOutput = & git init -b $Branch 2>&1
    $initCode = $LASTEXITCODE
    foreach ($line in $initOutput) { if ($line) { Write-Log "  $line" } }
    if ($initCode -ne 0) {
        Write-Log "git init -b failed; falling back to git init then checkout -B."
        Invoke-LoggedGit init
        Invoke-LoggedGit checkout -B $Branch
    }
}

$currentName = (& git config user.name) 2>$null
if ([string]::IsNullOrWhiteSpace($currentName)) {
    Invoke-LoggedGit config user.name "Codex Backup"
}

$currentEmail = (& git config user.email) 2>$null
if ([string]::IsNullOrWhiteSpace($currentEmail)) {
    Invoke-LoggedGit config user.email "codex-backup@local"
}

$currentBranch = (& git branch --show-current) 2>$null
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    Invoke-LoggedGit checkout -B $Branch
} elseif ($currentBranch -ne $Branch) {
    Write-Log "Current branch is '$currentBranch'. Leaving branch unchanged."
    $Branch = $currentBranch
}

if (-not [string]::IsNullOrWhiteSpace($RemoteUrl)) {
    $existingRemote = (& git remote get-url origin) 2>$null
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($existingRemote)) {
        Write-Log "Updating origin remote to supplied URL."
        Invoke-LoggedGit remote set-url origin $RemoteUrl
    } else {
        Write-Log "Adding origin remote."
        Invoke-LoggedGit remote add origin $RemoteUrl
    }
}

Invoke-LoggedGit add -A
$status = (& git status --porcelain)
if (-not [string]::IsNullOrWhiteSpace(($status -join "`n"))) {
    $message = "CODEX backup $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Invoke-LoggedGit commit -m $message
} else {
    Write-Log "No file changes to commit."
}

if ($SkipPush) {
    Write-Log "SkipPush supplied. GitHub push skipped."
    Write-Log "Backup complete."
    exit 0
}

$origin = (& git remote get-url origin) 2>$null
if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($origin)) {
    Write-Log "Pushing branch '$Branch' to origin: $origin"
    Invoke-LoggedGit push -u origin $Branch
    Write-Log "GitHub push complete."
} else {
    Write-Log "No origin remote configured. Local git backup is complete; GitHub push skipped."
    Write-Log "To enable GitHub backup, rerun with -RemoteUrl 'https://github.com/OWNER/REPO.git'."
}

Write-Log "Backup complete."

