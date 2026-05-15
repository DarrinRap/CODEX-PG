$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing

$AssetsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$IconPath = Join-Path $AssetsDir 'PANDA_Agent_Hub_panda_tray.ico'
$PreviewPath = Join-Path $AssetsDir 'PANDA_Agent_Hub_panda_tray_256.png'

function New-PandaTrayBitmap {
    param([int]$Size)

    $bitmap = New-Object System.Drawing.Bitmap $Size, $Size, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $graphics.Clear([System.Drawing.Color]::Transparent)

    $scale = $Size / 256.0
    function N([double]$Value) { return [float]($Value * $scale) }
    function Rect([double]$X, [double]$Y, [double]$W, [double]$H) {
        return New-Object System.Drawing.RectangleF (N $X), (N $Y), (N $W), (N $H)
    }

    $dark = [System.Drawing.Color]::FromArgb(255, 18, 22, 34)
    $peach = [System.Drawing.Color]::FromArgb(255, 232, 168, 124)
    $face = [System.Drawing.Color]::FromArgb(255, 248, 247, 242)
    $black = [System.Drawing.Color]::FromArgb(255, 12, 14, 18)
    $green = [System.Drawing.Color]::FromArgb(255, 72, 168, 95)

    $darkBrush = New-Object System.Drawing.SolidBrush $dark
    $peachPen = New-Object System.Drawing.Pen $peach, (N 13)
    $faceBrush = New-Object System.Drawing.SolidBrush $face
    $blackBrush = New-Object System.Drawing.SolidBrush $black
    $greenBrush = New-Object System.Drawing.SolidBrush $green
    $whitePen = New-Object System.Drawing.Pen ([System.Drawing.Color]::White), (N 10)
    $greenPen = New-Object System.Drawing.Pen $green, (N 5)

    try {
        $graphics.FillEllipse($darkBrush, (Rect 13 13 230 230))
        $graphics.DrawEllipse($peachPen, (Rect 15 15 226 226))

        # Panda silhouette tuned for the 16-32 px tray sizes.
        $graphics.FillEllipse($blackBrush, (Rect 54 47 58 58))
        $graphics.FillEllipse($blackBrush, (Rect 144 47 58 58))
        $graphics.FillEllipse($faceBrush, (Rect 50 63 156 142))
        $graphics.FillEllipse($blackBrush, (Rect 75 93 42 52))
        $graphics.FillEllipse($blackBrush, (Rect 139 93 42 52))
        $graphics.FillEllipse($faceBrush, (Rect 91 109 11 11))
        $graphics.FillEllipse($faceBrush, (Rect 154 109 11 11))
        $graphics.FillEllipse($blackBrush, (Rect 113 142 31 22))
        $graphics.DrawArc((New-Object System.Drawing.Pen $black, (N 7)), (Rect 98 147 31 28), 10, 130)
        $graphics.DrawArc((New-Object System.Drawing.Pen $black, (N 7)), (Rect 126 147 31 28), 40, 130)

        # Small health/status mark, visually linked to PAH's green ok state.
        $graphics.FillEllipse($greenBrush, (Rect 172 172 48 48))
        $graphics.DrawEllipse($whitePen, (Rect 172 172 48 48))
        $graphics.DrawLine($whitePen, (N 185), (N 197), (N 196), (N 207))
        $graphics.DrawLine($whitePen, (N 196), (N 207), (N 211), (N 184))
    }
    finally {
        $darkBrush.Dispose()
        $peachPen.Dispose()
        $faceBrush.Dispose()
        $blackBrush.Dispose()
        $greenBrush.Dispose()
        $whitePen.Dispose()
        $greenPen.Dispose()
        $graphics.Dispose()
    }

    return $bitmap
}

function Get-IcoDibBytes {
    param([System.Drawing.Bitmap]$Bitmap)
    $width = $Bitmap.Width
    $height = $Bitmap.Height
    $maskStride = [int]([Math]::Ceiling($width / 32.0) * 4)
    $pixelBytes = $width * $height * 4
    $maskBytes = $maskStride * $height

    $stream = New-Object System.IO.MemoryStream
    $writer = New-Object System.IO.BinaryWriter $stream
    try {
        # BITMAPINFOHEADER. ICO stores height as XOR bitmap + AND mask.
        $writer.Write([UInt32]40)
        $writer.Write([Int32]$width)
        $writer.Write([Int32]($height * 2))
        $writer.Write([UInt16]1)
        $writer.Write([UInt16]32)
        $writer.Write([UInt32]0)
        $writer.Write([UInt32]$pixelBytes)
        $writer.Write([Int32]0)
        $writer.Write([Int32]0)
        $writer.Write([UInt32]0)
        $writer.Write([UInt32]0)

        # BGRA pixels, bottom-up.
        for ($y = $height - 1; $y -ge 0; $y--) {
            for ($x = 0; $x -lt $width; $x++) {
                $c = $Bitmap.GetPixel($x, $y)
                $writer.Write([byte]$c.B)
                $writer.Write([byte]$c.G)
                $writer.Write([byte]$c.R)
                $writer.Write([byte]$c.A)
            }
        }

        # Transparent AND mask. Alpha channel carries the real transparency.
        $writer.Write((New-Object byte[] $maskBytes))
        return ,$stream.ToArray()
    }
    finally {
        $writer.Dispose()
    }
}

$sizes = @(16, 20, 24, 32, 40, 48, 64, 128, 256)
$entries = @()
foreach ($size in $sizes) {
    $bitmap = New-PandaTrayBitmap -Size $size
    try {
        if ($size -eq 256) {
            $bitmap.Save($PreviewPath, [System.Drawing.Imaging.ImageFormat]::Png)
        }
        $entries += [pscustomobject]@{
            Size = $size
            Bytes = Get-IcoDibBytes -Bitmap $bitmap
        }
    }
    finally {
        $bitmap.Dispose()
    }
}

$stream = New-Object System.IO.MemoryStream
$writer = New-Object System.IO.BinaryWriter $stream
try {
    $writer.Write([UInt16]0)
    $writer.Write([UInt16]1)
    $writer.Write([UInt16]$entries.Count)

    $offset = 6 + (16 * $entries.Count)
    foreach ($entry in $entries) {
        $sizeByte = if ($entry.Size -eq 256) { 0 } else { $entry.Size }
        $writer.Write([byte]$sizeByte)
        $writer.Write([byte]$sizeByte)
        $writer.Write([byte]0)
        $writer.Write([byte]0)
        $writer.Write([UInt16]1)
        $writer.Write([UInt16]32)
        $writer.Write([UInt32]$entry.Bytes.Length)
        $writer.Write([UInt32]$offset)
        $offset += $entry.Bytes.Length
    }
    foreach ($entry in $entries) {
        $writer.Write($entry.Bytes)
    }
    $iconBytes = $stream.ToArray()
}
finally {
    $writer.Dispose()
}

[System.IO.File]::WriteAllBytes($IconPath, $iconBytes)
Write-Host "Wrote $IconPath"
Write-Host "Wrote $PreviewPath"
