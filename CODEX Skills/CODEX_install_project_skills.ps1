param(
    [string]$DestinationRoot = "$env:USERPROFILE\.codex\skills"
)

$ErrorActionPreference = 'Stop'

$SourceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillFolders = @(
    'CODEX PG Project Orientation',
    'CODEX PG Code Review',
    'CODEX PG Claude Task Writer'
)

Write-Host "Installing CODEX PG project skills"
Write-Host "Source: $SourceRoot"
Write-Host "Destination: $DestinationRoot"

New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null

foreach ($folder in $SkillFolders) {
    $source = Join-Path $SourceRoot $folder
    $destination = Join-Path $DestinationRoot $folder

    if (-not (Test-Path -LiteralPath $source)) {
        throw "Missing source skill folder: $source"
    }

    if (Test-Path -LiteralPath $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }

    Copy-Item -LiteralPath $source -Destination $destination -Recurse
    Write-Host "Installed: $folder"
}

Write-Host "Done. Restart Codex or start a fresh session if the skills do not appear immediately."
