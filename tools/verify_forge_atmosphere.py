"""Verify atmosphere sources, transparent masks, static states and composition labels."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,xml.etree.ElementTree as ET
from PIL import Image,ImageChops,ImageStat
from build_pilot import SVG,font
from forge_library import compose_layers,lighting_descriptor

def verify(root,node):
 rows=json.loads((root/'components.json').read_text());walls=json.loads((root/'wallpapers.json').read_text());scenes=json.loads((root/'scenes.json').read_text());states=json.loads((root/'runtime-style.json').read_text())['sampleStates'];checks=0;neutral=0;composites=0;texts=0
 assert len(rows)==3 and len(walls)==6 and len(scenes)==17;checks+=3
 for src in json.loads((root/'source/provenance.json').read_text())['inputs']:
  assert hashlib.sha256((root/'source'/src['file']).read_bytes()).hexdigest()==src['sha256'];checks+=1
 for row in rows:
  key=row['id'];doc=ET.parse(root/'masters'/f'{key}.svg').getroot();assert not doc.findall('.//{'+SVG+'}text');checks+=1
  for size in row['exportWidths']:
   layers={k:Image.open(root/'exports'/f'{key}.{k}.{size}.png').convert('RGBA') for k in row['layers']}
   for k,im in layers.items():
    assert im.getchannel('A').getextrema()[0]==0;checks+=1
    if k!='cold':
     r,g,b,_=im.split();assert not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox();neutral+=1;checks+=1
   if size==row['exportWidths'][-1]:
    if key=='charge_chamber':
     crop=layers['cold'].crop((size*.25,size*.25,size*.75,size*.75)).convert('L');assert ImageStat.Stat(crop).stddev[0]>10,'Sculpted material did not render';checks+=1
    for st,desc in states.items():
     expected=compose_layers(layers,lighting_descriptor(desc));actual=Image.open(root/'exports'/f'{key}.{st}.preview.png').convert('RGBA');assert expected.tobytes()==actual.tobytes();composites+=1;checks+=1
    for st in ['off','hovered']:assert Image.open(root/'exports'/f'{key}.{st}.preview.png').convert('RGBA').tobytes()==layers['cold'].tobytes();checks+=1
 for row in walls:
  key=row['id'];w,h=row['size'];layers={k:Image.open(root/'exports'/f'{key}.{k}.{w}.png').convert('RGBA') for k in ['cold','reflection','spill','seam','core','focus','symbol']}
  assert layers['cold'].size==(w,h) and layers['cold'].getchannel('A').getextrema()==(255,255);checks+=1
  for k,im in layers.items():
   if k!='cold':
    r,g,b,_=im.split();assert not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox();neutral+=1;checks+=1
  for st in ['off','on','reduced']:
   actual=Image.open(root/'previews'/f'{key}.{st}.preview.png').convert('RGBA');assert actual.tobytes()==compose_layers(layers,states[st]).tobytes();composites+=1;checks+=1
  assert Image.open(root/'previews'/f'{key}.off.preview.png').convert('RGBA').tobytes()==layers['cold'].tobytes();checks+=1
  # The declared reading region remains a uniform dark quiet well, independent of state.
  x,y,ww,hh=row['readingRegionNormalized'];box=(round(x*w),round(y*h),round((x+ww)*w),round((y+hh)*h));alpha=layers['seam'].getchannel('A').crop(box);assert alpha.getextrema()[1]==0,(key,'emission in declared reading region');checks+=1
 for s in scenes:
  doc=ET.parse(root/'scenes'/f"{s['id']}.svg").getroot();w,h=s['size'];assert s['fixtureOnly'] and not s['nativeIntegrated'];checks+=1
  boxes=[]
  for n in doc.findall('.//{'+SVG+'}text'):
   label=n.text or '';x=float(n.get('x'));y=float(n.get('y'));size=int(n.get('font-size'));width=font(size,n.get('font-weight')=='700').getlength(label);left=x-width/2 if n.get('text-anchor')=='middle' else x
   assert 15<=left and left+width<=w-15 and 0<y-size and y+5<h,(s['id'],label);boxes.append((left,y-size,width,size+5,label));texts+=1;checks+=1
  for i,(x,y,ww,hh,label) in enumerate(boxes):
   for xx,yy,bw,bh,other in boxes[i+1:]:assert min(x+ww,xx+bw)-max(x,xx)<=1 or min(y+hh,yy+bh)-max(y,yy)<=1,(s['id'],label,other)
  checks+=1
  if s['id']=='recovery-menu':assert {'Reboot system','Apply update','Factory reset','Advanced'}<={n.text for n in doc.findall('.//{'+SVG+'}text')};checks+=1
 svg_count=0;png_count=0
 for f in root.rglob('*.svg'):
  doc=ET.parse(f).getroot();ids=[n.get('id') for n in doc.iter() if n.get('id')];assert len(ids)==len(set(ids)),f;svg_count+=1;checks+=1
  for n in doc.findall('.//{'+SVG+'}image'):
   href=n.get('href','')
   if href and not href.startswith('data:'):target=(f.parent/href).resolve();assert target.is_relative_to(root) and target.is_file();checks+=1
 for f in root.rglob('*.png'):
  with Image.open(f) as im:im.verify()
  png_count+=1;checks+=1
 gallery=(root/'index.html').read_text();assert gallery.count('<article>')==23;checks+=1
 for href in re.findall(r'(?:href|src)="([^"]+)"',gallery):assert (root/href).is_file();checks+=1
 p=subprocess.run([node,'--test','tools/state_driver_v2.test.cjs'],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True);assert p.returncode==0;pfile=root/'verification/evidence/state-tests.txt';pfile.write_text(p.stdout+p.stderr)
 report={'date':'2026-10-22','components':3,'wallpapers':6,'sceneConcepts':17,'checks':checks,'neutralMasks':neutral,'exactStateComposites':composites,'liveTextLabels':texts,'svgFiles':svg_count,'pngFiles':png_count,'stateTests':7,'v1Scope':'Six layered wallpaper surfaces and 17 editable boot/charging/recovery/loading concept scenes using three atmosphere components; cold bases and unchanged sculpted core preserved. Remaining motion/state/native scope is explicit.','v2Method':'Source hashes, SVG/PNG decode, unique IDs and local image links, true component alpha, neutral mask equality, exact state recomposition, cold/off/hover identity, wallpaper reading-region seam exclusion, text bounds/intersections, required recovery actions, gallery references and seven cold-off state tests.','deviceTests':'NOT RUN','nativeIntegration':'NOT RUN','fullVisualRoadmap':'INCOMPLETE: motion, extended flow states, app-specific/historical reconciliation and target review remain.'}
 (root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--node',required=True);a=p.parse_args();verify(a.root.resolve(),a.node)
