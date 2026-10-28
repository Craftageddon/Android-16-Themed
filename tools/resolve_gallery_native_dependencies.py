'''Resolve actual pinned native Gallery dependency declarations, without executing builds.'''
from pathlib import Path
import base64,hashlib,json,re,urllib.parse,xml.etree.ElementTree as E,zipfile,time,urllib.error
from audit_os_resource_coverage import ROOT,read_json,write_json,get as raw_get
OUT=ROOT/'iterations/27-gallery-contracts';CACHE=ROOT/'build-work/gallery27-native-dependencies';CACHE.mkdir(parents=True,exist_ok=True)
PIN='0f07e8d60ab0aba46129e427101f96ba459a95c1';BASE='https://android.googlesource.com/platform/prebuilts/sdk/+/'+PIN+'/'
LAST_GET=0.;BY_SHA={}
for record in read_json(ROOT/'iterations/26-gallery-workflows/source/platform-dependencies.json')['libraries']:
 for row in [record,record.get('buildDeclaration',{})]:
  if row.get('gitBlobSha1') and row.get('localBuildCache'):BY_SHA[row['gitBlobSha1']]=Path(row['localBuildCache'])
def get(url):
 global LAST_GET
 for attempt in range(4):
  time.sleep(max(0,.8-(time.monotonic()-LAST_GET)));LAST_GET=time.monotonic()
  try:return raw_get(url)
  except urllib.error.HTTPError as e:
   if e.code not in [429,502,503] or attempt==3:raise
   delay=min(30,float(e.headers.get('Retry-After',3*(attempt+1))))
   print('Source host requested retry; preserving pinned cache, delay='+str(delay),flush=True);time.sleep(delay)

def modules(text):
 result={}
 for kind,body in re.findall(r'(\w+)\s*\{(.*?)^\}',text,re.M|re.S):
  n=re.search(r'\bname:\s*"([^"]+)"',body)
  if not n:continue
  row={'name':n[1],'kind':kind}
  for field in ['static_libs','libs','aars','jars','srcs','exclude_srcs']:
   m=re.search(r'\b'+field+r':\s*\[(.*?)\]',body,re.S);row[field]=re.findall(r'"([^"]+)"',m[1]) if m else []
  result[n[1]]=row
 return result

def listing(path):
 legacy=CACHE/'trees'/Path(path.replace('/','__')+'.json');f=CACHE/'trees'/(hashlib.sha1(path.encode()).hexdigest()+'.json');f.parent.mkdir(parents=True,exist_ok=True)
 if f.exists():return json.loads(f.read_bytes())
 if legacy.exists():data=json.loads(legacy.read_bytes());f.write_bytes(json.dumps(data).encode());return data
 data=json.loads(get(BASE+path+'/?format=JSON')[4:]);f.write_bytes(json.dumps(data).encode());return data

def blob(path,node):
 legacy=CACHE/'files'/path;f=CACHE/'files'/(node['id']+Path(path).suffix);f.parent.mkdir(parents=True,exist_ok=True)
 data=f.read_bytes() if f.exists() else legacy.read_bytes() if legacy.exists() else BY_SHA[node['id']].read_bytes() if node['id'] in BY_SHA else base64.b64decode(get(BASE+urllib.parse.quote(path,safe='/')+'?format=TEXT'))
 git=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert git==node['id'],path;f.write_bytes(data)
 r={'path':path,'url':BASE+path+'?format=TEXT','gitBlobSha1':git,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'localBuildCache':str(f)}
 if path.endswith('.aar'):
  with zipfile.ZipFile(f) as z:
   jar=z.read('classes.jar');r['package']=E.fromstring(z.read('AndroidManifest.xml')).get('package')
  jf=f.with_suffix('.classes.jar');jf.write_bytes(jar);r.update(classesJar=str(jf),classesSha256=hashlib.sha256(jar).hexdigest())
 elif path.endswith('.jar'):r.update(classesJar=str(f),classesSha256=r['sha256'])
 return r

