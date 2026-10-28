'''Acquire pinned compiler binaries and missing native source declarations; no execution.'''
from pathlib import Path
import base64,hashlib,json,xml.etree.ElementTree as E,urllib.parse
from audit_os_resource_coverage import ROOT,read_json,write_json
from resolve_gallery_native_dependencies import get,modules
OUT=ROOT/'iterations/27-gallery-contracts';CACHE=ROOT/'build-work/gallery27-native-dependencies'
def listing(base,path):return json.loads(get(base+path+'?format=JSON')[4:])['entries']
def acquire(base,path,node):
 f=CACHE/'files'/(node['id']+Path(path).suffix);f.parent.mkdir(parents=True,exist_ok=True);data=f.read_bytes() if f.exists() else base64.b64decode(get(base+path+'?format=TEXT'));git=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert git==node['id'];f.write_bytes(data);return {'path':path,'url':base+path+'?format=TEXT','gitBlobSha1':git,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'localBuildCache':str(f),'executed':False}
def main():
 projects={p.get('path'):p for p in E.parse(ROOT/'integration/research/2026-10-23/official-20261019-build-manifest.xml').getroot().iter('project')}
 compiler=projects['external/kotlinc'];base='https://android.googlesource.com/'+compiler.get('name')+'/+/'+compiler.get('revision')+'/'
 names=['annotations-13.0.jar','kotlin-compiler.jar','kotlin-reflect.jar','kotlin-script-runtime.jar','kotlin-stdlib.jar','kotlinx-coroutines-core-jvm.jar','trove4j.jar'];nodes=listing(base,'lib/');rows=[]
 for name in names:
  r=acquire(base,'lib/'+name,next(n for n in nodes if n['name']==name));rows.append(r);write_json(OUT/'source/pinned-compiler.json',{'project':'external/kotlinc','revision':compiler.get('revision'),'files':rows,'executed':False});print('Verified compiler input '+name+' / '+str(r['bytes'])+' bytes',flush=True)
 declarations=[]
 for path in ['external/jsr305','external/kotlinx.atomicfu','external/kotlinx.serialization']:
  project=projects[path];base='https://android.googlesource.com/'+project.get('name')+'/+/'+project.get('revision')+'/';nodes=listing(base,'');row=acquire(base,'Android.bp',next(n for n in nodes if n['name']=='Android.bp'));row.update(project=path,revision=project.get('revision'),modules=modules(Path(row['localBuildCache']).read_text(encoding='utf8')));declarations.append(row)
 write_json(OUT/'source/additional-native-declarations.json',declarations);print({'pinnedCompilerFiles':len(rows),'additionalDeclarations':len(declarations)})
if __name__=='__main__':main()
