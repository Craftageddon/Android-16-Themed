"""Whole-catalog source/export verification; no native runtime or device claims."""
from pathlib import Path
import argparse,hashlib,json,subprocess,xml.etree.ElementTree as ET
from PIL import Image,ImageChops
from build_pilot import SVG
from build_symbols import NAMES
from build_components import SPECS as COMPONENTS
from build_pilot import SPECS as PILOT
from build_reference_forge import COLORS,LAYERS
from forge_library import compose_layers,lighting_descriptor
from verify_scalable_frames import validate

def verify(a):
 root=a.root.resolve();rows=json.loads((root/'components.json').read_text());style=json.loads((root/'runtime-style.json').read_text());checks=0;neutral=0;coverage={};pairs=0
 assert len(rows)==(281 if a.kind=='symbols' else 64)
 assert len({r['id'] for r in rows})==len(rows)
 if a.kind=='symbols':
  assert {r['symbol'] for r in rows if r['type']=='symbol'}==set(NAMES)
  assert all(sum(r.get('symbol')==name for r in rows)==2 for name in NAMES)
 else:
  assert {r['canonicalId'] for r in rows if r['type']=='control'}=={s[0] for s in COMPONENTS}
  assert {r['canonicalId'] for r in rows if r['type']=='pilot'}=={s[0] for s in PILOT}
 checks+=4
 provenance=json.loads((root/'source/GENERATION.json').read_text())
 for src in provenance['coldSources']:
  f=root/'source'/src['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==src['sha256'];checks+=1
 proxy=provenance['textureProxy'];assert hashlib.sha256((root/'source'/proxy['file']).read_bytes()).hexdigest()==proxy['sha256'];checks+=1
 for row in rows:
  key=row['id'];doc=ET.parse(root/'masters'/f'{key}.svg').getroot();assert not doc.findall('.//{'+SVG+'}text');checks+=1
  for key2 in LAYERS:
   g=doc.find('{'+SVG+'}g[@id="'+key2+'"]');assert g is not None
   if key2!='cold':assert g.get('style')=='display:none'
   else:assert all(n.get('filter') is None for n in g.iter())
   checks+=1
  for width in row['exportWidths']:
   layers={k:Image.open(root/'exports'/f'{key}.{k}.{width}.png').convert('RGBA') for k in LAYERS}
   assert layers['cold'].width==width;checks+=1
   for name,im in layers.items():
    assert im.getchannel('A').getextrema()[0]==0, (key,name,'missing transparent region')
    if name!='cold':
     r,g,b,_=im.split();assert not ImageChops.difference(r,g).getbbox();assert not ImageChops.difference(g,b).getbbox();neutral+=1
    checks+=1
   if width==row['exportWidths'][-1]:
    for st,s in style['sampleStates'].items():
     desc=lighting_descriptor(s,row['emissionLockedOff']);expected=compose_layers(layers,desc)
     with Image.open(root/'exports'/f'{key}.{st}.preview.png') as actual:assert actual.convert('RGBA').tobytes()==expected.tobytes(), (key,st)
     pairs+=1;checks+=1
    with Image.open(root/'exports'/f'{key}.off.preview.png') as off:assert off.convert('RGBA').tobytes()==layers['cold'].tobytes();checks+=1
    # Only inspect channel overlap for sculpted masters: blur intentionally extends beyond metal.
    if row['type']=='hero':
     seam=layers['seam'].getchannel('A');cold=layers['cold'].getchannel('A');active=seam.point(lambda v:255 if v>32 else 0);inside=ImageChops.multiply(active,cold.point(lambda v:255 if v>32 else 0))
     total=sum(active.histogram()[1:]);valid=sum(inside.histogram()[1:]);coverage[key]=round(valid/max(1,total),4);assert coverage[key]>.85,(key,coverage[key]);checks+=1
  if row['emissionLockedOff']:
   assert all(lighting_descriptor(s,True)['gains'][k]==0 for s in style['sampleStates'].values() for k in ['reflection','spill','seam','core']);checks+=1
 svg_count=0
 for f in root.rglob('*.svg'):
  doc=ET.parse(f).getroot();svg_count+=1;ids=[n.get('id') for n in doc.iter() if n.get('id')];assert len(ids)==len(set(ids)),f
  for node in doc.findall('.//{'+SVG+'}image'):
   href=node.get('href','')
   if href and not href.startswith('data:'):
    resolved=(f.parent/href).resolve();assert resolved.is_relative_to(root) and resolved.is_file(),(f,href)
  checks+=1
 png_count=0
 for f in root.rglob('*.png'):
  with Image.open(f) as im:im.verify()
  png_count+=1;checks+=1
 if a.kind=='controls':
  patches=sorted((root/'android/res').rglob('*.9.png'));assert len(patches)==112
  for f in patches:validate(Image.open(f).convert('RGBA'));checks+=1
  layouts=json.loads((root/'screens/layout-metadata.json').read_text());assert layouts['screenCount']==8
  for name in layouts['names']:
   doc=ET.parse(root/'screens'/f'{name}.svg').getroot();assert doc.findall('.//{'+SVG+'}text');assert (root/'screens'/f'{name}.png').is_file();checks+=1
 tests=subprocess.run([a.node,'--test','tools/state_driver_v2.test.cjs'],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,encoding='utf8',errors='replace');assert tests.returncode==0,tests.stdout+tests.stderr
 (root/'verification/evidence/state-tests.txt').write_text(tests.stdout+tests.stderr,encoding='utf8')
 contrast={}
 if 'contentColors' in style:
  def luminance(color):
   vals=[int(color[i:i+2],16)/255 for i in [1,3,5]];vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals];return sum(v*w for v,w in zip(vals,[.2126,.7152,.0722]))
  bg=luminance(style['contentColors']['well'])
  for key in ['text','secondary','semantic']:
   value=(luminance(style['contentColors'][key])+.05)/(bg+.05);assert value>=4.5;contrast[key]=round(value,2);checks+=1
 report={'date':'2026-10-21','components':len(rows),'kind':a.kind,'assertions':checks,'neutralLayerExports':neutral,'recomposedStates':pairs,'svgFiles':svg_count,'pngFiles':png_count,'sculptedChannelOverlap':coverage,'stateTests':7,'coldBasesUnchanged':True,'offPixelIdenticalToCold':True,'offValueArtCannotEmit':True,'quietWellPaletteContrast':contrast,'contrastScope':'Design palette only; actual device brightness, text size and performance not validated','nativeIntegrated':False,'deviceVerified':False,'apkUpdated':False,'v1Scope':'All 136 retained named symbols in two optical treatments plus nine sculpted motifs.' if a.kind=='symbols' else 'All 46 retained control variants and all 18 pilot specimens, four newly textured scalable frames and eight existing screen compositions. This is authored-catalog coverage, not complete Android OS coverage.','v2Method':'Source hashes, alpha, neutral masks, SVG links and unique IDs, exact off/cold and runtime recomposition parity, catalog set equality, PNG/SVG decoding, state-owner tests, quiet-well palette contrast and nine-patch audits where applicable'}
 (root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--kind',choices=['symbols','controls'],required=True);p.add_argument('--node',required=True);verify(p.parse_args())
