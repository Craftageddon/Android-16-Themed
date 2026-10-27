'''Acquire exact committed Gallery libraries and native drawable-inflation contract.'''
import concurrent.futures,hashlib,json,base64,urllib.parse
from pathlib import Path
from audit_os_resource_coverage import ROOT,read_json,write_json,get
OUT=ROOT/'iterations/26-gallery-workflows';AUDIT=ROOT/'iterations/19-os-resource-audit'
def main():
    assert not (OUT/'complete-assets.zip').exists()
    project=next(r['project'] for r in read_json(AUDIT/'source-projects.json') if r['project']['path']=='packages/apps/Glimpse')
    tree=read_json(AUDIT/'source-trees/packages__apps__Glimpse.json')['tree']
    jobs=[r for r in tree if r['type']=='blob' and r['path'].endswith(('.aar','.jar','.properties'))]
    def fetch(n):
        p=OUT/'upstream'/project['path']/n['path'];url='https://raw.githubusercontent.com/'+project['name']+'/'+project['revision']+'/'+urllib.parse.quote(n['path'],safe='/')
        data=p.read_bytes() if p.exists() else get(url)
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==n['sha'],n['path']
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        return {'project':project['path'],'revision':project['revision'],'path':n['path'],'url':url,'gitBlobSha1':blob,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'saved':p.relative_to(OUT).as_posix(),'downloadedNotExecuted':True}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=sorted(pool.map(fetch,jobs),key=lambda r:r['path'])
    write_json(OUT/'source-binary-dependencies.json',rows)
    pin='7f6de40b6429462d47ba9ba351b99943269c8067';path='graphics/java/android/graphics/drawable/DrawableInflater.java'
    url='https://api.github.com/repos/LineageOS/android_frameworks_base/contents/'+path+'?ref='+pin
    meta=json.loads(get(url));data=base64.b64decode(meta['content'])
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==meta['sha']
    p=OUT/'source/pinned-framework'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    write_json(OUT/'source/framework-drawable-contract.json',{'project':'frameworks/base','revision':pin,'path':path,'url':url,'gitBlobSha1':meta['sha'],'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'saved':p.relative_to(OUT).as_posix(),'sourceOnlyNotExecuted':True})
    print({'committedDependencyFiles':len(rows),'bytes':sum(r['bytes'] for r in rows),'frameworkContractBytes':len(data),'executed':False})
if __name__=='__main__':main()
