"""Acquire an explicitly identified factory candidate without running its contents.

Stored outside the Git checkout. HTML/quota/confirmation responses are recorded
as failures, never renamed into a usable ROM. Provenance remains unverified.
"""
from pathlib import Path
import argparse,hashlib,json,time,urllib.request

p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
url='https://drive.usercontent.google.com/download?id=1juGydm1H_PF-ECImn-8t4tWWYSaW0oZ1&export=download&authuser=0&confirm=t'
report={'candidate':'Thor_20260112.7z','sourcePage':'https://drive.google.com/file/d/1juGydm1H_PF-ECImn-8t4tWWYSaW0oZ1/view','manufacturerProvenanceVerified':False,'executed':False,'flashed':False,'status':'starting','bytes':0}
target=out/'Thor_20260112.7z';partial=out/'Thor_20260112.7z.partial';assert not target.exists() and not partial.exists()
try:
 req=urllib.request.Request(url,headers={'User-Agent':'Craftageddon-Firmware-Research/1.0'})
 with urllib.request.urlopen(req,timeout=45) as response:
  head=response.read(65536);report['contentType']=response.headers.get('Content-Type');report['reportedBytes']=response.headers.get('Content-Length');report['contentDisposition']=response.headers.get('Content-Disposition')
  assert head.startswith(bytes.fromhex('377abcaf271c')),'Response is not a 7z archive; sign-in/quota/confirmation may be required'
  digest=hashlib.sha256();digest.update(head);count=len(head);last=time.monotonic()
  with partial.open('xb') as stream:
   stream.write(head)
   while data:=response.read(1024*1024):
    count+=len(data);assert count<=12*1024**3,'Unexpected archive size exceeds acquisition limit';stream.write(data);digest.update(data)
    if time.monotonic()-last>=15:print(json.dumps({'downloadedMiB':round(count/1024**2,1)}),flush=True);last=time.monotonic()
  assert not report['reportedBytes'] or int(report['reportedBytes'])==count,'Incomplete response'
  partial.rename(target);report.update(status='downloaded-unverified',bytes=count,sha256=digest.hexdigest(),archiveIntegrityVerified=False)
except Exception as e:report.update(status='acquisition-failed',error=str(e),partialBytes=partial.stat().st_size if partial.exists() else 0)
(out/'candidate-acquisition.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if report['status']!='downloaded-unverified':raise SystemExit(1)
