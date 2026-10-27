"""Acquire only pinned AndroidX compilation artifacts, preserving source identities."""
import base64,hashlib,concurrent.futures,zipfile,json
from pathlib import Path
from audit_os_resource_coverage import ROOT,read_json,write_json,get
OUT=ROOT/'iterations/26-gallery-workflows';PIN='0f07e8d60ab0aba46129e427101f96ba459a95c1'
BASE='https://android.googlesource.com/platform/prebuilts/sdk/+/'+PIN+'/'
CACHE=ROOT/'build-work/gallery26-platform';CACHE.mkdir(parents=True,exist_ok=True)
ARTIFACTS=['navigationevent/navigationevent-android','core/core','core/core-viewtree','recyclerview/recyclerview','activity/activity','lifecycle/lifecycle-common-jvm','lifecycle/lifecycle-runtime-android','lifecycle/lifecycle-viewmodel-android','savedstate/savedstate-android','annotation/annotation-jvm','annotation/annotation-experimental','customview/customview','customview/customview-poolingcontainer','coordinatorlayout/coordinatorlayout','drawerlayout/drawerlayout','fragment/fragment','lifecycle/lifecycle-livedata-core']
def listing(path):return json.loads(get(BASE+path+'/?format=JSON')[4:])['entries']
def save(path,node):
    f=CACHE/path.replace('/','__');data=f.read_bytes() if f.exists() else base64.b64decode(get(BASE+path+'?format=TEXT'))
    git=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert git==node['id'],path
    f.write_bytes(data)
    r={'path':path,'url':BASE+path+'?format=TEXT','gitBlobSha1':git,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'localBuildCache':str(f)}
    if f.suffix=='.aar':
        with zipfile.ZipFile(f) as z:jar=z.read('classes.jar');symbols=z.read('R.txt')
        jf=f.with_suffix('.classes.jar');jf.write_bytes(jar);r['classesJar']=str(jf);r['classesSha256']=hashlib.sha256(jar).hexdigest();rf=f.with_suffix('.R.txt');rf.write_bytes(symbols);r['resourceSymbols']=str(rf)
    elif f.suffix=='.jar':r['classesJar']=str(f);r['classesSha256']=r['sha256']
    return r

def fetch(artifact):
    p='current/androidx/m2repository/androidx/'+artifact;versions=listing(p);assert len(versions)==1,(artifact,versions)
    version=versions[0]['name'];p+='/'+version;nodes=listing(p);leaf=artifact.rsplit('/',1)[-1]+'-'+version
    libs=[n for n in nodes if n['name'] in [leaf+'.aar',leaf+'.jar']];assert len(libs)==1,(artifact,libs)
    bp=next(n for n in nodes if n['name']=='Android.bp');br=save(p+'/Android.bp',bp);r=save(p+'/'+libs[0]['name'],libs[0]);r['buildDeclaration']=br;r['artifact']=artifact;r['version']=version;return r

def main():
    assert not (OUT/'complete-assets.zip').exists()
    existing=read_json(OUT/'source/platform-dependencies.json')['libraries'] if (OUT/'source/platform-dependencies.json').exists() else []
    cached={r.get('artifact'):r for r in existing if r.get('artifact')}
    for r in cached.values():assert hashlib.sha256(Path(r['localBuildCache']).read_bytes()).hexdigest()==r['sha256']
    missing=[a for a in ARTIFACTS if a not in cached]
    with concurrent.futures.ThreadPoolExecutor(3) as pool:downloaded=list(pool.map(fetch,missing))
    cached.update({r['artifact']:r for r in downloaded});rows=[cached[a] for a in ARTIFACTS]
    earlier=read_json(ROOT/'iterations/21-native-workflows/source/build-dependencies/pinned-aar-receipts.json')
    for r in earlier['libraries']:
        if '/appcompat/' in r['path'] or '/preference/' in r['path']:
            f=Path(r['localBuildCache']);assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];copy=dict(r)
            with zipfile.ZipFile(f) as z:symbols=z.read('R.txt')
            rf=CACHE/(f.stem+'.R.txt');rf.write_bytes(symbols);copy['resourceSymbols']=str(rf);rows.append(copy)
    write_json(OUT/'source/platform-dependencies.json',{'repository':'platform/prebuilts/sdk','revision':PIN,'libraries':rows,'purpose':'Actual source API compatibility compile, not Soong build','licenses':'Original dependency licenses retained in source artifacts; no relicensing.'})
    print({'pinnedLibraries':len(rows),'bytes':sum(r['bytes'] for r in rows)})
if __name__=='__main__':main()
