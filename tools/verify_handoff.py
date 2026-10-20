"""Audit hero masks, linked SVG screen assets and the native handoff resources."""
from pathlib import Path
import hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
from PIL import Image

root=Path(sys.argv[1]).resolve();out=root/'iterations/03-thor-compositions';ns='{http://www.w3.org/2000/svg}'
heroes=[]
for kind in ['primary','ring']:
 with Image.open(out/'hero'/f'{kind}-cold.png') as im:
  assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
  pixels=[p for p in im.get_flattened_data() if p[3]>64]
  assert not any(r>180 and r>g*1.8 and g>b*1.2 for r,g,b,a in pixels),'warm emission in cold material'
  dimensions=im.size
 for layer in ['seam','core']:
  with Image.open(out/'hero'/f'{kind}-{layer}.png') as im:
   assert im.size==dimensions and im.mode=='RGBA'
   opaque=[p for p in im.get_flattened_data() if p[3]>0]
   assert opaque and all(r==g==b==255 for r,g,b,a in opaque)
 if kind=='ring':
  with Image.open(out/'hero/ring-cold.png') as im:assert im.getpixel((im.width//2,im.height//2))[3]==0,'center hole is not transparent'
 heroes.append({'kind':kind,'dimensions':dimensions,'alphaAndNeutralMasks':'PASS','coldEmissionAudit':'PASS'})
screens=[]
for p in sorted((out/'screens').glob('*.svg')):
 doc=ET.parse(p).getroot();texts=doc.findall('.//'+ns+'text');assert texts,'screen has no live text'
 for image in doc.findall('.//'+ns+'image'):
  href=image.attrib['href'];assert not href.startswith(('http','data:')),'screen source must use local bundled images'
  target=(p.parent/href).resolve();target.relative_to(out);assert target.is_file(),href
 screens.append({'file':p.name,'liveTextNodes':len(texts),'linkedImages':'resolved'})
assert len(screens)==6
for p in (root/'native-handoff/res').rglob('*.xml'):ET.parse(p)
result={'heroChecks':heroes,'screens':screens,'androidResourceSyntax':'XML parsed; see aapt2.json for actual compiler result','physicalTarget':'NOT RUN'}
(out/'verification/evidence/handoff.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
