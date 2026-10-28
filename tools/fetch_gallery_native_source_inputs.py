'''Fetch and verify exact native Java/Kotlin source subtrees without executing repository scripts.'''
from pathlib import Path,PurePosixPath
import base64,hashlib,io,json,tarfile,xml.etree.ElementTree as E,urllib.parse,urllib.error
from audit_os_resource_coverage import ROOT,write_json
from resolve_gallery_native_dependencies import get
OUT=ROOT/'iterations/27-gallery-contracts';CACHE=ROOT/'build-work/gallery27-native-dependencies'
TARGETS={'external/guava':['android/guava/src','futures/failureaccess','android-annotation-stubs/src'],'external/jsr305':['ri/src/main/java'],'external/jspecify':['src/main'],'external/error_prone':['annotations/src/main/java'],'external/kotlinx.atomicfu':['atomicfu/src/commonMain','atomicfu/src/jvmMain'],'external/kotlinx.coroutines':['kotlinx-coroutines-core/common/src','kotlinx-coroutines-core/concurrent/src','kotlinx-coroutines-core/jvm/src','kotlinx-coroutines-core/jdk8/src','android-annotation-stubs/src','ui/kotlinx-coroutines-android/src'],'external/kotlinx.serialization':['core/commonMain/src','core/jvmMain/src']}
def object_hash(kind,data):return hashlib.sha1(kind.encode()+b' '+str(len(data)).encode()+b'\0'+data).hexdigest()
def tree_hash(files):
 root={}
 for name,row in files.items():
  node=root;parts=PurePosixPath(name).parts
  for part in parts[:-1]:node=node.setdefault(part,{})
  node[parts[-1]]=row
 def walk(node):
  entries=[]
  for name,value in node.items():
   if isinstance(value,tuple):mode,data=value;sha=object_hash('blob',data);sort=name
   else:mode='40000';sha=walk(value);sort=name+'/'
   entries.append((sort,mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(sha)))
  return object_hash('tree',b''.join(e[1] for e in sorted(entries)))
 return walk(root)
def main():
 projects={p.get('path'):p for p in E.parse(ROOT/'integration/research/2026-10-23/official-20261019-build-manifest.xml').getroot().iter('project')};records=[]
 for project,subdirs in TARGETS.items():
  p=projects[project];prefix='https://android.googlesource.com/'+p.get('name')
  for subtree in subdirs:
   identity=project+'@'+p.get('revision')+'/'+subtree;cache=CACHE/'archives'/(hashlib.sha1(identity.encode()).hexdigest()+'.tgz');cache.parent.mkdir(parents=True,exist_ok=True)
   meta_url=prefix+'/+/'+p.get('revision')+'/'+subtree+'/?format=JSON'
   try:meta=json.loads(get(meta_url)[4:])
   except urllib.error.HTTPError as e:
    if e.code!=404:raise
    records.append({'project':project,'revision':p.get('revision'),'subtree':subtree,'sourceGlobHasNoDirectory':True,'sourceUrl':meta_url});print('No directory for declared glob '+identity,flush=True);continue
   url=prefix+'/+archive/'+p.get('revision')+'/'+subtree+'.tar.gz';data=cache.read_bytes() if cache.exists() else get(url);files={}
   with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
    for member in archive.getmembers():
     name=PurePosixPath(member.name).as_posix();pp=PurePosixPath(name);assert not pp.is_absolute() and '..' not in pp.parts and ':' not in name
     if member.isdir():continue
     if member.isfile():payload=archive.extractfile(member).read();mode='100755' if member.mode&0o111 else '100644'
     elif member.issym():payload=member.linkname.encode();mode='120000'
     else:raise AssertionError((identity,name,member.type))
     files[name]=(mode,payload)
   actual=tree_hash(files);assert actual==meta['id'],(identity,actual,meta['id']);cache.write_bytes(data);source_files=[]
   for name,(mode,payload) in files.items():
    if not name.endswith(('.java','.kt')):continue
    assert mode!='120000',('Source symlink requires explicit target handling',identity,name)
    git=object_hash('blob',payload);dest=CACHE/'source-blobs'/git[:20]/PurePosixPath(name).name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(payload)
    source_files.append({'path':subtree+'/'+name,'gitBlobSha1':git,'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload),'localBuildCache':str(dest)})
   records.append({'project':project,'repository':p.get('name'),'revision':p.get('revision'),'subtree':subtree,'sourceUrl':url,'archiveSha256':hashlib.sha256(data).hexdigest(),'sourceTreeGitSha1':actual,'gitTreeVerified':True,'sourceFiles':source_files,'repoScriptsExecuted':False})
   write_json(OUT/'source/native-source-inputs.json',records);print('Verified '+identity+' / '+str(len(source_files))+' source files',flush=True)
 print({'sourceSubtrees':len(records),'sourceFiles':sum(len(r.get('sourceFiles',[])) for r in records),'repositoryScriptsExecuted':False})
if __name__=='__main__':main()
