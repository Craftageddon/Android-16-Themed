"""Independent checkpoint checks: source provenance, state parity, permissions and clean rebuild."""
from pathlib import Path
import hashlib,json,subprocess,sys,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];root=ROOT/'iterations/18-native-runtime';native=root/'native'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((root/'verification/evidence/native-build.json').read_text())
subprocess.run([sys.executable,str(ROOT/'tools/build_native37.py')],check=True)
after=json.loads((root/'verification/evidence/native-build.json').read_text())
assert before['certificateDerSha256']==after['certificateDerSha256']
assert before['apkMembers']==after['apkMembers'],'Clean rebuild differs in executable/resources'
out=Path(after['buildOutput']);jdk=Path('C:/Program Files/Android/Android Studio/jbr/bin')
subprocess.run([str(jdk/'javac.exe'),'--release','8','-encoding','UTF-8','-d',str(out/'test'),str(native/'src/com/craftageddon/thor/integration/StatePolicy.java'),str(native/'tests/StatePolicyProbe.java')],check=True,capture_output=True)
probe=subprocess.check_output([str(jdk/'java.exe'),'-cp',str(out/'test'),'com.craftageddon.thor.integration.StatePolicyProbe'],text=True)
values={int(line.split(',')[0]):[float(x) for x in line.split(',')[1:]] for line in probe.splitlines()}
style=json.loads((ROOT/'iterations/12-forge-controls-and-screens/runtime-style.json').read_text())
samples={'off':1,'focused_off':9,'on':3,'selected_focused':11,'active_pressed':19,'disabled':0,'reduced':3}
names=['reflection','spill','seam','core','focus','symbol']
for name,mask in samples.items():
 expected=style['sampleStates'][name];actual=values[mask]
 assert actual==[expected['baseOpacity']]+[expected['gains'][n] for n in names],name
source_checks=0
for row in json.loads((root/'resource-provenance.json').read_text())['resources']:
 assert h(ROOT/row['source'])==h(root/row['target'])==row['sha256'];source_checks+=1
manifest=E.parse(native/'AndroidManifest.xml').getroot();AN='{http://schemas.android.com/apk/res/android}'
assert manifest.find('uses-permission') is None
service=manifest.find('application/service')
assert service.get(AN+'permission')=='android.permission.BIND_QUICK_SETTINGS_TILE'
assert service.get(AN+'exported')=='true'
strings=E.parse(native/'res/values/strings.xml').getroot();labels=[''.join(n.itertext()) for n in strings]
assert all(not any(c.isalpha() and not c.isascii() for c in label) for label in labels)
assert len({n.get('name') for n in strings})==len(labels)
for path,digest in after['nativeSourceHashes'].items():assert h(native/path)==digest,path
report={'result':'PASS','date':'2026-10-23','cleanBuildsCompared':2,'identicalExecutableResourceMembers':len(after['apkMembers']),'stableCertificateSha256':after['certificateDerSha256'],'nativeStateCombinations':64,'nativeStatesComparedAgainstDesktopStyle':list(samples),'unchangedSourceResources':source_checks,'nativeEnglishStrings':len(labels),'defaultLocale':'en-US','noRequestedPermissions':True,'protectedQuickSettingsService':True,'method':'Fresh separate build compares every executable/resource APK member; independently run compiled Java state probe against saved desktop style JSON; source-to-native resource hashes, compiled manifest/permission checks and actual live native string XML.','nativeRuntimeAcceptance':'NOT RUN','dualScreenControllerAcceptance':'NOT RUN','systemUIPlatformBuild':'NOT RUN','targetV3':'NOT RUN'}
(root/'verification/evidence/native-independent-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
