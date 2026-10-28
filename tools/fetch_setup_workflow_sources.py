'''Acquire exact SetupWizard production source, all nonlocalized visual inputs and build contracts.'''
from pathlib import Path
import concurrent.futures,hashlib,json,re,urllib.parse
from audit_os_resource_coverage import ROOT,read_json,write_json,get
OUT=ROOT/'iterations/28-setup-workflows';AUDIT=ROOT/'iterations/19-os-resource-audit';BASE=ROOT/'iterations/20-semantic-review';PIN='69174527a30bc72a28a5d55acdec8ce5edaba9e0'
def main():
 assert not (OUT/'complete-assets.zip').exists()
 project=next(x['project'] for x in read_json(AUDIT/'source-projects.json') if x['project']['path']=='packages/apps/SetupWizard');assert project['revision']==PIN
 tree=read_json(AUDIT/'source-trees/packages__apps__SetupWizard.json')['tree']
 def wanted(p):
  if p.startswith('app/src/main/'):
   if '/res/values-' in p:
    qualifier=p.split('/res/values-',1)[1].split('/')[0]
    if re.fullmatch(r'[a-z]{2,3}(?:-r[A-Z]{2})?',qualifier):return False
   return True
  return p.endswith(('.bp','.gradle.kts','.toml','.pro','.flags','.xml')) or p in ['LICENSE','NOTICE','COPYING','REUSE.toml']
 jobs=[n for n in tree if n['type']=='blob' and wanted(n['path'])]
 def fetch(node):
  path=node['path'];dest=OUT/'upstream'/project['path']/path;cached=BASE/'source/objects'/node['sha'][:2]/node['sha'][2:];prior=AUDIT/'source-evidence'/project['path']/path;url='https://raw.githubusercontent.com/'+project['name']+'/'+PIN+'/'+urllib.parse.quote(path,safe='/')
  data=dest.read_bytes() if dest.exists() else cached.read_bytes() if cached.exists() else prior.read_bytes() if prior.exists() else get(url)
  actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert actual==node['sha'],path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  return {'project':project['path'],'repository':project['name'],'revision':PIN,'path':path,'url':url,'gitBlobSha1':actual,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'saved':dest.relative_to(OUT).as_posix(),'sourceOnlyNotExecuted':True}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=sorted(pool.map(fetch,jobs),key=lambda r:r['path'])
 write_json(OUT/'source-manifest.json',rows)
 state_file=OUT/'WORK-IN-PROGRESS.json';state=read_json(state_file) if state_file.exists() else {'artworkAndOwnerAdaptation':'NOT YET AUTHORED','nativeCompilationAndDeviceAcceptance':'NOT RUN','openBaselineFamilyDecisions':9575,'wholeGoalComplete':False}
 state.update(baseCommit='3848a61e5df38a0e3bb64fa398c65ef18f23fb09',workflow='W-03',project=project,sourceFiles=len(rows));write_json(state_file,state)
 print({'pinnedSetupSourceFiles':len(rows),'bytes':sum(r['bytes'] for r in rows),'revision':PIN,'sourceCodeExecuted':False})
if __name__=='__main__':main()
