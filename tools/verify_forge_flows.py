"""Bounded source, geometry, lighting, gallery and export verification for pass 13."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,xml.etree.ElementTree as ET
from PIL import Image,ImageChops,ImageDraw
from build_pilot import SVG,font
from build_reference_forge import LAYERS
from forge_library import compose_layers,lighting_descriptor

def verify(root,node):
 checks=0;neutral=0;composites=0;text_count=0;collisions=[]
 rows=json.loads((root/'components.json').read_text());scenes=json.loads((root/'screens/layout-metadata.json').read_text());style=json.loads((root/'runtime-style.json').read_text())
 assert len(rows)==18 and len({r['id'] for r in rows})==18;assert len({r['id'] for r in scenes})==len(scenes);checks+=3
 for source in json.loads((root/'source/material-provenance.json').read_text())['inputs']:
  assert hashlib.sha256((root/'source'/source['file']).read_bytes()).hexdigest()==source['sha256'];checks+=1
 for row in rows:
  key=row['id'];doc=ET.parse(root/'masters'/f'{key}.svg').getroot();assert not doc.findall('.//{'+SVG+'}text');checks+=1
  if key=='unavailable':
   assert row['emissionLockedOff'] and all(lighting_descriptor(d,True)['gains'][k]==0 for d in style['sampleStates'].values() for k in ['reflection','spill','seam','core']);checks+=1
  for name in LAYERS:
   g=doc.find('{'+SVG+'}g[@id="'+name+'"]');assert g is not None
   if name!='cold':assert g.get('style')=='display:none'
   else:assert all(n.get('filter') is None for n in g.iter())
   checks+=1
  for width in row['exportWidths']:
   layers={k:Image.open(root/'exports'/f'{key}.{k}.{width}.png').convert('RGBA') for k in LAYERS};assert layers['cold'].width==width;checks+=1
   for name,im in layers.items():
    assert im.getchannel('A').getextrema()[0]==0
    if name!='cold':
     rr,gg,bb,_=im.split();assert not ImageChops.difference(rr,gg).getbbox();assert not ImageChops.difference(gg,bb).getbbox();neutral+=1
    checks+=1
   if width==row['exportWidths'][-1]:
    for st,desc in style['sampleStates'].items():
     actual=Image.open(root/'exports'/f'{key}.{st}.preview.png').convert('RGBA');expected=compose_layers(layers,lighting_descriptor(desc,row['emissionLockedOff']));assert actual.tobytes()==expected.tobytes(),(key,st);composites+=1;checks+=1
    for st in ['off','hovered']:
     assert Image.open(root/'exports'/f'{key}.{st}.preview.png').convert('RGBA').tobytes()==layers['cold'].tobytes();checks+=1
 # Original control comparison, using actual exported layers/previews.
 board=Image.new('RGB',(1920,2180),'#080c11');d=ImageDraw.Draw(board)
 d.text((30,20),'REFERENCE FORGE 13 / NEW CONTROL ARTWORK',font=font(32,True),fill='#eee7d9');d.text((30,72),'Cold above / selected-on below / unlabelled production masters and neutral masks',font=font(21),fill='#b5bdc6')
 for i,row in enumerate(rows):
  x=20+i%6*316;y=130+i//6*675;d.text((x+10,y),row['id'].replace('_',' ').title(),font=font(19,True),fill='#eee7d9')
  for st,yy in [('off',y+45),('on',y+345)]:
   im=Image.open(root/'exports'/f"{row['id']}.{st}.preview.png").convert('RGBA');im.thumbnail((288,265),Image.Resampling.LANCZOS);board.paste(im,(x+(296-im.width)//2,yy+(275-im.height)//2),im)
 board.save(root/'previews/new-component-states.png')
 for scene in scenes:
  key=scene['id'];w,h=scene['logicalSize'];assert scene['fixtureOnly'] and not scene['nativeIntegrated'] and not scene['deviceVerified'];assert not scene['measuredDeviceGeometry'];checks+=2
  for text in scene['textBoxes']:
   x,y,ww,hh=text['bounds'];assert 12<=x and x+ww<=w-12+.01 and 0<=y and y+hh<h,(key,text);text_count+=1;checks+=1
  # Text-to-text intersections, with 1px tolerance for metric rounding.
  for i,a in enumerate(scene['textBoxes']):
   x,y,ww,hh=a['bounds']
   for b in scene['textBoxes'][i+1:]:
    xx,yy,bw,bh=b['bounds']
    if min(x+ww,xx+bw)-max(x,xx)>1 and min(y+hh,yy+bh)-max(y,yy)>1:collisions.append([key,a['text'],b['text']])
  for item in scene['artworkOwners']:
   x,y,ww,hh=item['bounds'];assert 0<=x and 0<=y and x+ww<=w and y+hh<=h;assert item['state'] in style['sampleStates'];checks+=2
  doc=ET.parse(root/'screens'/f'{key}.svg').getroot();cold=ET.parse(root/'inspections'/f'{key}.cold-material.svg').getroot()
  assert doc.findall('.//{'+SVG+'}text');assert sum(n.get('data-forge-layer')=='cold' for n in doc.iter())==len(scene['artworkOwners']);checks+=2
  for n in cold.iter():
   if n.get('data-forge-layer') in ['reflection','spill','seam','core']:assert n.get('opacity')=='0';checks+=1
  for n in doc.iter():
   if n.get('data-state') in ['off','hovered','focused_off']:
    for g in n.findall('{'+SVG+'}g'):
     if g.get('data-forge-layer') in ['reflection','spill','seam','core']:assert g.get('opacity')=='0';checks+=1
  if key=='thor-controls-unavailable':
   assert all(i['state'] in ['off','disabled'] for i in scene['artworkOwners']);checks+=1
  if key in ['lock-pin','keyboard-numbers']:
   labels={n['text'] for n in scene['textBoxes']};assert set('0123456789')<=labels and '⌫' in labels;checks+=2
  if key=='input-prompts':
   assert {'Up','Up-right','Right','Down-right','Down','Down-left','Left','Up-left','Tap','Hold','Chord','Capture'}<={n['text'] for n in scene['textBoxes']};checks+=1
  if scene['group']=='thor':assert scene['capability'] is not None or key=='input-prompts';checks+=1
 assert not collisions,collisions
 svg_count=0
 for file in root.rglob('*.svg'):
  doc=ET.parse(file).getroot();ids=[n.get('id') for n in doc.iter() if n.get('id')];assert len(ids)==len(set(ids)),file;checks+=1;svg_count+=1
  for n in doc.findall('.//{'+SVG+'}image'):
   href=n.get('href','')
   if href and not href.startswith('data:'):
    target=(file.parent/href).resolve();assert target.is_relative_to(root) and target.is_file(),(file,href);checks+=1
 png_count=0
 for file in root.rglob('*.png'):
  with Image.open(file) as im:im.verify()
  png_count+=1;checks+=1
 gallery=(root/'index.html').read_text(encoding='utf8');assert gallery.count('<article ')==len(scenes);checks+=1
 for href in re.findall(r'(?:src|href)="([^"]+)"',gallery):assert (root/href).is_file();checks+=1
 tests=subprocess.run([node,'--test','tools/state_driver_v2.test.cjs'],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,encoding='utf8');assert tests.returncode==0,tests.stdout+tests.stderr
 (root/'verification/evidence/state-tests.txt').write_text(tests.stdout+tests.stderr,encoding='utf8')
 gallery_test=subprocess.run([node,'tools/test_forge_gallery.cjs',str(root)],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,encoding='utf8');assert gallery_test.returncode==0,gallery_test.stdout+gallery_test.stderr
 gallery_report=json.loads(gallery_test.stdout);checks+=gallery_report['checks'];(root/'verification/evidence/gallery-tests.json').write_text(json.dumps(gallery_report,indent=2)+'\n')
 report={'date':'2026-10-21','components':len(rows),'scenes':len(scenes),'androidScenes':sum(s['group']=='android' for s in scenes),'thorScenes':sum(s['group']=='thor' for s in scenes),'checks':checks,'neutralMasksChecked':neutral,'stateCompositesChecked':composites,'liveTextBoxesChecked':text_count,'textIntersections':collisions,'svgFiles':svg_count,'pngFiles':png_count,'stateTests':7,'v1Scope':'18 new unlabelled layered controls and '+str(len(scenes))+' editable Android/Thor concept scenes reviewed against cold-off/separate-emission requirements. Sample capability fixtures explicit. Remaining states recorded. Exploratory art checkpoint, not complete device coverage.','v2Method':'SVG/XML parsing, measured text containment and text intersection checks, neutral-mask pixel identity, exact exported state recomposition and off/hover identity, layer/scene state inspection, source hash checks, PNG decode, local gallery reference validation, existing seven state resolver tests. No target runtime, browser interaction, native compilation or performance test claimed.','nativeIntegration':'NOT RUN','targetDevice':'NOT RUN','browserInteraction':'NOT RUN','fontMetrics':'Windows Segoe UI at logical design sizes; device scaling/localization pending'}
 report['galleryFilterScenarios']=gallery_report['scenarios'];report['browserAttempt']='In-app browser could not reach Windows loopback URL (connection timed out); no browser rendering/interaction pass claimed. Gallery script tested independently in Node VM.'
 (root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--node',required=True);a=p.parse_args();verify(a.root.resolve(),a.node)
