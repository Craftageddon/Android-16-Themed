'''Compile every actual Gallery Java/Kotlin owner with real linked resource classes and native inputs.'''
from pathlib import Path
import datetime,hashlib,json,subprocess,zipfile
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/27-gallery-contracts';UP=OUT/'upstream/packages/apps/Glimpse';PATCH=OUT/'native-patch/packages/apps/Glimpse';JDK=Path('C:/Program Files/Android/Android Studio/jbr')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 link=read_json(OUT/'verification/evidence/full-resource-link.json');ns=read_json(OUT/'verification/evidence/real-resource-namespace-checks.json');deps=read_json(OUT/'verification/evidence/native-dependency-compilation.json');compiler=read_json(OUT/'source/pinned-compiler.json');closure=read_json(OUT/'source/native-dependency-closure.json');listener=read_json(OUT/'source/native-listener-interface.json')
 assert link['result']==ns['result']==deps['result']=='PASS';assert link['linkedResourcePackageSha256']==ns['resourceLinkSha256'];source_work=Path(link['work']);graph=read_json(source_work/'dependency-graph.json');rows={r['module']:r for r in read_json(source_work/'library-resource-inputs.json')};rjars={r['module']:r for r in read_json(source_work/'real-r-namespace-inputs.json')};built={r['module']:Path(r['jar']) for r in deps['modules']};stdlib=Path(next(r['localBuildCache'] for r in compiler['files'] if r['path']=='lib/kotlin-stdlib.jar'));android=Path(closure['sdk36']['localBuildCache'])
 mapping={'error_prone_annotations':built['error_prone_annotations'],'jspecify':built['jspecify'],'guava':built['guava-android-host'],'guava-listenablefuture-prebuilt-jar':Path(listener['localBuildCache']),'kotlin-stdlib':stdlib,'kotlinx-coroutines-core':built['kotlinx_coroutines-host'],'kotlinx_coroutines':built['kotlinx_coroutines-host'],'kotlinx_coroutines-host':built['kotlinx_coroutines-host'],'kotlinx-coroutines-android':built['kotlinx_coroutines_android'],'kotlinx_coroutines_android':built['kotlinx_coroutines_android'],'kotlinx_serialization_core':built['kotlinx_serialization_core']}
 # Annotation-only and atomicfu are real compiled native module inputs, not invented classes.
 graph['graph']['guava']={'dependencies':['jsr305','error_prone_annotations','guava-android-annotation-stubs'],'artifact':None};mapping.update({n:built[n] for n in ['jsr305','guava-android-annotation-stubs','kotlinx_atomicfu']})
 for name in ['kotlinx-coroutines-core','kotlinx_coroutines','kotlinx_coroutines-host']:graph['graph'].setdefault(name,{'dependencies':['kotlinx_atomicfu'],'artifact':None})
 order=[];seen=set()
 def visit(name):
  if name in seen:return
  seen.add(name);order.append(name)
  for dep in graph['graph'].get(name,{}).get('dependencies',[]):visit(dep)
 for name in graph['app']['static_libs']:visit(name)
 cp=[android,Path(ns['appRClasses'])];providers=[]
 for name in order:
  if name in rows:
   row=rows[name];f=Path(row['classesJar']);assert sha(f)==row['classesSha256'];cp.append(f)
   if name in rjars:
    rr=rjars[name];jar=Path(rr['resourceJar']);assert sha(jar)==rr['resourceJarSha256'];cp.append(jar)
   providers.append({'module':name,'classpath':str(f),'sha256':sha(f),'namespace':row['namespace']})
  elif name in mapping:cp.append(mapping[name]);providers.append({'module':name,'classpath':str(mapping[name]),'sha256':sha(mapping[name])})
  else:
   art=graph['graph'].get(name,{}).get('artifact')
   if art and Path(art).suffix=='.jar':cp.append(Path(art));providers.append({'module':name,'classpath':art,'sha256':sha(Path(art))})
 # Preorder first-provider semantics match native static class dependency order.
 cp=list(dict.fromkeys(cp));effective={}
 for root in [UP/'app/src/main/java',PATCH/'app/src/main/java']:
  for p in root.rglob('*'):
   if p.suffix in ['.java','.kt']:effective[p.relative_to(root).as_posix()]=p
 java=sorted(p for p in effective.values() if p.suffix=='.java');kotlin=sorted(p for p in effective.values() if p.suffix=='.kt');assert len(java)==9 and len(kotlin)>40
 work=ROOT/'build-work'/('gallery27-owners-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True);(work/'java').mkdir();(work/'kotlin').mkdir();logs=[]
 def run(command,name):
  p=subprocess.run([str(x) for x in command],capture_output=True,text=True,encoding='utf8',errors='replace');f=work/(name+'.log');f.write_text(p.stdout+p.stderr,encoding='utf8');logs.append({'stage':name,'command':[str(x) for x in command],'exitCode':p.returncode,'log':str(f)})
  if p.returncode:raise RuntimeError(name+' failed\n'+(p.stdout+p.stderr)[-11000:])
 def argsfile(name,args):
  p=work/(name+'.args');p.write_text('\n'.join('"'+str(x).replace('\\','/')+'"' for x in args),encoding='utf8');return '@'+str(p)
 try:
  run([JDK/'bin/javac.exe',argsfile('javac',['--release','17','-proc:none','-encoding','UTF-8','-cp',';'.join(map(str,cp)),'-d',work/'java',*java])],'java')
  runtime=';'.join(r['localBuildCache'] for r in compiler['files']);args=['-no-stdlib','-no-reflect','-no-jdk','-jvm-target','17','-module-name','Glimpse','-classpath',';'.join(map(str,[work/'java',*cp])),'-d',work/'kotlin',*kotlin]
  run([JDK/'bin/java.exe','-Xmx4096m','-cp',runtime,'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',argsfile('kotlinc',args)],'kotlin')
 except Exception:
  write_json(OUT/'verification/evidence/complete-owner-compilation-attempt.json',{'result':'FAIL','work':str(work),'actualJavaSources':len(java),'actualKotlinSources':len(kotlin),'commands':logs,'nativeSourceDependencies':providers,'modelsOrControllersSubstituted':False,'wholeGoalComplete':False});raise
 run([JDK/'bin/jar.exe','cf',work/'Glimpse-source-classes.jar','-C',work/'java','.', '-C',work/'kotlin','.'],'jar')
 sources={name:{'source':str(p.relative_to(ROOT)),'sha256':sha(p)} for name,p in effective.items()}
 write_json(OUT/'verification/evidence/complete-owner-compilation.json',{'result':'PASS','work':str(work),'actualJavaSources':len(java),'actualKotlinSources':len(kotlin),'sourceFiles':sources,'commands':logs,'nativeSourceDependencies':providers,'resourceLinkSha256':link['linkedResourcePackageSha256'],'sdk36Sha256':sha(android),'pinnedCompilerRevision':compiler['revision'],'classJar':str(work/'Glimpse-source-classes.jar'),'classJarSha256':sha(work/'Glimpse-source-classes.jar'),'modelsOrControllersSubstituted':False,'officialSoongInvocation':'NOT RUN','nativeInflationAndDeviceTests':'NOT RUN','wholeGoalComplete':False})
 print({'actualJavaSourcesCompiled':len(java),'actualKotlinSourcesCompiled':len(kotlin),'modelsOrControllersSubstituted':False,'officialSoongInvocation':'NOT RUN'})
if __name__=='__main__':main()
