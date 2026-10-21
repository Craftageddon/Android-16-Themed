"""Bounded AAPT2 resource compile/link check, kept distinct from runtime validation."""
from pathlib import Path
import argparse,json,subprocess
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--work',type=Path,required=True);p.add_argument('--aapt2',type=Path,required=True);p.add_argument('--android-jar',type=Path,required=True);a=p.parse_args();root=a.root.resolve();work=a.work.resolve();work.mkdir(parents=True,exist_ok=False);compiled=work/'compiled';compiled.mkdir()
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert r.returncode==0,f'exit {r.returncode}: '+r.stdout+r.stderr;return r.stdout+r.stderr
version=run([a.aapt2,'version']);run([a.aapt2,'compile','--dir',root/'android/res','-o',compiled]);flats=sorted(compiled.glob('*.flat'));report=json.loads((root/'verification/evidence/technical.json').read_text());expected=136 if report['kind']=='symbols' else 112;assert len(flats)==expected
manifest=work/'AndroidManifest.xml';manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.craftageddon.forgecheck"><uses-sdk android:minSdkVersion="26" android:targetSdkVersion="36"/><application android:label="Forge resource check"/></manifest>')
run([a.aapt2,'link','--manifest',manifest,'-I',a.android_jar,'-o',work/'resources.ap_',*flats]);dump=run([a.aapt2,'dump','resources',work/'resources.ap_']);ids=[l for l in dump.splitlines() if 'resource 0x' in l and 'drawable/' in l];assert len(ids)==(136 if report['kind']=='symbols' else 28)
report.update(compiledConfigurations=len(flats),linkedDrawables=len(ids),aapt2Version=version.strip(),nativeRuntimeValidation=False);report['v2Method']+='; Android resource compile/link'
(root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n');(root/'verification/evidence/resource-table.txt').write_text(dump);print(json.dumps({'compiled':len(flats),'linked':len(ids),'kind':report['kind']}))
