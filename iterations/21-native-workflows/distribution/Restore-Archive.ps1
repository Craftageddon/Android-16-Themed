[CmdletBinding()]
param([string]$Destination = '')
$ErrorActionPreference = 'Stop'
$archiveManifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'ARCHIVE-PARTS.json') -Raw | ConvertFrom-Json
if (-not $Destination) { $Destination = Join-Path $PSScriptRoot '..\complete-assets.zip' }
$archiveTarget = [IO.Path]::GetFullPath($Destination)
if (Test-Path -LiteralPath $archiveTarget) {
    if ((Get-FileHash -LiteralPath $archiveTarget -Algorithm SHA256).Hash.ToLowerInvariant() -eq $archiveManifest.sha256) { Write-Output "Already verified: $archiveTarget"; return }
    throw 'Destination already exists with different contents. Choose an empty destination.'
}
$archiveTemporary = $archiveTarget + '.' + [Guid]::NewGuid().ToString('N') + '.restoring'
$archiveOutput = [IO.File]::Open($archiveTemporary, [IO.FileMode]::CreateNew)
try {
    foreach ($archivePart in $archiveManifest.parts) {
        $archivePartPath = Join-Path $PSScriptRoot $archivePart.file
        if ((Get-FileHash -LiteralPath $archivePartPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $archivePart.sha256) { throw "Part checksum failed: $($archivePart.file)" }
        $archiveInput = [IO.File]::OpenRead($archivePartPath)
        try { $archiveInput.CopyTo($archiveOutput) } finally { $archiveInput.Dispose() }
    }
} finally { $archiveOutput.Dispose() }
if ((Get-Item -LiteralPath $archiveTemporary).Length -ne $archiveManifest.bytes) { throw 'Assembled size mismatch' }
if ((Get-FileHash -LiteralPath $archiveTemporary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $archiveManifest.sha256) { throw 'Assembled checksum mismatch' }
Move-Item -LiteralPath $archiveTemporary -Destination $archiveTarget
Write-Output "Verified complete archive: $archiveTarget"
