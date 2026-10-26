"""Resolve resource string/array data and native owner contracts outside the art count."""
from pathlib import Path
import base64,concurrent.futures,gzip,hashlib,json,re,urllib.parse
from audit_os_resource_coverage import ROOT,read_json,write_json,get

OUT=ROOT/'iterations/20-semantic-review';INPUT=ROOT/'iterations/19-os-resource-audit'

def main():
    assert not (OUT/'complete-assets.zip').exists()
    projects=read_json(INPUT/'source-projects.json');original={(x['project'],x['path']) for x in read_json(INPUT/'resource-files.json')};jobs={}
    owner_names={'PhoneStatusBarPolicy.java','DevelopmentTiles.java','SquigglyProgress.kt','IlluminationDrawable.kt','LightSourceDrawable.kt','CastDrawable.java','ScreenRecordDrawable.java','TintDrawable.java','TintDrawable.kt'}
    for item in projects:
        project=item['project']
        if 'sections' in item:tree=json.loads(gzip.decompress((INPUT/'source-trees/frameworks__base.json.gz').read_bytes()))['entries']
        else:tree=json.loads(gzip.decompress((INPUT/item['treeCache']).read_bytes()))['tree']
        for node in tree:
            if node['type']!='blob':continue
            path=node['path'];parts=path.split('/')
            def needed_values(part):
                if part=='values' or part in ['values-en','values-en-rUS','values-en-rGB']:return True
                tokens=part.split('-')
                if tokens[0]!='values' or 'watch' not in tokens:return False
                return not any((re.fullmatch('[a-z]{2}',token) and token!='en') or token.startswith('b+') for token in tokens[1:])
            default_values=any(needed_values(p) for p in parts) and path.endswith('.xml')
            owner=(project['path']=='bootable/recovery' and path in ['minui/resources.cpp','recovery_ui/screen_ui.cpp','recovery_ui/include/recovery_ui/screen_ui.h']) or (project['path']=='frameworks/base' and path in ['cmds/bootanimation/BootAnimation.cpp','cmds/bootanimation/BootAnimation.h']) or Path(path).name in owner_names
            license_file=len(parts)<=2 and re.fullmatch(r'(?:LICENSE|NOTICE|COPYING|COPYRIGHT)(?:[._-].*)?',parts[-1],re.I) is not None
            if (default_values or owner or license_file) and (project['path'],path) not in original:jobs[(project['path'],path)]=(project,path,node['sha'],'values-auxiliary' if default_values else ('owner-source' if owner else 'upstream-license'))
    framework=next(x['project'] for x in projects if x['project']['path']=='frameworks/base');rev=framework['revision'];cache=OUT/'source/widget-directory.json.gz';cache.parent.mkdir(parents=True,exist_ok=True)
    url=f"https://api.github.com/repos/{framework['name']}/contents/core/java/android/widget?ref={rev}"
    raw=gzip.decompress(cache.read_bytes()) if cache.exists() else get(url);listing=json.loads(raw);assert isinstance(listing,list) and len(listing)<1000;cache.write_bytes(gzip.compress(raw,mtime=0))
    wanted={'Button.java','CompoundButton.java','CheckBox.java','RadioButton.java','Switch.java','ProgressBar.java','SeekBar.java','EditText.java','TextView.java','ImageView.java'}
    found=set()
    for node in listing:
        if node.get('name') in wanted:jobs[(framework['path'],node['path'])]=(framework,node['path'],node['sha'],'owner-source');found.add(node['name'])
    assert found==wanted,wanted-found
    def fetch(job):
        project,path,sha,kind=job;target=OUT/'source/objects'/sha[:2]/sha[2:]
        if project.get('remote')=='aosp':url=f"https://android.googlesource.com/{project['name']}/+/{project['revision']}/{urllib.parse.quote(path,safe='/')}?format=TEXT"
        else:url=f"https://raw.githubusercontent.com/{project['name']}/{project['revision']}/{urllib.parse.quote(path,safe='/')}"
        data=target.read_bytes() if target.exists() else (base64.b64decode(get(url)) if project.get('remote')=='aosp' else get(url))
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==sha
        if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        return {'project':project['path'],'repository':project['name'],'revision':project['revision'],'path':path,'kind':kind,'sourceSet':'auxiliary-owner-or-value-data','gitBlobSha1':sha,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'object':target.relative_to(OUT).as_posix(),'url':url}
    results=[];errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        pending={pool.submit(fetch,job):key for key,job in jobs.items()}
        for future in concurrent.futures.as_completed(pending):
            try:results.append(future.result())
            except Exception as e:errors.append({'source':pending[future],'error':str(e)})
    results.sort(key=lambda x:(x['project'],x['path']));write_json(OUT/'auxiliary-source-files.json',results);write_json(OUT/'auxiliary-fetch-errors.json',errors)
    print(json.dumps({'auxiliaryFiles':len(results),'errors':errors,'scope':'Supporting resource values and exact native owner source; original16559-file artwork corpus count unchanged'}))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