def artifact(module):
 m=re.fullmatch(r'androidx[.-]([^_]+)_(.+)',module);assert m,module;group,name=m.groups();base='current/androidx/m2repository/androidx/'+group.replace('.','/')
 children=listing(base)['entries'];names={n['name'] for n in children};candidates=[n for n in [name,name+'-android',name+'-jvm'] if n in names]
 assert candidates,(module,sorted(names))
 for candidate in candidates:
  versions=listing(base+'/'+candidate)['entries'];assert len(versions)==1,(module,versions);path=base+'/'+candidate+'/'+versions[0]['name'];nodes=listing(path)['entries'];bn=next(n for n in nodes if n['name']=='Android.bp');br=blob(path+'/Android.bp',bn);parsed=modules(Path(br['localBuildCache']).read_text(encoding='utf8'))
  if module not in parsed:continue
  declaration=parsed[module];files=declaration['aars']+declaration['jars'];assert len(files)==1,(module,declaration)
  node=next(n for n in nodes if n['name']==files[0]);r=blob(path+'/'+node['name'],node);r.update(module=module,buildDeclaration=br,declaredDependencies=declaration['static_libs'],declaredCompileLibraries=declaration['libs']);return r
 raise AssertionError(('No exact Soong provider',module,candidates))

def main():
 assert not (OUT/'complete-assets.zip').exists();up=OUT/'upstream/packages/apps/Glimpse';local=modules((up/'app/libs/Android.bp').read_text(encoding='utf8'));app=modules((up/'app/Android.bp').read_text(encoding='utf8'))['Glimpse'];pending=list(app['static_libs']);records={};unknown=set();local_reached=[]
 while pending:
  name=pending.pop(0)
  if name in records or name in unknown or name in local_reached:continue
  if name in local:
   local_reached.append(name);pending+=local[name]['static_libs'];continue
  if name.startswith(('androidx.','androidx-')):
   try:r=artifact(name)
   except Exception as e:
    write_json(OUT/'source/native-dependency-resolution-progress.json',{'resolved':list(records.values()),'pending':[name,*pending],'error':type(e).__name__+': '+str(e),'wholeGoalComplete':False});raise
   records[name]=r;pending+=r['declaredDependencies'];print('Resolved '+name,flush=True)
  else:unknown.add(name)
 sdk_nodes=listing('36/public')['entries'];sdk=blob('36/public/android.jar',next(n for n in sdk_nodes if n['name']=='android.jar'))
 with zipfile.ZipFile(sdk['localBuildCache']) as z:sdk['containsFrameworkResourceTable']='resources.arsc' in z.namelist()
 manifest=E.parse(ROOT/'integration/research/2026-10-23/official-20261019-build-manifest.xml').getroot();projects={p.get('path'):p for p in manifest.iter('project')};external=[]
 for path in ['external/kotlinc','external/kotlinx.coroutines','external/guava','external/jspecify','external/error_prone']:
  p=projects[path];url='https://android.googlesource.com/'+p.get('name')+'/+/'+p.get('revision')+'/Android.bp?format=TEXT';data=base64.b64decode(get(url));f=CACHE/'external'/(path.replace('/','__')+'__Android.bp');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
  external.append({'project':path,'revision':p.get('revision'),'url':url,'sha256':hashlib.sha256(data).hexdigest(),'localBuildCache':str(f),'modules':modules(data.decode())})
 write_json(OUT/'source/native-dependency-closure.json',{'sdkRepository':'platform/prebuilts/sdk','sdkRevision':PIN,'platformLibraries':list(records.values()),'appCommittedModulesReached':local_reached,'additionalNativeModuleContracts':sorted(unknown),'sdk36':sdk,'externalDeclarations':external,'purpose':'Exact source/API dependency inventory; full Soong build not executed','wholeGoalComplete':False})
 print({'platformLibraries':len(records),'localModules':len(local_reached),'additionalModules':sorted(unknown),'sdk36ResourceTable':sdk['containsFrameworkResourceTable']})
if __name__=='__main__':main()
