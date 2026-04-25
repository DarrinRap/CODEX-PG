<#
.SYNOPSIS
Builds a read-only inventory of C:\panda-gallery for Codex reference.

.DESCRIPTION
This script reads C:\panda-gallery and writes inventory files into
C:\CODEX PG\CODEX Panda Gallery Readonly Reference. It does not write
inside C:\panda-gallery.
#>
[CmdletBinding()]
param(
    [string]$SourceRoot = "C:\panda-gallery",
    [string]$OutputRoot = "C:\CODEX PG\CODEX Panda Gallery Readonly Reference"
)

$ErrorActionPreference = "Stop"
$source = (Resolve-Path -LiteralPath $SourceRoot).Path
$output = (Resolve-Path -LiteralPath $OutputRoot).Path

if ($source.TrimEnd('\').ToLowerInvariant() -ne "c:\panda-gallery") {
    throw "Refusing unexpected source path: $source"
}
if (-not $output.TrimEnd('\').ToLowerInvariant().StartsWith("c:\codex pg\codex panda gallery readonly reference")) {
    throw "Refusing unexpected output path: $output"
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
$allFiles = Get-ChildItem -LiteralPath $source -Recurse -File -Force -ErrorAction SilentlyContinue
$summaryPath = Join-Path $output "CODEX_PANDA_GALLERY_INVENTORY.md"
$csvPath = Join-Path $output "CODEX_PANDA_GALLERY_FILE_INDEX.csv"

$allFiles |
    Select-Object FullName, Length, LastWriteTime, Extension |
    Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

$topExtensions = $allFiles |
    Group-Object Extension |
    Sort-Object Count -Descending |
    Select-Object -First 25

$topDirs = $allFiles |
    ForEach-Object {
        $relative = $_.FullName.Substring($source.Length).TrimStart('\')
        $first = ($relative -split '\\')[0]
        if ([string]::IsNullOrWhiteSpace($first)) { '<root>' } else { $first }
    } |
    Group-Object |
    Sort-Object Count -Descending |
    Select-Object -First 30

$lines = @()
$lines += '# CODEX Panda Gallery File Inventory'
$lines += ''
$lines += "Generated: $timestamp"
$lines += ''
$lines += 'Source: `C:\panda-gallery`'
$lines += ''
$lines += "Total files indexed: $($allFiles.Count)"
$lines += ''
$lines += '## Top Extensions'
$lines += ''
foreach ($group in $topExtensions) {
    $name = if ([string]::IsNullOrWhiteSpace($group.Name)) { '<none>' } else { $group.Name }
    $lines += "- `$name`: $($group.Count)"
}
$lines += ''
$lines += '## Top-Level File Distribution'
$lines += ''
foreach ($group in $topDirs) {
    $lines += "- `$($group.Name)`: $($group.Count)"
}
$lines += ''
$lines += '## Detailed CSV Index'
$lines += ''
$lines += '`CODEX_PANDA_GALLERY_FILE_INDEX.csv`'
$lines += ''
$lines += 'This inventory is a read-only reference artifact. It was written into the Codex workspace, not into `C:\panda-gallery`.'

$lines | Set-Content -Path $summaryPath -Encoding UTF8
Write-Host "Indexed $($allFiles.Count) files from $source"
Write-Host "Wrote $summaryPath"
Write-Host "Wrote $csvPath"
