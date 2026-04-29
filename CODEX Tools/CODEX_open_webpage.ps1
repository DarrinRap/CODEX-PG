param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Url
)

$ErrorActionPreference = 'Stop'

$Url = $Url.Trim()

if (-not $Url) {
    throw 'URL is required.'
}

if ($Url -notmatch '^(https?://|file:///)' ) {
    $Url = "https://$Url"
}

$null = Start-Process $Url -PassThru
Write-Host "Opened $Url"
