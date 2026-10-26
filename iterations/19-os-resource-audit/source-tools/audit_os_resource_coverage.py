"""Inventory pinned public LineageOS visual sources; never infer install presence."""
from pathlib import Path
import concurrent.futures,csv,gzip,hashlib,json,re,time,urllib.request,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'iterations/19-os-resource-audit'
PROJECT_PATHS=['frameworks/base','packages/apps/Settings','packages/apps/DocumentsUI','packages/apps/Glimpse','packages/apps/Launcher3','packages/apps/LineageParts','packages/apps/SetupWizard','packages/apps/Updater','packages/inputmethods/LatinIME','packages/modules/Permission','device/ayn/odin2thor','device/ayn/qcs8550-common','hardware/ayn','bootable/recovery','vendor/lineage']
PROJECT_PATHS += ['packages/apps/'+p for p in ['AudioFX','Backgrounds','Camelot','Canvas','Etar','ExactCalculator','Jelly','Profiles','Recorder','Seedvault','ThemePicker','Twelve','AvatarPicker','QuickAccessWallet']]
PROJECT_PATHS += ['build/make','packages/apps/WallpaperPicker2']
UA={'User-Agent':'Craftageddon-pinned-resource-audit','Accept':'application/vnd.github+json'}

def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=55) as f:return f.read()
        except Exception:
            if attempt==2:raise
            time.sleep(attempt+1)

def write_json(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);data=(json.dumps(v,indent=2)+'\n').encode('utf8');p.write_bytes(data)
    if len(data)>80000:p.with_suffix(p.suffix+'.gz').write_bytes(gzip.compress(data,mtime=0))

def read_json(p):
    data=p.read_bytes() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes())
    return json.loads(data)

def inventory_project(project):
    name=project['name'];rev=project['revision'];slug=project['path'].replace('/','__');cache=OUT/'source-trees'/f'{slug}.json.gz'
    url=f'https://api.github.com/repos/{name}/git/trees/{rev}?recursive=1'
    if project.get('remote')=='aosp':
        if cache.exists():obj=json.loads(gzip.decompress(cache.read_bytes()))
        else:
            entries=[];todo=[''];proof=[]
            while todo:
                path=todo.pop();source_url=f'https://android.googlesource.com/{name}/+/{rev}/{path}?format=JSON';raw=get(source_url);listing=json.loads(raw[raw.index(b'\n')+1:]);proof.append({'path':path,'url':source_url,'sha256':hashlib.sha256(raw).hexdigest()})
                for node in listing['entries']:
                    p=path+node['name'];item={'path':p,'type':node['type'],'sha':node['id']};entries.append(item)
                    if node['type']=='tree':todo.append(p+'/')
            obj={'sha':rev,'tree':entries,'truncated':False,'gitilesDirectoryProof':proof};cache.parent.mkdir(parents=True,exist_ok=True);cache.write_bytes(gzip.compress(json.dumps(obj).encode(),mtime=0))
        print(json.dumps({'project':project['path'],'entries':len(obj['tree']),'complete':True}),flush=True)
        return {'project':project,'url':f'https://android.googlesource.com/{name}/+/{rev}/','treeSha':rev,'entries':obj['tree'],'treeJsonSha256':hashlib.sha256(gzip.decompress(cache.read_bytes())).hexdigest(),'treeCache':cache.relative_to(OUT).as_posix(),'transport':'Gitiles complete directory traversal'}
    if project['path']=='frameworks/base':
        if cache.exists():return json.loads(gzip.decompress(cache.read_bytes()))
        sections=['core/res','packages/SystemUI','packages/SettingsLib','libs/WindowManager/Shell','cmds/bootanimation']
        combined=[];proof=[];walk_cache={}
        for section in sections:
            sha=rev
            for part in section.split('/'):
                if sha not in walk_cache:walk_cache[sha]=json.loads(get(f'https://api.github.com/repos/{name}/git/trees/{sha}'))
                sha=next(x['sha'] for x in walk_cache[sha]['tree'] if x['path']==part and x['type']=='tree')
            section_cache=OUT/'source-trees'/('framework__'+section.replace('/','__')+'.json.gz')
            section_url=f'https://api.github.com/repos/{name}/git/trees/{sha}?recursive=1'
            if section_cache.exists():raw=gzip.decompress(section_cache.read_bytes())
            else:
                raw=get(section_url);section_cache.parent.mkdir(parents=True,exist_ok=True);section_cache.write_bytes(gzip.compress(raw,mtime=0))
            tree=json.loads(raw);assert not tree.get('truncated'),section+' tree truncated'
            combined.extend({**x,'path':section+'/'+x['path']} for x in tree['tree'])
            proof.append({'section':section,'treeSha':sha,'url':section_url,'jsonSha256':hashlib.sha256(raw).hexdigest(),'cache':section_cache.relative_to(OUT).as_posix(),'entries':len(tree['tree']),'truncated':False})
        result={'project':project,'url':url,'treeSha':rev,'entries':combined,'sections':proof,'scope':'Only explicitly listed complete framework sections; not the entire framework repository'}
        cache.write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0))
        print(json.dumps({'project':project['path'],'entries':len(combined),'completeSections':len(proof)}),flush=True)
        return result
    if cache.exists():data=gzip.decompress(cache.read_bytes())
    else:
        data=get(url);obj=json.loads(data);assert not obj.get('truncated'),name+' tree truncated';assert 'tree' in obj
        cache.parent.mkdir(parents=True,exist_ok=True);cache.write_bytes(gzip.compress(data,mtime=0))
    obj=json.loads(data);assert not obj.get('truncated') and 'tree' in obj
    print(json.dumps({'project':project['path'],'entries':len(obj['tree']),'complete':True}),flush=True)
    return {'project':project,'url':url,'treeSha':obj['sha'],'entries':obj['tree'],'treeJsonSha256':hashlib.sha256(data).hexdigest(),'treeCache':cache.relative_to(OUT).as_posix()}

