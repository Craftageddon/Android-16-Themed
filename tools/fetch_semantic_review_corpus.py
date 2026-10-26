"""Acquire every indexed resource byte at its pinned revision; inspect as data only."""
from pathlib import Path
import argparse,base64,concurrent.futures,hashlib,json,threading,time,urllib.parse,urllib.request
from audit_os_resource_coverage import ROOT,read_json

OUT=ROOT/'iterations/20-semantic-review'
INPUT=ROOT/'iterations/19-os-resource-audit'

def sha_blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=8);args=parser.parse_args()
    assert not (OUT/'complete-assets.zip').exists(),'Preserve packaged checkpoints'
    OUT.mkdir(parents=True,exist_ok=True);objects=OUT/'source/objects';objects.mkdir(parents=True,exist_ok=True)
    files=read_json(INPUT/'resource-files.json');projects={x['project']['path']:x['project'] for x in read_json(INPUT/'source-projects.json')};groups={}
    for row in files:groups.setdefault(row['gitBlobSha1'],[]).append(row)
    # Reuse already verified source evidence without downloading it again.
    seeded=0
    for row in read_json(INPUT/'source-evidence.json'):
        sha=row['gitBlobSha1']
        if sha not in groups:continue
        p=objects/sha[:2]/sha[2:];p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():
            data=(INPUT/row['saved']).read_bytes();assert sha_blob(data)==sha;p.write_bytes(data);seeded+=1
    lock=threading.Lock();completed=[];errors=[];count=0;start=time.monotonic()
    def fetch(item):
        nonlocal count
        sha,rows=item;row=rows[0];p=objects/sha[:2]/sha[2:];project=projects[row['project']]
        encoded=urllib.parse.quote(row['path'],safe='/')
        if project.get('remote')=='aosp':url=f"https://android.googlesource.com/{project['name']}/+/{project['revision']}/{encoded}?format=TEXT"
        else:url=f"https://raw.githubusercontent.com/{project['name']}/{project['revision']}/{encoded}"
        if p.exists():data=p.read_bytes()
        else:
            for attempt in range(4):
                try:
                    request=urllib.request.Request(url,headers={'User-Agent':'Craftageddon-content-semantic-review'})
                    with urllib.request.urlopen(request,timeout=60) as response:data=response.read()
                    if project.get('remote')=='aosp':data=base64.b64decode(data,validate=True)
                    break
                except Exception:
                    if attempt==3:raise
                    time.sleep(min(2**attempt,4))
            assert sha_blob(data)==sha,'Source Git blob mismatch: '+row['path']
            p.parent.mkdir(parents=True,exist_ok=True);temporary=p.with_suffix('.downloading');temporary.write_bytes(data);temporary.replace(p)
        assert sha_blob(data)==sha,'Cached source mismatch: '+row['path']
        if row.get('bytes',0):assert len(data)==row['bytes'],row['path']
        entry={'gitBlobSha1':sha,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'object':p.relative_to(OUT).as_posix(),'sourceCount':len(rows),'exampleProject':row['project'],'examplePath':row['path'],'url':url}
        with lock:
            count+=1
            if count%250==0:print(json.dumps({'verifiedObjects':count,'total':len(groups),'elapsedSeconds':round(time.monotonic()-start)}),flush=True)
        return entry
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending={pool.submit(fetch,item):item[0] for item in groups.items()}
        for job in concurrent.futures.as_completed(pending):
            try:completed.append(job.result())
            except Exception as e:errors.append({'gitBlobSha1':pending[job],'error':str(e)});print(json.dumps(errors[-1]),flush=True)
    completed.sort(key=lambda x:x['gitBlobSha1']);(OUT/'source-objects.json').write_text(json.dumps(completed,indent=2)+'\n',encoding='utf8');(OUT/'source-fetch-errors.json').write_text(json.dumps(errors,indent=2)+'\n',encoding='utf8')
    report={'date':'2026-10-26','indexedFiles':len(files),'uniqueObjectsExpected':len(groups),'verifiedObjects':len(completed),'verifiedBytes':sum(x['bytes'] for x in completed),'reusedEvidenceObjects':seeded,'errors':len(errors),'allSourceBytesAcquired':not errors and len(completed)==len(groups),'method':'Every object is fetched at its exact pinned public source revision; Git blob SHA1 and SHA256 checked; no upstream code executed'}
    (OUT/'source-acquisition.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report),flush=True)
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
