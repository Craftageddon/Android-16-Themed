"""Independent SVG and pixel checks for variable-value motion controls."""
from pathlib import Path
import argparse,json,hashlib,math,xml.etree.ElementTree as ET
from PIL import Image,ImageChops,ImageDraw
from forge_library import layer,raster
from build_pilot import font
from verify_forge_motion_artwork import text_poses
NS='{http://www.w3.org/2000/svg}'
def check(root):
 names=['cold','reflection','spill','seam','core','focus','symbol'];checks=neutral=exports=0
 for key in ['charge_vessel','progress_vessel','slider_rail','eq_band']:
  p=root/'masters'/f'{key}.svg';doc=ET.parse(p).getroot();w=int(float(doc.get('viewBox').split()[2]))
  assert not doc.findall('.//'+NS+'text');checks+=1
  for name in names:
   g=doc.find(NS+'g[@id="'+name+'"]');assert g is not None;checks+=1
   if name!='cold':assert g.get('style')=='display:none';checks+=1
   else:assert all(n.get('filter') is None for n in g.iter());checks+=1
   for width in [w,w*2]:
    im=raster(layer(doc,name),width,'');im.save(root/'exports'/f'{key}.{name}.{width}.png');assert im.getchannel('A').getextrema()[0]==0;checks+=1;exports+=1
    if name!='cold':
     r,g,b,_=im.split();assert not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox();checks+=1;neutral+=1
 rows=json.loads((root/'reconciliation.json').read_text(encoding='utf8'));rows={r['id']:r for r in rows}
 for key in ['battery-charging','low-battery-warning','progress-notification','brightness-slider','volume-slider','charging-direct-power','five-band-eq-preset']:
  r=rows[key];assert not r['pendingArtwork']
  for part in r['newLayers']:
   doc=ET.parse(Path.cwd()/part['source']).getroot()
   for op in part.get('motionParts',[]):assert any(n.get('data-motion-part')==op['part'] for n in doc.iter());checks+=1
  for phase in [0,25,50,75,100]:
   doc=ET.parse(root/'desktop-frames'/f'{key}.{phase:03}.on.svg').getroot();ids=[n.get('id') for n in doc.iter() if n.get('id')];assert len(ids)==len(set(ids));checks+=1
   for pose in text_poses(doc):
    text=pose['text'];assert all(not c.isalpha() or c.isascii() for c in text);assert not ('200%' in text or '-100%' in text);checks+=1
    x,y,xx,yy=pose['box'];assert x>=0 and xx<=720 and y>=0 and yy<460,(key,text,pose['box']);checks+=1

  on=Image.open(root/'desktop-frames'/f'{key}.100.on.png').convert('RGB');off=Image.open(root/'desktop-frames'/f'{key}.100.off.png').convert('RGB')
  assert ImageChops.difference(on,off).getbbox(),(key,'No selected mask emission');checks+=1
 for key,label,height,y in [('battery-charging','68%',122.4,121.6),('low-battery-warning','15%',27,217)]:
  doc=ET.parse(root/'desktop-frames'/f'{key}.100.on.svg').getroot();window=next(n for n in doc.iter() if n.get('data-motion-part')=='fill-window');assert abs(float(window.get('height'))-height)<.00001 and abs(float(window.get('y'))-y)<.00001;assert label in {n.text for n in doc.findall('.//'+NS+'text')};checks+=2
 # Check fixed vessels outside the actual variable-value well, independently of metadata.
 for key,box in [('battery-charging',(322,138,398,300)),('progress-notification',(222,208,498,240))]:
  a=Image.open(root/'desktop-frames'/f'{key}.000.off.png').convert('RGB');b=Image.open(root/'desktop-frames'/f'{key}.100.off.png').convert('RGB');diff=ImageChops.difference(a,b);assert diff.getbbox(),(key,'Fill did not move')
  mask=Image.new('L',a.size,255);pen=ImageDraw.Draw(mask);pen.rectangle(box,fill=0)
  for phase in ['000','100']:
   for pose in text_poses(ET.parse(root/'desktop-frames'/f'{key}.{phase}.off.svg').getroot()):
    x,y,xx,yy=pose['box'];pen.rectangle((math.floor(x)-1,math.floor(y)-1,math.ceil(xx)+1,math.ceil(yy)+1),fill=0)
  assert not ImageChops.multiply(diff,Image.merge('RGB',(mask,mask,mask))).getbbox(),(key,'Fixed vessel changed');checks+=2
 eq=ET.parse(root/'desktop-frames/five-band-eq-preset.100.on.svg').getroot();positions={n.get('transform') for n in eq.iter() if n.get('data-motion-part')=='thumb'};assert len(positions)==5;checks+=1
 report={'result':'PASS','date':'2026-10-23','newValueComponents':4,'productionLayerExports':exports,'neutralMasksChecked':neutral,'checks':checks,'fixedBatteryAndProgressVessels':'Pixel-identical outside their value wells and changing live readouts','percentageBounds':'68 and 15 percent checked against actual exported SVG geometry','eqTargets':'Five distinct thumb positions in the exported SVG','authoredLocale':'en-US','nativeIntegration':'NOT RUN','browserAcceptance':'NOT RUN','scope':'Unlabelled vector sources, true-alpha neutral masks and actual desktop sampler exports; not device or hardware behavior'}
 (root/'verification/evidence/value-component-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();check(a.root.resolve())
