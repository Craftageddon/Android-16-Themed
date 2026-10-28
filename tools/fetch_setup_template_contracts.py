'''Preserve actual pinned setup template APIs and theme resources without executing them.'''
from pathlib import Path
import base64,hashlib,json,re,time
from audit_os_resource_coverage import ROOT,read_json,write_json
from resolve_gallery_native_dependencies import get
OUT=ROOT/'iterations/28-setup-workflows'
def object_sha(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def main():
 rows=[]
 for r in read_json(OUT/'source/setupcompat-inputs.json'):
  rel=r['path'];url='https://raw.githubusercontent.com/LineageOS/android_external_setupcompat/15f79d6014e9cc3c70819d81ccb70687ed2dab28/'+rel;dest=OUT/'source/setupcompat'/rel
  data=dest.read_bytes() if dest.exists() else get(url);assert object_sha(data)==r['gitBlobSha1'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rows.append({'project':'external/setupcompat','revision':'15f79d6014e9cc3c70819d81ccb70687ed2dab28','path':rel,'url':url,'gitBlobSha1':r['gitBlobSha1'],'sha256':hashlib.sha256(data).hexdigest(),'saved':dest.relative_to(OUT).as_posix(),'executed':False})
 pin='79dbf5860322236cd02e74e2ca0855591d95195c';base='https://android.googlesource.com/platform/external/setupdesign/+/'+pin+'/'
 listing_cache={}
 def listing(path):
  if path not in listing_cache:listing_cache[path]=json.loads(get(base+path+'?format=JSON')[4:])['entries']
  return listing_cache[path]
 def acquire(rel):
  parent,name=rel.rsplit('/',1) if '/' in rel else ('',rel);nodes=listing(parent+'/' if parent else '');node=next(n for n in nodes if n['name']==name and n['type']=='blob');dest=OUT/'source/setupdesign'/rel;data=dest.read_bytes() if dest.exists() else base64.b64decode(get(base+rel+'?format=TEXT'));assert object_sha(data)==node['id'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);rows.append({'project':'external/setupdesign','revision':pin,'path':rel,'url':base+rel+'?format=TEXT','gitBlobSha1':node['id'],'sha256':hashlib.sha256(data).hexdigest(),'saved':dest.relative_to(OUT).as_posix(),'executed':False})
 acquire('Android.bp');main_entries=listing('main/');names={n['name'] for n in main_entries};src='main/src' if 'src' in names else 'main/java' if 'java' in names else None;assert src,names
 prefix=src+'/com/google/android/setupdesign/'
 for rel in ['GlifLayout.java','GlifRecyclerLayout.java','template/IconMixin.java','template/HeaderMixin.java','items/SwitchItem.java','items/RecyclerItemAdapter.java','items/ItemInflater.java']:acquire(prefix+rel)
 resource_folders=[]
 for path in ['main/res/','main/res-default/']:
  try:nodes=listing(path)
  except Exception as e:
   if '404' in str(e):continue
   raise
  for node in nodes:
   if node['type']=='tree' and node['name'].startswith('values') and not re.fullmatch(r'values-[a-z]{2,3}(?:-r[A-Z]{2})?',node['name']):resource_folders.append(path+node['name']+'/')
 for folder in resource_folders:
  for n in listing(folder):
   if n['type']=='blob' and n['name'].endswith('.xml') and any(k in n['name'] for k in ['style','theme','attr','dimen','color']):acquire(folder+n['name'])
 write_json(OUT/'source/setup-template-contracts.json',{'files':rows,'nativePrivateAppCompilation':'NOT RUN','sourceCodeExecuted':False,'wholeGoalComplete':False});print({'pinnedTemplateSourcesAndResources':len(rows),'productionCodeExecuted':False})
if __name__=='__main__':main()
