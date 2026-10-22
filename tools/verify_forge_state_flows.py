"""Bounded editable-source, geometry, state and offline journey verification."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,xml.etree.ElementTree as ET
from PIL import Image,ImageChops
from build_pilot import SVG
from build_reference_forge import LAYERS

ROOT=Path(__file__).resolve().parents[1]
EMISSION=['reflection','spill','seam','core']

def verify(root,node):
 defs=json.loads((root/'flow-definitions.json').read_text(encoding='utf8'));scenes=json.loads((root/'screens/layout-metadata.json').read_text());families=json.loads((root/'journey-index.json').read_text());states=json.loads((root/'runtime-style.json').read_text())['sampleStates'];checks=0;texts=0;actions=0
 ids={r['id'] for r in defs};assert len(ids)==len(defs)==len(scenes)==120;assert ids=={r['id'] for r in scenes};checks+=2
 assert set(families)=={r['family'] for r in defs};checks+=1
 byid={r['id']:r for r in defs};visited=set();queue=[rows[0] for rows in families.values()]
 while queue:
  key=queue.pop()
  if key in visited:continue
  visited.add(key);queue.extend(a[2] for a in byid[key]['actions'])
 assert visited==ids,'Unreachable state';checks+=1
 for d in defs:
  assert len({a[0] for a in d['actions']})==len(d['actions']);checks+=1
  for a in d['actions']:assert len(a)==3 and a[2] in ids;actions+=1;checks+=1
 assert {a[2] for a in byid['capture-consent']['actions']}=={'record-countdown','capture-denied'};assert all(a[2] not in ['record-active','record-paused'] for a in byid['capture-denied']['actions']);checks+=2
 assert [a[2] for a in byid['record-countdown']['actions']]==['record-active','capture-choose'];checks+=1
 for kind in ['mapping','profile','fan','charging','lighting']:
  assert kind+'-pending' in ids and kind+'-error' in ids and kind+'-applied' in ids;checks+=1
 provenance=json.loads((root/'source/provenance.json').read_text());prior=ROOT/provenance['baseline']
 assert provenance['newComponentMasters']==0 and len(provenance['reusedMasters'])==18;checks+=1
 for row in provenance['reusedMasters']:
  f=root/'masters'/f"{row['id']}.svg";assert f.read_bytes()==(prior/'masters'/f.name).read_bytes();assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256'];checks+=2
  doc=ET.parse(f).getroot();assert not doc.findall('.//{'+SVG+'}text');checks+=1
  for name in LAYERS:
   g=doc.find('{'+SVG+'}g[@id="'+name+'"]');assert g is not None
   if name!='cold':assert g.get('style')=='display:none'
   else:assert all(n.get('filter') is None for n in g.iter())
   checks+=1
 for row in provenance['inputs']:
  f=root/'source'/row['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256'];assert f.read_bytes()==(prior/'source'/f.name).read_bytes();checks+=2
 for s in scenes:
  key=s['id'];d=byid[key];w,h=s['logicalSize'];assert s['fixtureOnly'] and not s['nativeIntegrated'] and not s['deviceVerified'] and not s['measuredDeviceGeometry'];assert s['authoredLocale']=='en-US';checks+=2
  assert {(a['id'],a['label'],a['target']) for a in s['flowActions']}=={tuple(a) for a in d['actions']};checks+=1
  for a in s['flowActions']:
   if a.get('viewerOnly'):continue
   assert not a['label'].lower().startswith(('preview','load sample'));x,y,ww,hh=a['bounds'];assert x>=12 and y>=140 and x+ww<=w-12 and y+hh<=h-55;checks+=2
  for t in s['textBoxes']:
   x,y,ww,hh=t['bounds'];assert 12<=x and x+ww<=w-12+.01 and 0<=y and y+hh<h,(key,t);texts+=1;checks+=1
  for i,a in enumerate(s['textBoxes']):
   x,y,ww,hh=a['bounds']
   for b in s['textBoxes'][i+1:]:
    xx,yy,bw,bh=b['bounds'];assert min(x+ww,xx+bw)-max(x,xx)<=1 or min(y+hh,yy+bh)-max(y,yy)<=1,(key,a['text'],b['text'])
  checks+=1
  for a in s['artworkOwners']:
   x,y,ww,hh=a['bounds'];assert 0<=x and 0<=y and x+ww<=w and y+hh<=h;assert a['state'] in states;checks+=2
  doc=ET.parse(root/'screens'/f'{key}.svg').getroot();cold=ET.parse(root/'inspections'/f'{key}.cold-material.svg').getroot();assert doc.findall('.//{'+SVG+'}text');checks+=1
  for n in cold.iter():
   if n.get('data-forge-layer') in EMISSION:assert n.get('opacity')=='0';checks+=1
  for n in doc.iter():
   if n.get('data-state') in ['off','hovered','focused_off','disabled']:
    for g in n.findall('{'+SVG+'}g'):
     if g.get('data-forge-layer') in EMISSION:assert g.get('opacity')=='0';checks+=1
  if s['unavailable']:
   assert all(a['state'] in ['off','disabled','focused_off'] for a in s['artworkOwners']),(key,'Unavailable artwork emits');checks+=1
  normal_pixels=Image.open(root/'screens'/f'{key}.png').convert('RGBA');cold_pixels=Image.open(root/'inspections'/f'{key}.cold-material.png').convert('RGBA')
  if not any(a['state'] in ['on','selected_focused','pressed'] for a in s['artworkOwners']):assert normal_pixels.tobytes()==cold_pixels.tobytes(),key
  else:assert ImageChops.difference(normal_pixels.convert('RGB'),cold_pixels.convert('RGB')).getbbox(),(key,'Selected emission did not render')
  checks+=1
  labels={t['text'] for t in s['textBoxes']}
  assert all(not c.isalpha() or c.isascii() for label in labels for c in label),(key,'Non-English script in authored labels');checks+=1
  if key in ['pin-entry','pin-error','pin-lockout']:
   assert set('0123456789')<=labels and '⌫' in labels;checks+=1
   if key=='pin-lockout':assert all(a['state']=='disabled' for a in s['artworkOwners'] if a['owner']=='pin_key');checks+=1
  if s.get('keyboardLayout') in ['lower','upper','caps','email','url']:
   alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ' if s['keyboardLayout'] in ['upper','caps'] else 'abcdefghijklmnopqrstuvwxyz';assert set(alphabet)<=labels;checks+=1
  if key=='keyboard-email':assert {'Email address','name@example.com','@','Space'}<=labels;checks+=1
  if key=='keyboard-url':assert {'Website address','https://example.com','/','.com','Go'}<=labels;checks+=1
  if key=='profile-partial':
   owner_states={a['owner']:a['state'] for a in s['artworkOwners']};assert owner_states['Display layout state']=='on' and owner_states['Input mapping state']=='on' and owner_states['Fan preference state']=='off';checks+=1
  if key=='profile-restored':assert 'Previous layout' in labels;checks+=1
  if s['group']=='thor':assert s['capability'];checks+=1
 svg_count=png_count=0
 catalog=json.loads((root/'english-text-catalog.json').read_text());assert catalog['authoredLocale']=='en-US' and catalog['textDirection']=='ltr';assert len({r['id'] for r in catalog['labels']})==len(catalog['labels']);checks+=2
 declared={t['text'] for s in scenes for t in s['textBoxes']}|{a[1] for d in defs for a in d['actions']};assert declared=={r['text'] for r in catalog['labels']};checks+=1
 for label in declared:assert all(not c.isalpha() or c.isascii() for c in label);checks+=1
 resources=ET.parse(root/'native-text/res/values/strings.xml').getroot();assert {n.get('name') for n in resources}=={r['id'] for r in catalog['labels']} and all(n.get('translatable')=='false' for n in resources);checks+=1
 for f in root.rglob('*.svg'):
  doc=ET.parse(f).getroot();names=[n.get('id') for n in doc.iter() if n.get('id')];assert len(names)==len(set(names)),f;svg_count+=1;checks+=1
  for n in doc.findall('.//{'+SVG+'}image'):
   href=n.get('href','')
   if href and not href.startswith('data:'):target=(f.parent/href).resolve();assert target.is_relative_to(root) and target.is_file(),(f,href);checks+=1
 for f in root.rglob('*.png'):
  with Image.open(f) as im:im.verify()
  png_count+=1;checks+=1
 for source,output in [('test_forge_journeys.cjs','viewer-tests.json'),('state_driver_v2.test.cjs','state-tests.txt')]:
  cmd=[node]+(['--test'] if source.endswith('.test.cjs') else [])+[str(ROOT/'tools'/source)]+([] if source.endswith('.test.cjs') else [str(root)])
  run=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8');assert run.returncode==0,run.stdout+run.stderr;(root/'verification/evidence'/output).write_text(run.stdout+run.stderr,encoding='utf8')
 viewer=json.loads((root/'verification/evidence/viewer-tests.json').read_text());checks+=viewer['checks']
 report={'date':'2026-10-22','components':18,'newComponents':0,'reusedComponents':18,'scenes':len(scenes),'androidScenes':sum(s['group']=='android' for s in scenes),'thorScenes':sum(s['group']=='thor' for s in scenes),'journeyFamilies':len(families),'actionTransitions':actions,'checks':checks,'liveTextBoxesChecked':texts,'textIntersections':0,'svgFiles':svg_count,'pngFiles':png_count,'stateTests':7,'viewerTests':viewer,'v1Scope':'120 additional editable Android/Thor journey state scenes, 18 unchanged layered masters reused. Desktop visual/layout passes recorded. Declared missing-state coverage only; no authentication, capture, hardware service or native UI is implemented.','v2Method':'Explicit target/reachability/consent graph checks; every offline viewer action exercised in Node VM; measured text bounds/intersections and art containment; cold-emission and unavailable/disabled rules; unchanged master/material hashes; SVG reference/ID checks and PNG decode. Existing seven state tests.','browserRender':'NOT RUN','nativeIntegration':'NOT RUN','deviceAcceptance':'NOT RUN','authoredLocale':'en-US','authoredText':'English only; complete approved catalog and native strings.xml provided','nativeImeBehavior':'NOT RUN'}
 (root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--node',required=True);a=p.parse_args();verify(a.root.resolve(),a.node)
