param(
    [string]$InputFile,
    [string]$OutputDir
)

Add-Type -AssemblyName System.IO.Compression

if (-not (Test-Path $InputFile)) {
    Write-Error "File not found: $InputFile"
    exit 1
}

$bytes = [System.IO.File]::ReadAllBytes($InputFile)

# Check RDS5
$magic = [System.Text.Encoding]::ASCII.GetString($bytes, 0, 4)
if ($magic -ne "RDS5") {
    Write-Error "Not an RDS5 file: $magic"
    exit 1
}

$chunkCount = [BitConverter]::ToInt32($bytes, 4)
Write-Output "Found RDS5 container: $InputFile"
Write-Output "Header Chunk Count: $chunkCount"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Find ETPF offset
$etpfOffset = -1
for ($i = 0x20; $i -lt [Math]::Min(0x2000, $bytes.Length - 4); $i += 4) {
    if ($bytes[$i] -eq 0x45 -and $bytes[$i+1] -eq 0x54 -and $bytes[$i+2] -eq 0x50 -and $bytes[$i+3] -eq 0x46) {
        $etpfOffset = $i
        break
    }
}
Write-Output "ETPF header at: 0x$($etpfOffset.ToString('X4'))"

# Read Chunk entries
$entries = @()
for ($i = 0; $i -lt $chunkCount; $i++) {
    $off = 0x18 + ($i * 8)
    $val1 = [BitConverter]::ToUInt32($bytes, $off)
    $val2 = [BitConverter]::ToUInt32($bytes, $off + 4)
    $blockIndex = $val1 -band 0x00FFFFFF
    $fileOffset = $blockIndex * 256
    $entries += [PSCustomObject]@{
        Index = $i
        FileOffset = $fileOffset
        Val1 = $val1
        Val2 = $val2
    }
}

# Decompress all chunks
$allDecomp = New-Object System.IO.MemoryStream
$successCount = 0

for ($i = 0; $i -lt ($entries.Count - 1); $i++) {
    $start = $entries[$i].FileOffset
    $end = $entries[$i+1].FileOffset
    $len = $end - $start
    if ($len -le 0 -or ($start + $len) -gt $bytes.Length) { continue }
    
    # Check zlib header (0x78 0xDA / 0x78 0x9C / 0x78 0x01)
    if ($bytes[$start] -eq 0x78) {
        try {
            $ms = New-Object System.IO.MemoryStream($bytes, ($start + 2), ($len - 2))
            $ds = New-Object System.IO.Compression.DeflateStream($ms, [System.IO.Compression.CompressionMode]::Decompress)
            $outChunk = New-Object System.IO.MemoryStream
            $ds.CopyTo($outChunk)
            $chunkData = $outChunk.ToArray()
            $allDecomp.Write($chunkData, 0, $chunkData.Length)
            
            # Save individual page
            [System.IO.File]::WriteAllBytes("$OutputDir\tile_$($i.ToString('D4')).bin", $chunkData)
            $successCount++
        } catch {
            Write-Warning "Failed to decompress chunk $i at offset 0x$($start.ToString('X'))"
        }
    }
}

$fullData = $allDecomp.ToArray()
$outCombined = "$OutputDir\_full_decompressed.bin"
[System.IO.File]::WriteAllBytes($outCombined, $fullData)

Write-Output "Successfully unpacked $successCount tiles (total $($fullData.Length) bytes = $($fullData.Length / 1024) KB) to $OutputDir"
