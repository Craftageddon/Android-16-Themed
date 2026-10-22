"""Prepare committed bytes for GitHub Git-data upload with secret-path guards."""
from pathlib import Path
import argparse,base64,hashlib,json,subprocess,zipfile

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--base',required=True);a=p.parse_args();root=a.root.resolve();dest=a.out.resolve();dest.mkdir(parents=True,exist_ok=False)
names=[x for x in subprocess.check_output(['git','-c','core.bare=false','diff','--name-only','-z',a.base,'HEAD'],cwd=root).decode().split('\0') if x]
private_markers=[('-----BEGIN '+s+'-----').encode() for s in ['PRIVATE KEY','RSA PRIVATE KEY','ENCRYPTED PRIVATE KEY','EC PRIVATE KEY']]
def allowed(name,data=None):
 path=Path(name);assert not {'local-secrets','build-work','__pycache__'}&set(path.parts),'Private/build path in publication'
 assert path.suffix not in ['.pk8','.jks','.keystore','.p12','.pfx','.key','.idsig'],'Private/signing sidecar in publication'
 if data is not None:assert not any(marker in data for marker in private_markers),'Private key marker in publication'
for archive in (root/'iterations').glob('*/complete-assets.zip'):
 with zipfile.ZipFile(archive) as z:
  for name in z.namelist():allowed(name,z.read(name))
chunks=[];chunk=[];length=0;binaries=[]
for i,name in enumerate(names):
 file=root/name;allowed(name)
 if not file.exists():
  item={'path':name,'mode':'100644','type':'blob','sha':None}
 else:
  data=file.read_bytes();allowed(name,data);sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  try:content=data.decode('utf8')
  except UnicodeDecodeError:content=None
  if content is None or len(data)>80000 or file.suffix in ['.png','.zip','.apk','.sig']:
   b64=base64.b64encode(data).decode();blob=dest/f'blob-{i:04}.txt';blob.write_text(b64,encoding='ascii');binaries.append({'path':name,'file':str(blob),'chars':len(b64),'sha':sha});continue
  item={'path':name,'mode':'100644','type':'blob','content':content}
 encoded=json.dumps(item)
 if length+len(encoded)>440000 and chunk:chunks.append(chunk);chunk=[];length=0
 chunk.append(item);length+=len(encoded)
if chunk:chunks.append(chunk)
for i,entries in enumerate(chunks):(dest/f'tree-{i}.json').write_text(json.dumps(entries),encoding='utf8')
(dest/'binary.json').write_text(json.dumps(binaries));plan={'textChunks':len(chunks),'binaryFiles':len(binaries),'changedFiles':len(names),'privatePathAndKeyMarkerGuard':'PASS'};(dest/'plan.json').write_text(json.dumps(plan));print(json.dumps(plan))
