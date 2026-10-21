"""Audit cold-off asset separation and renderer parity against the actual exports."""
from pathlib import Path
import argparse,hashlib,json,subprocess,xml.etree.ElementTree as ET
from PIL import Image,ImageChops
from build_reference_forge import LAYERS,COLORS,compose
from verify_scalable_frames import validate
import build_reference_forge as forge

p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--node',required=True);a=p.parse_args();root=a.root.resolve()
style=json.loads((root/'runtime-style.json').read_text());forge.STATES=style['sampleStates']
assert style['colors']==COLORS
prov=json.loads((root/'source/GENERATION.json').read_text());checks=0;coverage={}
for entry in prov['coldSources']:
 name=entry['name'];source=root/'source'/f'{name}-cold.png'
 assert hashlib.sha256(source.read_bytes()).hexdigest()==entry['sha256'];checks+=1
 for size in [256,512,1024]:
  layers={k:Image.open(root/'exports'/f'{name}.{k}.{size}.png').convert('RGBA') for k in LAYERS}
  assert layers['cold'].getchannel('A').getextrema()[0]==0;checks+=1
  for key,im in layers.items():
   assert im.size==(size,size)
   if key!='cold':
    # Nontransparent mask RGB is always neutral white, including antialiased edges.
    assert all(r==g==b==255 for r,g,b,alpha in im.get_flattened_data() if alpha);checks+=1
  if size==512:
   for state in style['sampleStates']:
    actual=Image.open(root/'exports'/f'{name}.{state}.preview.png').convert('RGBA')
    assert actual.tobytes()==compose(layers,state).tobytes();checks+=1
   off=Image.open(root/'exports'/f'{name}.off.preview.png').convert('RGBA')
   assert off.tobytes()==layers['cold'].tobytes();checks+=1
   assert off.tobytes()==Image.open(root/'exports'/f'{name}.hovered.preview.png').convert('RGBA').tobytes();checks+=1
   assert off.tobytes()!=Image.open(root/'exports'/f'{name}.on.preview.png').convert('RGBA').tobytes();checks+=1
   assert Image.open(root/'exports'/f'{name}.reduced.preview.png').convert('RGBA').tobytes()==Image.open(root/'exports'/f'{name}.on.preview.png').convert('RGBA').tobytes();checks+=1
   base=layers['cold'].getchannel('A');seam=layers['seam'].getchannel('A')
   active=[i for i,v in enumerate(seam.get_flattened_data()) if v>32];bd=list(base.get_flattened_data())
   coverage[name]=round(sum(bd[i]>32 for i in active)/len(active),4)
   assert coverage[name]>.85, (name,'emission channels need alignment review',coverage[name]);checks+=1
for file in root.rglob('*.svg'):ET.parse(file);checks+=1
for file in root.rglob('*.png'):
 with Image.open(file) as im:im.load();checks+=1
frame_count=0
for file in (root/'exports/scalable-frames/android/res').rglob('*.9.png'):
 original=Path(__file__).resolve().parents[1]/'iterations/09-rich-scalable-controls/android/res'/file.parent.name/file.name
 assert file.read_bytes()==original.read_bytes();validate(Image.open(file).convert('RGBA'));frame_count+=1;checks+=1
assert frame_count==112
for state in ['off','hovered','focused_off','disabled']:
 assert all(style['sampleStates'][state]['gains'][k]==0 for k in ['seam','core','spill','reflection']);checks+=1
result=subprocess.run([a.node,'--test','tools/state_driver_v2.test.cjs'],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,encoding='utf8',errors='replace');assert result.returncode==0,result.stdout+result.stderr
(root/'verification/evidence/state-tests.txt').write_text(result.stdout+result.stderr,encoding='utf8')
report={'date':'2026-10-21','components':3,'reusedFrameFamilies':4,'reusedNinePatchConfigurations':frame_count,'assertions':checks,'stateTests':6,'svgFiles':len(list(root.rglob('*.svg'))),'pngFiles':len(list(root.rglob('*.png'))),'channelOverlapWithColdAlpha':coverage,'coldBasePreserved':True,'offExactlyEqualsColdExport':True,'allEmissionMasksNeutral':True,'nativeIntegrated':False,'apkUpdated':False,'deviceVerified':False,'v1Scope':'Three reference-style detailed icons, separate neutral light layers, cold-off contract, and four retained scalable-frame family previews. Three inspected desktop passes. Does not claim the entire library has been restyled.','v2Method':'PNG decode, SVG parse, source hash, neutral-mask pixels, off/cold exact equality, recomposition pixel equality, channel alpha overlap, six Node state tests and all 112 retained nine-patch metadata/stretch/corner tests'}
(root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
