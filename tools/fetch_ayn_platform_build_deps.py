"""Read the official pinned SDK's actual Material/Preference library declarations."""
from pathlib import Path
import base64,concurrent.futures,gzip,hashlib,json,re,urllib.error,zipfile
from audit_os_resource_coverage import ROOT,get,write_json

OUT=ROOT/'iterations/21-native-workflows';REV='0f07e8d60ab0aba46129e427101f96ba459a95c1';URL='https://android.googlesource.com/platform/prebuilts/sdk/+/'+REV+'/'

def main():
    directory='current/androidx/';raw=get(URL+directory+'?format=JSON');listing=json.loads(raw[raw.index(b'\n')+1:]);node=next(x for x in listing['entries'] if x['name']=='Android.bp');data=base64.b64decode(get(URL+directory+'Android.bp?format=TEXT'));sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert sha==node['id'];dest=OUT/'source/build-dependencies';dest.mkdir(parents=True,exist_ok=True);(dest/'Android.bp').write_bytes(data);(dest/'directory.json.gz').write_bytes(gzip.compress(raw,mtime=0));text=data.decode('utf8');modules=[]
    for block in re.finditer(r'android_library_import\s*\{(.*?)\n\}',text,re.S):
        body=block.group(1);name=re.search(r'name:\s*"([^"]+)"',body);aars=re.search(r'aars:\s*\[(.*?)\]',body,re.S)
        if name and aars:modules.append({'name':name.group(1),'aars':re.findall(r'"([^"]+)"',aars.group(1)),'body':body})
    wanted=[x for x in modules if x['name'] in ['com.google.android.material_material','androidx.appcompat_appcompat','androidx.appcompat_appcompat-resources','androidx.preference_preference']]
    candidates=['current/androidx/m2repository/androidx/appcompat/appcompat/','current/androidx/m2repository/androidx/appcompat/appcompat-resources/','current/androidx/m2repository/androidx/preference/preference/','current/extras/material-design-x/']
    def inspect(path):
        try:
            raw=get(URL+path+'?format=JSON');obj=json.loads(raw[raw.index(b'\n')+1:]);return {'path':path,'entries':obj['entries'],'directoryPayloadSha256':hashlib.sha256(raw).hexdigest()}
        except urllib.error.HTTPError as e:
            if e.code==404:return {'path':path,'missing':True}
            raise
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:listings=list(pool.map(inspect,candidates))
    write_json(dest/'artifact-directories.json',listings)
    aar_jobs=[];bp_receipts=[];cache=ROOT/'build-work/ayn21-platform-dependencies';cache.mkdir(parents=True,exist_ok=True)
    def verified(path,node):
        target=cache/path.replace('/','__');payload=target.read_bytes() if target.exists() else base64.b64decode(get(URL+path+'?format=TEXT'));blob=hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest();assert blob==node['id'],path
        if not target.exists():target.write_bytes(payload)
        return target,{'path':path,'gitBlobSha1':blob,'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload),'localBuildCache':str(target),'url':URL+path+'?format=TEXT'}
    for listing in listings:
        if listing.get('missing'):continue
        path=listing['path']
        if path.endswith('material-design-x/'):
            bp_node=next(x for x in listing['entries'] if x['name']=='Android.bp');bp,bp_receipt=verified(path+'Android.bp',bp_node);bp_receipts.append(bp_receipt);body=bp.read_text();(dest/'material-Android.bp').write_bytes(bp.read_bytes());wanted_paths=re.findall(r'"([^"\n]+\.aar)"',body)
            assert 'com.google.android.material_material' in body,'This is not the native Material Components module'
            for relative in wanted_paths:
                full=path+relative;parent=full.rsplit('/',1)[0]+'/';metadata=inspect(parent);node=next(x for x in metadata['entries'] if x['name']==full.rsplit('/',1)[1]);aar_jobs.append((full,node))
        else:
            versions=[x for x in listing['entries'] if x['type']=='tree'];assert len(versions)==1,(path,versions);parent=path+versions[0]['name']+'/';metadata=inspect(parent)
            for node in metadata['entries']:
                if node['name'].endswith('.aar'):aar_jobs.append((parent+node['name'],node))
    def fetch_aar(job):
        target,receipt=verified(*job)
        with zipfile.ZipFile(target) as z:assert z.testzip() is None;assert 'classes.jar' in z.namelist();classes=target.with_suffix('.classes.jar');classes.write_bytes(z.read('classes.jar'))
        receipt['classesJar']=str(classes);receipt['classesSha256']=hashlib.sha256(classes.read_bytes()).hexdigest();return receipt
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:aar_receipts=list(pool.map(fetch_aar,aar_jobs))
    write_json(dest/'pinned-aar-receipts.json',{'repository':'platform/prebuilts/sdk','revision':REV,'bpSources':bp_receipts,'libraries':aar_receipts,'scope':'Exact official source-pin dependency bytes for compilation; not redistributed as Craftageddon art, not executed on hardware.'})
    write_json(dest/'pinned-module-declarations.json',{'repository':'platform/prebuilts/sdk','revision':REV,'directory':directory,'androidBpGitBlobSha1':sha,'androidBpSha256':hashlib.sha256(data).hexdigest(),'modules':wanted});print(json.dumps({'revision':REV,'fetchedActualAars':len(aar_receipts),'paths':[x['path'] for x in aar_receipts]}))

if __name__=='__main__':main()
