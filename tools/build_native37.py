"""Build and verify the signed API37 native integration application. No install step."""
from pathlib import Path
import argparse,base64,datetime,hashlib,json,os,re,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from sign_artifact import dpapi
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT/'iterations/18-native-runtime');p.add_argument('--sdk',type=Path,default=Path(os.environ['LOCALAPPDATA'])/'Android/Sdk');p.add_argument('--jdk',type=Path,default=Path('C:/Program Files/Android/Android Studio/jbr'));a=p.parse_args()
root=a.root.resolve();native=root/'native';out=ROOT/'build-work'/('native37-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));out.mkdir(parents=True)
for d in ['gen','classes','dex','test']:(out/d).mkdir()
tool=a.sdk/'build-tools/37.0.0';android=a.sdk/'platforms/android-37.0/android.jar';java=a.jdk/'bin/java.exe'
def run(args,env=None,allow_failure=False):
 result=subprocess.run([str(x) for x in args],env=env,capture_output=True,text=True,encoding='utf8',errors='replace')
 if result.returncode and not allow_failure:raise RuntimeError(result.stdout+'\n'+result.stderr)
 return result
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
run([tool/'aapt2.exe','compile','--dir',native/'res','-o',out/'resources.zip'])
run([tool/'aapt2.exe','link','-o',out/'unsigned.apk','-I',android,'--manifest',native/'AndroidManifest.xml','--java',out/'gen','--auto-add-overlay',out/'resources.zip'])
sources=sorted((native/'src').rglob('*.java'))+sorted((out/'gen').rglob('*.java'))
compile=run([a.jdk/'bin/javac.exe','--release','8','-encoding','UTF-8','-classpath',android,'-d',out/'classes',*sources])
(out/'javac.txt').write_text(compile.stdout+compile.stderr)
run([a.jdk/'bin/jar.exe','cf',out/'classes.jar','-C',out/'classes','.'])
run([java,'-cp',tool/'lib/d8.jar','com.android.tools.r8.D8','--min-api','33','--lib',android,'--output',out/'dex',out/'classes.jar'])
run([a.jdk/'bin/jar.exe','uf',out/'unsigned.apk','-C',out/'dex','classes.dex'])
run([tool/'zipalign.exe','-f','-p','4',out/'unsigned.apk',out/'aligned.apk'])
run([a.jdk/'bin/javac.exe','--release','8','-encoding','UTF-8','-d',out/'test',native/'src/com/craftageddon/thor/integration/StatePolicy.java',native/'tests/StatePolicyTest.java'])
unit=run([java,'-cp',out/'test','com.craftageddon.thor.integration.StatePolicyTest'])
assert 'PASS: 64' in unit.stdout
# Stable project application identity; never reuse a debug key or silently rotate partial state.
private=ROOT/'local-secrets/apk-signing';private.mkdir(parents=True,exist_ok=True);key=private/'forge-native.p12';secret=private/'password.dpapi';pin=private/'certificate-sha256.txt'
assert all(x.exists() for x in [key,secret,pin]) or not any(x.exists() for x in [key,secret,pin]),'Incomplete identity - stop rather than rotate'
env=os.environ.copy()
if key.exists():password=dpapi(secret.read_bytes(),True).decode('ascii')
else:password=base64.urlsafe_b64encode(os.urandom(48)).decode('ascii')
env['CRAFTAGEDDON_APK_STORE_PASSWORD']=password
if not key.exists():
 run([a.jdk/'bin/keytool.exe','-genkeypair','-keystore',key,'-storetype','PKCS12','-storepass:env','CRAFTAGEDDON_APK_STORE_PASSWORD','-keypass:env','CRAFTAGEDDON_APK_STORE_PASSWORD','-alias','forge-native','-keyalg','RSA','-keysize','3072','-validity','10950','-dname','CN=Craftageddon Native Integration, O=Craftageddon, C=US'],env)
 secret.write_bytes(dpapi(password.encode('ascii')))
 cert=out/'certificate.der'
 run([a.jdk/'bin/keytool.exe','-exportcert','-keystore',key,'-storepass:env','CRAFTAGEDDON_APK_STORE_PASSWORD','-alias','forge-native','-file',cert],env)
 pin.write_text(h(cert)+'\n')
else:
 cert=out/'certificate.der'
 run([a.jdk/'bin/keytool.exe','-exportcert','-keystore',key,'-storepass:env','CRAFTAGEDDON_APK_STORE_PASSWORD','-alias','forge-native','-file',cert],env)
 assert h(cert)==pin.read_text().strip(),'Unexpected persistent certificate'
apk=out/'Craftageddon-Thor-Native-0.1.0.apk'
run([java,'-jar',tool/'lib/apksigner.jar','sign','--ks',key,'--ks-key-alias','forge-native','--ks-pass','env:CRAFTAGEDDON_APK_STORE_PASSWORD','--key-pass','env:CRAFTAGEDDON_APK_STORE_PASSWORD','--v4-signing-enabled','false','--out',apk,out/'aligned.apk'],env)
verified=run([java,'-jar',tool/'lib/apksigner.jar','verify','--verbose','--print-certs',apk]);expected=pin.read_text().strip();assert ('certificate SHA-256 digest: '+expected) in verified.stdout
run([tool/'zipalign.exe','-c','-p','4',apk])
with zipfile.ZipFile(apk) as z:
 assert z.testzip() is None
 executable={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.startswith('META-INF/')};assert 'classes.dex' in executable
 tampered=out/'tampered.apk'
 with zipfile.ZipFile(tampered,'w') as t:
  for entry in z.infolist():t.writestr(entry,z.read(entry.filename)+(b'!' if entry.filename=='classes.dex' else b''))
bad=run([java,'-jar',tool/'lib/apksigner.jar','verify',tampered],allow_failure=True);assert bad.returncode!=0,'Tampered APK accepted'
manifest=run([tool/'aapt2.exe','dump','badging',apk]);assert "package: name='com.craftageddon.thor.integration'" in manifest.stdout
assert "targetSdkVersion:'37'" in manifest.stdout and "minSdkVersion:'33'" in manifest.stdout
assert 'uses-permission:' not in manifest.stdout,'Unexpected application permission'
report={'result':'PASS','version':'0.1.0','date':'2026-10-23','package':'com.craftageddon.thor.integration','targetSdk':37,'minSdk':33,'compiledResourceFiles':len(list((native/'res').rglob('*')))-len([p for p in (native/'res').rglob('*') if p.is_dir()]),'nativeStateCombinationsTested':64,'apkSha256':h(apk),'apkBytes':apk.stat().st_size,'certificateDerSha256':expected,'signatureVerified':True,'zipAlignmentVerified':True,'tamperedApkRejected':True,'requestedPermissions':[],'serviceBindPermission':'android.permission.BIND_QUICK_SETTINGS_TILE protects exported tile service; not a requested privilege','authoredLocale':'en-US','apkMembers':executable,'installedOrRun':'NOT RUN','platformSystemUIRebuild':'NOT RUN','deviceAcceptance':'NOT RUN - user chose to continue without a connected Thor','identityScope':'Stable Craftageddon application signer, not AYN/LineageOS platform trust or production acceptance','buildOutput':str(out),'toolchain':{'api37AndroidJarSha256':h(android),'aapt2Sha256':h(tool/'aapt2.exe'),'d8JarSha256':h(tool/'lib/d8.jar'),'apksignerJarSha256':h(tool/'lib/apksigner.jar')},'nativeSourceHashes':{p.relative_to(native).as_posix():h(p) for p in sorted(native.rglob('*')) if p.is_file()}}
dist=root/'package';dist.mkdir(exist_ok=True)
import shutil
shutil.copy2(apk,dist/apk.name);shutil.copy2(cert,dist/'signing-certificate.der')
(dist/(apk.name+'.sha256')).write_text(h(apk)+'  '+apk.name+'\n')
evidence=root/'verification/evidence';(evidence/'native-build.json').write_text(json.dumps(report,indent=2)+'\n');(evidence/'apksigner.txt').write_text(verified.stdout+verified.stderr);(evidence/'badging.txt').write_text(manifest.stdout);(evidence/'state-tests.txt').write_text(unit.stdout)
print(json.dumps({k:v for k,v in report.items() if k not in ['apkMembers','buildOutput']}))
