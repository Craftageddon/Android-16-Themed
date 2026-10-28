'''Link real Gallery and native dependency resources against exact pinned SDK36.'''
from pathlib import Path,PurePosixPath
import datetime,hashlib,json,re,shutil,subprocess,zipfile,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json,get
from resolve_gallery_native_dependencies import modules
OUT=ROOT/'iterations/27-gallery-contracts';UP=OUT/'upstream/packages/apps/Glimpse';PATCH=OUT/'native-patch/packages/apps/Glimpse';CACHE=ROOT/'build-work/gallery27-native-dependencies';SDK=Path('C:/Users/spencerm/AppData/Local/Android/Sdk')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (OUT/'complete-assets.zip').exists()
 closure=read_json(OUT/'source/native-dependency-closure.json');platform={r['module']:r for r in closure['platformLibraries']};local=modules((UP/'app/libs/Android.bp').read_text(encoding='utf8'));app=modules((UP/'app/Android.bp').read_text(encoding='utf8'))['Glimpse']
 prior=read_json(ROOT/'iterations/21-native-workflows/source/build-dependencies/pinned-aar-receipts.json');bp=prior['bpSources'][0];assert sha(Path(bp['localBuildCache']))==bp['sha256'];material_modules=modules(Path(bp['localBuildCache']).read_text(encoding='utf8'))
 material=next(r for r in prior['libraries'] if '/material/' in r['path']);assert sha(Path(material['localBuildCache']))==material['sha256']
 platform['com.google.android.material_material-nodeps']=dict(material,module='com.google.android.material_material-nodeps',declaredDependencies=material_modules['com.google.android.material_material-nodeps']['static_libs'])
 graph={name:dict(row,dependencies=row['static_libs'],artifact=(UP/'app/libs'/row['aars'][0] if row['aars'] else UP/'app/libs'/row['jars'][0]) if row['aars'] or row['jars'] else None) for name,row in local.items()}
 for name,row in platform.items():graph[name]={'dependencies':row['declaredDependencies'],'artifact':Path(row['localBuildCache']),'metadata':row}
 wrapper=material_modules['com.google.android.material_material'];graph[wrapper['name']]={'dependencies':wrapper['static_libs'],'artifact':None}
 ordered=[];seen=set();visiting=set()
 def visit(name):
  if name in seen:return
  assert name not in visiting,name;visiting.add(name)
  for dep in graph.get(name,{}).get('dependencies',[]):visit(dep)
  visiting.remove(name);seen.add(name)
  if graph.get(name,{}).get('artifact') and graph[name]['artifact'].suffix=='.aar':ordered.append(name)
 for name in app['static_libs']:visit(name)
 # Source: pinned Soong aar.go reverses its topological res nodes before overlays;
 # Blueprint depset postorder + two reversals yields dependency-first stable order.
 work=ROOT/'build-work'/('gallery27-resources-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True);logs=[];rows=[];flats=[]
 aapt=SDK/'build-tools/37.0.0/aapt2.exe';android=Path(closure['sdk36']['localBuildCache']);assert sha(android)==closure['sdk36']['sha256']
 def run(args,save=None):
  p=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf8',errors='replace');logs.append(p.stdout+p.stderr)
  if save:save.write_text(p.stdout+p.stderr,encoding='utf8')
  if p.returncode:raise RuntimeError('Exit '+str(p.returncode)+'\n'+(p.stdout+p.stderr)[-10000:])
  return p.stdout
 for i,name in enumerate(ordered):
  artifact=graph[name]['artifact'];folder=work/f'lib{i:02}';folder.mkdir();res=folder/'res';pkg=None;symbols=None
  with zipfile.ZipFile(artifact) as z:
   pkg=E.fromstring(z.read('AndroidManifest.xml')).get('package');symbols=z.read('R.txt').decode('utf8') if 'R.txt' in z.namelist() else ''
   for member in z.namelist():
    pp=PurePosixPath(member);assert not pp.is_absolute() and '..' not in pp.parts
    if member.startswith('res/') and not member.endswith('/'):
     target=folder/member;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(member))
   classes=folder/'classes.jar';classes.write_bytes(z.read('classes.jar'))
  if res.exists():
   flat=folder/'resources.zip';run([aapt,'compile','--dir',res,'-o',flat]);flats.append(flat)
  rows.append({'module':name,'aar':str(artifact),'aarSha256':sha(artifact),'namespace':pkg,'classesJar':str(classes),'classesSha256':sha(classes),'resources':str(res),'resourceSymbols':symbols,'overlayOrder':i})
 appdir=work/'app-res';shutil.copytree(UP/'app/src/main/res',appdir)
 for p in (PATCH/'app/src/main/res').rglob('*'):
  if p.is_file():target=appdir/p.relative_to(PATCH/'app/src/main/res');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 flat=work/'app-resources.zip';run([aapt,'compile','--dir',appdir,'-o',flat]);flats.append(flat);(work/'gen').mkdir()
 args=['link','-I',str(android),'--manifest',str(UP/'app/src/main/AndroidManifest.xml'),'--min-sdk-version','30','--target-sdk-version','36','--auto-add-overlay','--java',str(work/'gen'),'--output-text-symbols',str(work/'R.txt'),'-o',str(work/'linked-resources.ap_')]
 for f in flats:args+=['-R',str(f)]
 argfile=work/'aapt2-link.args';argfile.write_text('\n'.join('"'+x.replace('\\','/')+'"' for x in args),encoding='utf8')
 try:
  assert sum(len(str(x))+3 for x in [aapt,*args])<30000
  run([aapt,*args])
 except Exception:
  evidence=OUT/'verification/evidence';evidence.mkdir(parents=True,exist_ok=True);(evidence/'full-resource-link-log.txt').write_text('\n'.join(logs),encoding='utf8');write_json(evidence/'full-resource-link.json',{'result':'FAIL','work':str(work),'wholeGoalComplete':False});raise
 run([aapt,'dump','resources',work/'linked-resources.ap_'],work/'resource-table.txt')
 evidence=OUT/'verification/evidence';evidence.mkdir(parents=True,exist_ok=True);(evidence/'full-resource-link-log.txt').write_text('\n'.join(logs[:-1]),encoding='utf8')
 write_json(evidence/'full-resource-link.json',{'result':'PASS','work':str(work),'sdk36Sha256':sha(android),'appResourceConfigs':sum(p.is_file() for p in appdir.rglob('*')),'libraryAarsLinked':len(rows),'libraries':[dict(r,resourceSymbolsSha256=hashlib.sha256(r['resourceSymbols'].encode()).hexdigest(),resourceSymbols=None) for r in rows],'linkedResourcePackageSha256':sha(work/'linked-resources.ap_'),'realResourceSymbols':str(work/'R.txt'),'nativeSoongBuild':'NOT RUN','nativeInflation':'NOT RUN','wholeGoalComplete':False})
 write_json(work/'library-resource-inputs.json',rows);write_json(work/'dependency-graph.json',{'app':app,'graph':{n:{'dependencies':r['dependencies'],'artifact':str(r['artifact']) if r.get('artifact') else None} for n,r in graph.items()},'resourceOverlayOrderLowToHigh':ordered})
 print({'realDependencyAarsLinked':len(rows),'actualAppResourcesLinked':True,'sdk36Pinned':True,'work':str(work)})
if __name__=='__main__':main()
