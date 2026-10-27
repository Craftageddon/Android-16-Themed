'''Acquire the complete pinned Gallery source/presentation input set; no app execution.'''
from pathlib import Path
import concurrent.futures,hashlib,json,urllib.parse,re
from audit_os_resource_coverage import ROOT,read_json,write_json,get
OUT=ROOT/'iterations/26-gallery-workflows';AUDIT=ROOT/'iterations/19-os-resource-audit';BASE=ROOT/'iterations/20-semantic-review'
def main():
    assert not (OUT/'complete-assets.zip').exists()
    project=next(x['project'] for x in read_json(AUDIT/'source-projects.json') if x['project']['path']=='packages/apps/Glimpse')
    tree=read_json(AUDIT/'source-trees/packages__apps__Glimpse.json')['tree']
    jobs=[n for n in tree if n['type']=='blob' and (
        n['path'].endswith(('.kt','.java','.bp','.toml','.gradle.kts','.pro')) or
        n['path'] in ['LICENSE','NOTICE','COPYING','REUSE.toml','app/src/main/AndroidManifest.xml'] or
        (n['path'].endswith('.xml') and '/res/values-' not in n['path']) or
        ('/res/values-' in n['path'] and not re.fullmatch(r'[a-z]{2,3}(?:-r[A-Z]{2})?',n['path'].split('/res/values-',1)[1].split('/')[0])))]
    def fetch(node):
        path=node['path'];dest=OUT/'upstream'/project['path']/path
        cached=BASE/'source/objects'/node['sha'][:2]/node['sha'][2:]
        prior=AUDIT/'source-evidence'/project['path']/path
        url='https://raw.githubusercontent.com/'+project['name']+'/'+project['revision']+'/'+urllib.parse.quote(path,safe='/')
        data=dest.read_bytes() if dest.exists() else cached.read_bytes() if cached.exists() else prior.read_bytes() if prior.exists() else get(url)
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert actual==node['sha'],path
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        return {'project':project['path'],'repository':project['name'],'revision':project['revision'],'path':path,'url':url,
            'gitBlobSha1':actual,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'saved':dest.relative_to(OUT).as_posix(),
            'sourceOnlyNotExecuted':True}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=sorted(pool.map(fetch,jobs),key=lambda r:r['path'])
    write_json(OUT/'source-manifest.json',rows)
    write_json(OUT/'WORK-IN-PROGRESS.json',{'base':'dc2fa9aa2d5e34c04bd852db548fa5d773eae885','workflow':'W-05','revision':project['revision'],'sourceFiles':len(rows),'adaptation':'NOT YET AUTHORED','wholeGoalComplete':False})
    print(json.dumps({'pinnedSourceFiles':len(rows),'bytes':sum(r['bytes'] for r in rows),'revision':project['revision'],'codeExecuted':False}))
if __name__=='__main__':main()
