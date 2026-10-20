"""Independent structural and pixel audit of a generated design checkpoint."""
from pathlib import Path
import hashlib, json, sys
import xml.etree.ElementTree as ET
from PIL import Image

def lum(hexcolor):
 v=[int(hexcolor[i:i+2],16)/255 for i in (1,3,5)]
 v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]
 return .2126*v[0]+.7152*v[1]+.0722*v[2]
def contrast(a,b):
 x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
def verify(root):
 components=json.loads((root/'components.json').read_text());tokens=json.loads((root/'tokens.json').read_text())
 assert len(components)==18 and len({c['id'] for c in components})==18
 checks=[];nonempty_masks=0
 for c in components:
  w,h=c['viewBox'][2:];master=ET.parse(root/'masters'/f"{c['id']}.svg").getroot()
  ns={'s':'http://www.w3.org/2000/svg'}
  assert not master.findall('.//s:text',ns),'live content baked into master'
  for mask in ['seam','core']:
   node=master.find(f"s:g[@id='{mask}']",ns);assert node is not None and node.get('style')=='display:none'
  for layer in ['cold','seam','core','symbol']:
   ET.parse(root/'layers'/f"{c['id']}.{layer}.svg")
   for density in [1,2]:
    p=root/'exports'/f"{c['id']}.{layer}@{density}x.png"
    with Image.open(p) as im:
     im.load();assert im.mode=='RGBA' and im.size==(w*density,h*density),(p,im.size,im.mode)
     alpha=im.getchannel('A');assert alpha.getpixel((0,0))==0,(p,'clipped corner')
     if layer in ['seam','core']:
      pixels=[p for p in im.getdata() if p[3]>0]
      assert all(r==g==b==255 for r,g,b,a in pixels),'mask is not neutral white'
      if pixels:nonempty_masks+=1
     if layer=='cold':
      assert not any(r>160 and r>g*1.8 and g>b*1.2 and a>30 for r,g,b,a in im.getdata()),'emission baked into cold base'
  checks.append(c['id'])
 for p in root.rglob('*.png'):
  with Image.open(p) as im:im.verify()
 cr={k:round(contrast(tokens['colors'][k],tokens['colors']['well']),2) for k in ['text','secondary','focus']}
 assert cr['text']>=7 and cr['secondary']>=4.5 and cr['focus']>=3
 result={'scope':'desktop design checkpoint only','components':checks,'validatedPng':len(list(root.rglob('*.png'))),'nonemptyNeutralMasksAtBothDensities':nonempty_masks,'contrastOnWell':cr,'hardware':'NOT RUN','InkscapeGUI':'NOT RUN','nativeIntegration':'NOT RUN'}
 (root/'verification/evidence/technical.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result))
 return result
if __name__=='__main__':verify(Path(sys.argv[1]).resolve())
