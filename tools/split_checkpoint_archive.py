"""Transport a complete hash-bound ZIP in small GitHub blobs without changing its bytes."""
from pathlib import Path
import argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root.resolve();archive=root/'complete-assets.zip';out=root/'distribution';out.mkdir(exist_ok=False)
rows=[];joined=hashlib.sha256();size=12*1024*1024
with archive.open('rb') as stream:
 i=1
 while chunk:=stream.read(size):
  file=out/f'complete-assets.zip.part{i:02}';file.write_bytes(chunk);joined.update(chunk);rows.append({'file':file.name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()});i+=1
digest=hashlib.sha256(archive.read_bytes()).hexdigest();assert joined.hexdigest()==digest
manifest={'archive':'complete-assets.zip','bytes':archive.stat().st_size,'sha256':digest,'parts':rows,'restore':'Run Restore-Archive.ps1 from this directory; it verifies each part and the assembled ZIP. Full ZIP is also preserved in local deliverables.'}
(out/'ARCHIVE-PARTS.json').write_text(json.dumps(manifest,indent=2)+'\n')
script=r'''[CmdletBinding()]
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
'''
(out/'Restore-Archive.ps1').write_text(script,encoding='utf8')
print(json.dumps({'parts':len(rows),'bytes':archive.stat().st_size,'assembledSha256':digest}))
