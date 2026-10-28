'''Compile native dependency source inputs with the manifest-pinned compiler; no substitute app models.'''
from pathlib import Path
import datetime,hashlib,json,re,subprocess,zipfile
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/27-gallery-contracts';JDK=Path('C:/Program Files/Android/Android Studio/jbr')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def strip_comments(text):return re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',lambda m:m[0] if m[0].startswith('"') else '',text,flags=re.S)
def body(text,name):
 for _,b in re.findall(r'(\w+)\s*\{(.*?)^\}',strip_comments(text),re.S|re.M):
  n=re.search(r'\bname:\s*"([^"]+)"',b)
  if n and n[1]==name:return b
 raise KeyError(name)
def field(b,name):
 m=re.search(r'\b'+name+r':\s*\[(.*?)\]',b,re.S);return [json.loads(x) for x in re.findall(r'"(?:\\.|[^"\\])*"',m[1])] if m else []
def glob_regex(pattern):
 parts=pattern.split('/');s='^'
 for i,p in enumerate(parts):
  if p=='**':s+='(?:[^/]+/)*';continue
  s+=re.escape(p).replace(r'\*','[^/]*').replace(r'\?','[^/]')
  if i<len(parts)-1:s+='/'
 return s+'$'
def main():
 compiler=read_json(OUT/'source/pinned-compiler.json');closure=read_json(OUT/'source/native-dependency-closure.json');extra=read_json(OUT/'source/additional-native-declarations.json');sources=read_json(OUT/'source/native-source-inputs.json');bps={r['project']:Path(r['localBuildCache']).read_text(encoding='utf8') for r in closure['externalDeclarations']+extra};src={}
 for r in sources:
  for f in r.get('sourceFiles',[]):
   p=Path(f['localBuildCache']);assert sha(p)==f['sha256'];src.setdefault(r['project'],{})[f['path']]=p
 stdlib=Path(next(r['localBuildCache'] for r in compiler['files'] if r['path']=='lib/kotlin-stdlib.jar'));annotation=Path(next(r['localBuildCache'] for r in compiler['files'] if r['path']=='lib/annotations-13.0.jar'));android=Path(closure['sdk36']['localBuildCache'])
 runtime=';'.join(r['localBuildCache'] for r in compiler['files']);work=ROOT/'build-work'/('gallery27-native-libs-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True);logs=[];built={};records=[]
 # Host-only coroutine source needs Java instrumentation and sun.misc from the JDK.
 # Keep its Android annotation types from the real pinned SDK without shadowing JDK java.*.
 host_annotations=work/'android-public-annotations.jar'
 with zipfile.ZipFile(android) as source,zipfile.ZipFile(host_annotations,'w',zipfile.ZIP_DEFLATED) as target:
  for name in source.namelist():
   if name.startswith('android/annotation/') and name.endswith('.class'):target.writestr(name,source.read(name))
 def kind_of(project,name):
  for kind,b in re.findall(r'(\w+)\s*\{(.*?)^\}',strip_comments(bps[project]),re.S|re.M):
   match=re.search(r'\bname:\s*"([^"]+)"',b)
   if match and match[1]==name:return kind
  raise KeyError(name)
 def run(args,name):
  p=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf8',errors='replace');(work/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf8');logs.append({'module':name,'command':[str(x) for x in args],'exitCode':p.returncode,'log':str(work/(name+'.log'))})
  if p.returncode:raise RuntimeError(name+' failed\n'+(p.stdout+p.stderr)[-7000:])
  return p.stdout+p.stderr
 def select(project,patterns,excludes):
  include=[re.compile(glob_regex(x)) for x in patterns];exclude=[re.compile(glob_regex(x)) for x in excludes];rows=[(name,p) for name,p in src[project].items() if any(x.fullmatch(name) for x in include) and not any(x.fullmatch(name) for x in exclude)];return sorted(rows)
 def compile_module(name,project,deps=(),java=False,extra_source_modules=()):
  b=body(bps[project],name);main=select(project,field(b,'srcs'),field(b,'exclude_srcs'));common=select(project,field(b,'common_srcs'),field(b,'exclude_common_srcs'));classes=work/name;classes.mkdir();jar=work/(name+'.jar');cp=[stdlib,annotation,*[built[x] for x in deps]]
  selected=main+common
  for ext_name in extra_source_modules:
   bb=body(bps[project],ext_name);selected+=select(project,field(bb,'srcs'),field(bb,'exclude_srcs'))
  assert selected,(name,b)
  if java:
   version=re.search(r'\bjava_version:\s*"([^"]+)"',b);version=version[1] if version else '17';version='8' if version=='1.8' else version
   flags=['-source',version,'-target',version] if version=='8' else ['--release',version]
   args=[*flags,'-proc:none','-encoding','UTF-8','-cp',';'.join(map(str,cp)),'-d',str(classes),*[str(p) for _,p in selected]];argfile=work/(name+'.args');argfile.write_text('\n'.join('"'+x.replace('\\','/')+'"' for x in args),encoding='utf8');run([JDK/'bin/javac.exe','@'+str(argfile)],name)
  else:
   host=kind_of(project,name)=='java_library_host';cp.append(host_annotations if host else android);flags=field(b,'kotlincflags');args=['-no-stdlib','-no-reflect',*([] if host else ['-no-jdk']),'-jvm-target','17','-module-name',name,'-classpath',';'.join(map(str,cp)),'-d',str(classes),*flags]
   if common:args+=['-Xcommon-sources='+','.join(str(p) for _,p in common)]
   args += [str(p) for _,p in selected];argfile=work/(name+'.args');argfile.write_text('\n'.join('"'+x.replace('\\','/')+'"' for x in args),encoding='utf8');run([JDK/'bin/java.exe','-Xmx3072m','-cp',runtime,'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','@'+str(argfile)],name)
  run([JDK/'bin/jar.exe','cf',jar,'-C',classes,'.'],name+'-jar');built[name]=jar;records.append({'module':name,'project':project,'sourceFiles':[{'path':n,'sha256':sha(p)} for n,p in selected],'sourceFileCount':len(selected),'commonSourceFileCount':len(common),'jar':str(jar),'jarSha256':sha(jar),'originalBuildFlags':field(b,'kotlincflags'),'nativeSoongInvocation':False,'moduleKind':kind_of(project,name),'hostJdkSymbolsEnabled':kind_of(project,name)=='java_library_host'});print('Compiled '+name+' / '+str(len(selected))+' real source files',flush=True);write_json(OUT/'verification/evidence/native-dependency-compilation-progress.json',{'work':str(work),'modules':records,'wholeGoalComplete':False})
 try:
  compile_module('jsr305','external/jsr305',java=True)
  compile_module('jspecify','external/jspecify',java=True)
  compile_module('error_prone_annotations','external/error_prone',deps=['jspecify'],java=True)
  compile_module('guava-android-annotation-stubs','external/guava',java=True)
  compile_module('guava-android-host','external/guava',deps=['jsr305','error_prone_annotations','guava-android-annotation-stubs'],java=True,extra_source_modules=['guava-both'])
  compile_module('kotlinx-coroutines-android-annotation-stubs','external/kotlinx.coroutines',java=True)
  compile_module('kotlinx_atomicfu','external/kotlinx.atomicfu')
  compile_module('kotlinx_coroutines-host','external/kotlinx.coroutines',deps=['kotlinx_atomicfu','kotlinx-coroutines-android-annotation-stubs'])
  # The Android module's public annotation dependency is the exact native AndroidX jar.
  ann=next(r for r in closure['platformLibraries'] if r['module']=='androidx.annotation_annotation');built['androidx.annotation_annotation']=Path(ann['classesJar'])
  compile_module('kotlinx_coroutines_android','external/kotlinx.coroutines',deps=['kotlinx_coroutines-host','kotlinx_atomicfu','kotlinx-coroutines-android-annotation-stubs','androidx.annotation_annotation'])
  compile_module('kotlinx_serialization_core','external/kotlinx.serialization')
 except Exception:
  write_json(OUT/'verification/evidence/native-dependency-compilation-attempt.json',{'result':'FAIL','work':str(work),'completedModules':records,'commands':logs,'wholeGoalComplete':False});raise
 write_json(OUT/'verification/evidence/native-dependency-compilation.json',{'result':'PASS','work':str(work),'modules':records,'commands':logs,'compilerRevision':compiler['revision'],'sourceTreesGitVerified':True,'officialSoongBuild':'NOT RUN','wholeGoalComplete':False})
 print({'nativeSourceModules':len(records),'realSourcesCompiled':sum(r['sourceFileCount'] for r in records)})
if __name__=='__main__':main()
