"""Verify saved cold material hashes, neutral masks, SVGs and previews."""
from pathlib import Path
import hashlib,json,sys,xml.etree.ElementTree as ET
from PIL import Image
root=Path(sys.argv[1]).resolve();neutral=0
for kind in ['notification','tile']:
 folder=root/'materials'/kind;meta=json.loads((folder/f'{kind}-metadata.json').read_text())
 assert hashlib.sha256((folder/f'{kind}-cold.png').read_bytes()).hexdigest()==meta['coldSha256']
 with Image.open(folder/f'{kind}-cold.png') as im:assert list(im.size)==meta['canvas'] and im.mode=='RGBA' and im.getpixel((0,0))[3]==0
 doc=ET.parse(folder/f'{kind}-master.svg').getroot();ns='{http://www.w3.org/2000/svg}'
 assert not doc.findall('.//'+ns+'text')
 for layer in ['cold','seam','core','symbol']:assert doc.find(ns+f"g[@id='{layer}']") is not None
 for layer in ['seam','core']:
  assert doc.find(ns+f"g[@id='{layer}']").get('style')=='display:none'
  with Image.open(folder/f'{kind}-{layer}.png') as im:
   pixels=[p for p in im.get_flattened_data() if p[3]>0];assert pixels and all(r==g==b==255 for r,g,b,a in pixels);neutral+=1
 assert (folder/f'{kind}-cold.preview.png').read_bytes()!=(folder/f'{kind}-selected.preview.png').read_bytes()
for p in root.rglob('*.svg'):ET.parse(p)
for p in root.rglob('*.png'):
 with Image.open(p) as im:im.verify()
report={'components':2,'screenConcepts':2,'decodedPngs':len(list(root.rglob('*.png'))),'parsedSvgs':len(list(root.rglob('*.svg'))),'nonemptyNeutralMasks':neutral,'unmodifiedColdHashesVerified':2,'nativeIntegrated':False,'deviceVerified':False,'scope':'File validation and desktop visual review; mask alignment is visually authored, not device-qualified.'}
(root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
