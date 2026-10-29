param([string]$OutputPath)
$ErrorActionPreference = 'Stop'
$pilotRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$pilotIndex = Get-Content -Raw -LiteralPath (Join-Path $pilotRoot 'archive-index.json') | ConvertFrom-Json
if (-not $OutputPath) { $OutputPath = Join-Path (Split-Path $pilotRoot -Parent) $pilotIndex.archive }
$pilotTarget = [IO.Path]::GetFullPath($OutputPath)
if (Test-Path -LiteralPath $pilotTarget) {
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $pilotTarget).Hash -ne $pilotIndex.sha256) {
        throw 'The destination exists with different contents. Choose a new output filename.'
    }
    Write-Output "Verified existing archive: $pilotTarget"
    return
}
$pilotFiles = @()
foreach ($pilotPart in $pilotIndex.parts) {
    $pilotPath = [IO.Path]::GetFullPath((Join-Path $pilotRoot $pilotPart.path))
    if (-not $pilotPath.StartsWith($pilotRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Archive part path leaves the distribution folder.'
    }
    $pilotFile = Get-Item -LiteralPath $pilotPath
    if ($pilotFile.Length -ne $pilotPart.bytes) { throw "Part length mismatch: $pilotPath" }
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $pilotPath).Hash -ne $pilotPart.sha256) { throw "Part hash mismatch: $pilotPath" }
    $pilotFiles += $pilotPath
}
$pilotStream = [IO.File]::Open($pilotTarget, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
try {
    foreach ($pilotPath in $pilotFiles) {
        $pilotInput = [IO.File]::OpenRead($pilotPath)
        try { $pilotInput.CopyTo($pilotStream) } finally { $pilotInput.Dispose() }
    }
} finally { $pilotStream.Dispose() }
if ((Get-Item -LiteralPath $pilotTarget).Length -ne $pilotIndex.bytes) { throw 'Restored archive length mismatch.' }
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $pilotTarget).Hash -ne $pilotIndex.sha256) { throw 'Restored archive hash mismatch.' }
Write-Output "Verified archive: $pilotTarget"
Write-Output 'Extract into a new folder and open index.html to review all corrected artwork.'