def main():
    assert not (OUT/'complete-assets.zip').exists(),'Never rewrite a packaged checkpoint'
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=ROOT/'integration/research/2026-10-23/official-20261019-build-manifest.xml'
    assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='4bf203ee7ab8b663d0bf6c83d3e35bd349222d3ca228940df191e2aff50d2364'
    projects={n.get('path'):n.attrib for n in ET.parse(manifest).getroot().findall('project')}
    results=[];errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs={pool.submit(inventory_project,projects[p]):p for p in PROJECT_PATHS}
        for job in concurrent.futures.as_completed(jobs):
            try:results.append(job.result())
            except Exception as e:errors.append({'project':jobs[job],'error':str(e)});print(json.dumps(errors[-1]),flush=True)
    results.sort(key=lambda x:x['project']['path'])
    write_json(OUT/'source-projects.json',[{k:v for k,v in x.items() if k!='entries'} for x in results])
    write_json(OUT/'source-fetch-errors.json',errors)
    records=[]
    for result in results:
        project=result['project'];prefix=project['path'];repo=project['name'];rev=project['revision']
        for item in result['entries']:
            if item['type']!='blob':continue
            path=item['path'];parts=path.split('/');resource_dir=next((p for p in parts if re.fullmatch(r'(?:drawable|mipmap|layout|anim|animator|transition|color)(?:-[A-Za-z0-9_+]+)*',p)),None)
            visual=resource_dir is not None and any(p in ['res','res-product','res-keyguard','res_ext','resources'] or p.startswith('res-') for p in parts)
            raw_visual=('/raw/' in '/'+path and Path(path).suffix.lower() in ['.json','.zip','.png','.webp','.gif','.mp4','.svg','.lottie'])
            recovery=prefix=='bootable/recovery' and path.startswith('res-') and Path(path).suffix in ['.png','.xml','.bmp']
            boot=prefix=='vendor/lineage' and ('bootanimation' in path.lower()) and Path(path).suffix.lower() in ['.png','.zip','.svg','.txt','.mk','.bp']
            values=('/values/' in '/'+path and Path(path).suffix=='.xml' and Path(path).stem not in ['strings','plurals','arrays'])
            if not (visual or raw_visual or recovery or boot or values):continue
            kind=resource_dir.split('-')[0] if resource_dir else ('values-visual' if values else 'raw-visual' if raw_visual else 'recovery-bitmap' if recovery else 'boot-source')
            stem=Path(path).name
            for suffix in ['.9.png','.xml','.png','.webp','.jpg','.jpeg','.gif','.json','.zip','.svg','.txt','.mk','.bp']:
                if stem.endswith(suffix):stem=stem[:-len(suffix)];break
            owner='SystemUI' if prefix=='frameworks/base' and path.startswith('packages/SystemUI/') else 'Framework' if prefix=='frameworks/base' and path.startswith('core/res/') else 'SettingsLib' if prefix=='frameworks/base' and path.startswith('packages/SettingsLib/') else prefix
            source_set='test-or-sample' if any(p.lower() in ['test','tests','testdata','testutils','samples','sample','screenshot','screenshots','testapps','demo','demos','androidtest','javatests','benchmark','benchmarks','robolectric'] for p in parts) else 'production-candidate'
            records.append({'owner':owner,'project':prefix,'repository':repo,'revision':rev,'path':path,'kind':kind,'qualifier':resource_dir or kind,'resourceName':stem,'sourceSet':source_set,'gitBlobSha1':item['sha'],'bytes':item.get('size',0),'url':f'https://github.com/{repo}/blob/{rev}/{path}','sourcePresence':'Pinned source present; installed/reachable resource NOT established'})
    write_json(OUT/'resource-files.json',records)
    print(json.dumps({'projects':len(results),'errors':len(errors),'visualSourceFiles':len(records)}),flush=True)

if __name__=='__main__':main()
