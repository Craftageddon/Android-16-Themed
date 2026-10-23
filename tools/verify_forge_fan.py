"""Check the actual rotor snapshots and neutral production mask exports."""
from pathlib import Path
import argparse,hashlib,json,xml.etree.ElementTree as ET
from PIL import Image,ImageChops,ImageDraw
from forge_library import layer,raster

p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root.resolve();doc=ET.parse(root/'masters/fan_rotor.svg').getroot();ns='{http://www.w3.org/2000/svg}';names=['cold','reflection','spill','seam','core','focus','symbol'];checks=0;out=root/'exports';out.mkdir(exist_ok=True)
for name in names:
 g=doc.find(ns+'g[@id="'+name+'"]');assert g is not None;assert g.find(ns+'g[@data-motion-part="rotor"]') is not None;checks+=2
 if name!='cold':assert g.get('style')=='display:none';checks+=1
 else:assert all(n.get('filter') is None for n in g.iter());checks+=1
 im=raster(layer(doc,name),360,'');im.save(out/f'fan_rotor.{name}.360.png');assert im.getchannel('A').getextrema()[0]==0;checks+=1
 if name!='cold':
  r,g,b,_=im.split();assert not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox();checks+=1
pixels=root/'desktop-frames';cold=Image.open(pixels/'cooling-fan-speed.000.off.png').convert('RGB')
for phase in ['000','012','037','062','100']:assert Image.open(pixels/f'cooling-fan-speed.{phase}.off.png').convert('RGB').tobytes()==cold.tobytes();checks+=1
on0=Image.open(pixels/'cooling-fan-speed.000.on.png').convert('RGB');on37=Image.open(pixels/'cooling-fan-speed.037.on.png').convert('RGB');diff=ImageChops.difference(on0,on37);assert diff.getbbox(),'Rotor does not visibly move';checks+=1
exterior=Image.new('L',on0.size,255);ImageDraw.Draw(exterior).ellipse((296,151,424,279),fill=0);assert not ImageChops.multiply(diff,Image.merge('RGB',(exterior,exterior,exterior))).getbbox(),'Fan housing changed with rotor';checks+=1
assert ImageChops.difference(on37,cold).getbbox(),'Selected mask emission missing';checks+=1
assert not doc.findall('.//'+ns+'text');checks+=1
report={'result':'PASS','checks':checks,'neutralMaskExports':6,'newComponent':'fan_rotor','sourceSha256':hashlib.sha256((root/'masters/fan_rotor.svg').read_bytes()).hexdigest(),'coldFanFramesIdentical':5,'rotorPixelChange':'PASS','stationaryHousingExteriorPixels':'IDENTICAL','nativeIntegration':'NOT RUN','scope':'Actual desktop SVG exports and sampled frames only; physical fan/service, browser rendering and target behavior not verified'};(root/'verification/evidence/fan-component-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
