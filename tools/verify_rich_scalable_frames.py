"""Check actual rich nine-patch exports, light separation and Android compile/link."""
from pathlib import Path
import argparse,hashlib,json,subprocess,xml.etree.ElementTree as ET
from PIL import Image
from verify_scalable_frames import validate
from build_rich_scalable_frames import LAYERS,STATES,LIGHT_COLORS,composite

def verify(a):
 root=a.root.resolve();rows=json.loads((root/'components.json').read_text());assert len(rows)==4
 original=a.original.read_bytes();source=root/'source/cold-frame.png';assert source.read_bytes()==original
 digest=hashlib.sha256(original).hexdigest();files=sorted((root/'android/res').rglob('*.9.png'));assert len(files)==112;neutral=0
 for p in files:
  with Image.open(p) as im:
   src=validate(im)
   if not p.name.endswith('_cold.9.png'):
    pixels=[v for v in src.get_flattened_data() if v[3]>0];assert pixels and all(r==g==b==255 for r,g,b,alpha in pixels);neutral+=1
 assert neutral==96
 ns='{http://www.w3.org/2000/svg}'
 for row in rows:
  assert row['sourceColdSha256']==digest
  doc=ET.parse(root/'masters'/f"{row['id']}.svg").getroot();assert not doc.findall('.//'+ns+'text')
  for key in LAYERS:
   g=doc.find(ns+f"g[@id='{key}']");assert g is not None
   if key!='cold':assert g.get('style')=='display:none'
  cold=doc.find(ns+"g[@id='cold']");assert all(n.get('filter') is None for n in cold.iter())
  for p in cold.iter():
   if p.tag in [ns+'path',ns+'rect']:assert p.get('fill')=='#151b21'
  states={s:hashlib.sha256((root/'exports'/f"{row['id']}.{s}.preview.png").read_bytes()).hexdigest() for s in ['cold','idle','selected','pressed','disabled']};assert len(set(states.values()))==5
 assert STATES['disabled'][1:]==[0]*6 and STATES['selected'][-1]==STATES['pressed'][-1]==1
 assert STATES['selected_focused'][-2:]==[1,1]
 spec=json.loads((root/'runtime-style.json').read_text());assert spec['layerOrder']==LAYERS and spec['colors']==LIGHT_COLORS
 matched=0
 for row in rows:
  name=row['id'];h=row['size'][1];layers={key:Image.open(root/'android/res/drawable-xhdpi'/f'cg_es_rich_{name}_{key}.9.png').convert('RGBA') for key in LAYERS}
  for state in STATES:
   actual=composite(layers,(800,max(224,h*2)),state)
   with Image.open(root/'exports'/f'{name}.{state}.preview.png') as saved:assert actual.tobytes()==saved.convert('RGBA').tobytes()
   assert spec['sampleStateLayerGains'][state]==dict(zip(LAYERS,STATES[state]));matched+=1
 for p in root.rglob('*.svg'):ET.parse(p)
 for p in root.rglob('*.png'):
  with Image.open(p) as im:im.verify()
 work=a.work.resolve();work.mkdir(parents=True,exist_ok=False);compiled=work/'compiled';compiled.mkdir()
 def run(args):
  p=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert p.returncode==0,f'Compiler exit {p.returncode}: '+p.stdout+p.stderr;return p.stdout+p.stderr
 version=run([a.aapt2,'version']);run([a.aapt2,'compile','--dir',root/'android/res','-o',compiled]);flats=sorted(compiled.glob('*.flat'));assert len(flats)==112
 manifest=work/'AndroidManifest.xml';manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.craftageddon.richresources"><uses-sdk android:minSdkVersion="26" android:targetSdkVersion="36"/><application android:label="Rich resource smoke"/></manifest>')
 run([a.aapt2,'link','--manifest',manifest,'-I',a.android_jar,'-o',work/'resources.ap_',*flats]);dump=run([a.aapt2,'dump','resources',work/'resources.ap_']);ids=[l for l in dump.splitlines() if 'resource 0x' in l and 'drawable/' in l];assert len(ids)==28
 report={'date':'2026-10-21','components':4,'layersPerFamily':7,'densityVariants':4,'ninePatchConfigurations':112,'neutralMaskConfigurations':96,'fixedCornerComparisons':1344,'uniformBandChecks':224,'unmodifiedColdSourceSha256':digest,'coldLayersContainNoLightFilter':True,'distinctStateSnapshotsVerified':20,'parsedSvgs':len(list(root.rglob('*.svg'))),'decodedPngs':len(list(root.rglob('*.png'))),'compiledConfigurations':112,'linkedDrawables':28,'aapt2Version':version.strip(),'nativeIntegrated':False,'deviceVerified':False,'apkUpdated':False,'v2Method':'SVG/pixel/alpha/light-separation checks, fixed-cap and constant-band audit, Android resource compile/link','scope':'Actual layered export previews; runtime/device V3 remains pending. Earlier Material Lab APK is unchanged.'}
 report['runtimeStyleMatchingSavedPreviews']=matched
 (root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n');(root/'verification/evidence/resource-table.txt').write_text(dump);print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--original',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--aapt2',type=Path,required=True);p.add_argument('--android-jar',type=Path,required=True);verify(p.parse_args())
