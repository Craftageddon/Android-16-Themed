"""Offline standalone APK build from installed Android/JDK tools. Never installs it."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,zipfile

def build(a):
 root=a.root.resolve();src=root/'source';work=a.work.resolve();assert not work.exists();work.mkdir(parents=True)
 sdk=a.sdk.resolve();bt=sdk/'build-tools'/a.build_tools;jar=sdk/'platforms'/a.platform/'android.jar';java=a.java_home/'bin/java.exe';javac=a.java_home/'bin/javac.exe';keytool=a.java_home/'bin/keytool.exe';tool=bt/'aapt2.exe'
 for p in [java,javac,keytool,tool,jar,bt/'lib/d8.jar',bt/'lib/apksigner.jar']:assert p.exists(),p
 # Copy the exact versioned resources, so the APK source ZIP works independently.
 res=src/'res'
 if not res.exists():
  assert a.frames is not None,'Supply --frames for the first source assembly';shutil.copytree(a.frames/'android/res',res)
 masters=root/'asset-masters'
 if not masters.exists():
  assert a.frames is not None;shutil.copytree(a.frames/'masters',masters)
 compiled=work/'compiled';compiled.mkdir();generated=work/'generated';generated.mkdir();classes=work/'classes';classes.mkdir();dex=work/'dex';dex.mkdir();release=(a.release_dir or root/'release').resolve();release.mkdir(parents=True,exist_ok=False)
 logs=[]
 def run(args):
  p=subprocess.run(list(map(str,args)),capture_output=True,text=True);logs.append({'tool':Path(str(args[0])).name,'exitCode':p.returncode,'output':(p.stdout+p.stderr)[-12000:]});assert p.returncode==0,f'Build exit {p.returncode}: '+p.stdout+p.stderr;return p.stdout+p.stderr
 aapt_version=run([tool,'version']);java_version=run([java,'-version']);run([tool,'compile','--dir',res,'-o',compiled])
 unaligned=work/'unaligned.apk';run([tool,'link','--manifest',src/'AndroidManifest.xml','-I',jar,'--java',generated,'-o',unaligned,*sorted(compiled.glob('*.flat'))])
 sources=sorted((src/'src').rglob('*.java'))+sorted(generated.rglob('*.java'));run([javac,'--release','8','-classpath',jar,'-d',classes,*sources])
 run([java,'-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--min-api','26','--lib',jar,'--output',dex,*sorted(classes.rglob('*.class'))])
 with zipfile.ZipFile(unaligned,'a',zipfile.ZIP_DEFLATED) as z:
  assert 'classes.dex' not in z.namelist();z.write(dex/'classes.dex','classes.dex')
 aligned=work/'aligned-unsigned.apk';run([bt/'zipalign.exe','-p','-f','4',unaligned,aligned])
 key=a.keystore
 if key is None:
  private=work/'private';private.mkdir();key=private/'local-preview.keystore'
  run([keytool,'-genkeypair','-keystore',key,'-storepass','android','-keypass','android','-alias','androiddebugkey','-keyalg','RSA','-keysize','2048','-validity','3650','-dname','CN=Craftageddon Local Preview,O=Development,C=US'])
 apk=release/'EmberSteel-MaterialLab-0.1.0.apk';run([java,'-jar',bt/'lib/apksigner.jar','sign','--v4-signing-enabled','false','--ks',key,'--ks-pass','pass:android','--key-pass','pass:android','--out',apk,aligned])
 signature=run([java,'-jar',bt/'lib/apksigner.jar','verify','--verbose','--print-certs',apk]);assert 'Verified using v2 scheme' in signature
 assert not list(release.glob('*.idsig')),'Optional sidecar output must stay disabled'
 run([bt/'zipalign.exe','-c','-p','4',apk]);badging=run([tool,'dump','badging',apk]);assert 'com.craftageddon.materiallab' in badging and "targetSdkVersion:'36'" in badging and 'uses-permission:' not in badging
 with zipfile.ZipFile(apk) as z:
  assert z.testzip() is None and {'AndroidManifest.xml','resources.arsc','classes.dex'}<=set(z.namelist())
  assert not any(n.endswith(('.keystore','.jks','.java')) for n in z.namelist())
  compiled_nine=0
  for n in z.namelist():
   if n.endswith('.9.png'):
    data=z.read(n);assert b'npTc' in data,'Missing compiled Android nine-patch chunk';compiled_nine+=1
  assert compiled_nine==80,compiled_nine
 evidence=(a.report_dir or root/'verification/evidence').resolve();evidence.mkdir(parents=True,exist_ok=True);(evidence/'signature.txt').write_text(signature);(evidence/'badging.txt').write_text(badging)
 (evidence/'build-log.json').write_text(json.dumps(logs,indent=2)+'\n')
 report={'date':'2026-10-21','components':4,'version':'0.1.0','package':'com.craftageddon.materiallab','apk':apk.name,'apkBytes':apk.stat().st_size,'apkSha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'compiledNinePatchConfigurations':80,'logicalLayers':20,'javaSources':len(sources),'compiledClasses':len(list(classes.rglob('*.class'))),'signatureVerified':True,'zipAlignmentVerified':True,'requestedPermissions':[],'sdkPlatform':a.platform,'buildTools':a.build_tools,'aapt2Version':aapt_version.strip(),'javaVersion':java_version.strip(),'nativeIntegrated':False,'standaloneAppBuilt':True,'installed':False,'deviceVerified':False,'emulatorRun':False,'v1Scope':'Standalone Android preview application using four versioned scalable frame families; editable masters and neutral masks retained. No privileged OS or hardware integration.','scope':'Offline resource compile/link, Java compile, DEX packaging, ZIP/chunk/manifest audit, signing and alignment only. No installation or runtime screenshots.'}
 report['v2Method']='Android resource/Java/DEX build, compiled nine-patch chunks, manifest, signature and ZIP alignment audits'
 (evidence/'technical.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--frames',type=Path);p.add_argument('--work',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True);p.add_argument('--java-home',type=Path,required=True);p.add_argument('--release-dir',type=Path);p.add_argument('--report-dir',type=Path);p.add_argument('--keystore',type=Path);p.add_argument('--build-tools',default='36.1.0');p.add_argument('--platform',default='android-36.1');build(p.parse_args())
