'''Verify the exact native compiler and acquire the exact declared listener artifact.'''
from pathlib import Path
import base64,hashlib,subprocess
from audit_os_resource_coverage import ROOT,read_json,write_json
from resolve_gallery_native_dependencies import get
OUT=ROOT/'iterations/27-gallery-contracts';JDK=Path('C:/Program Files/Android/Android Studio/jbr')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 compiler=read_json(OUT/'source/pinned-compiler.json')
 for r in compiler['files']:assert sha(Path(r['localBuildCache']))==r['sha256'];r['participatesInVerifiedCompilerClasspath']=True;r.pop('executed',None)
 args=[str(JDK/'bin/java.exe'),'-cp',';'.join(r['localBuildCache'] for r in compiler['files']),'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler','-version'];p=subprocess.run(args,capture_output=True,text=True,encoding='utf8');output=p.stdout+p.stderr;assert p.returncode==0 and '2.2.0-custom-branch-22' in output
 compiler['executed']=True;write_json(OUT/'source/pinned-compiler.json',compiler);write_json(OUT/'verification/evidence/native-compiler-version.json',{'result':'PASS','command':args,'exitCode':p.returncode,'output':output,'revision':compiler['revision'],'allCompilerInputsHashVerified':True,'wholeGoalComplete':False})
 r=read_json(OUT/'source/native-listener-interface.json');dest=ROOT/'build-work/gallery27-native-dependencies/files'/(r['gitBlobSha1']+'.jar');dest.parent.mkdir(parents=True,exist_ok=True);data=dest.read_bytes() if dest.exists() else base64.b64decode(get(r['url']));assert hashlib.sha256(data).hexdigest()==r['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['gitBlobSha1'];dest.write_bytes(data);r['localBuildCache']=str(dest);write_json(OUT/'source/native-listener-interface.json',r);print({'pinnedCompilerVersion':'2.2.0-custom-branch-22','nativeListenerArtifactHashVerified':True})
if __name__=='__main__':main()
