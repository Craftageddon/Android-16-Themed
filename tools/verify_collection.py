"""File/pixel checks for expanded design collections; no target-device inference."""
from pathlib import Path
import argparse,csv,hashlib,json,xml.etree.ElementTree as ET
from PIL import Image
from verify_pilot import contrast
def verify(root):
 rows=json.loads((root/'components.json').read_text());assert len({r['id'] for r in rows})==len(rows)
 count=0;neutral=0;ns='{http://www.w3.org/2000/svg}'
 for r in rows:
  w,h=r.get('size',r.get('viewBox',[0,0,0,0])[2:]);doc=ET.parse(root/'masters'/f"{r['id']}.svg").getroot();assert not doc.findall('.//'+ns+'text')
  for layer in ['cold','seam','core','symbol']:
   node=doc.find(ns+f"g[@id='{layer}']");assert node is not None
   if layer in ['seam','core']:assert node.get('style')=='display:none'
   for d in [1,2]:
    p=root/'exports'/f"{r['id']}.{layer}@{d}x.png"
    with Image.open(p) as im:
     im.load();assert im.mode=='RGBA' and im.size==(w*d,h*d);assert im.getpixel((0,0))[3]==0
     pixels=[px for px in im.get_flattened_data() if px[3]>32]
     if layer in ['seam','core']:assert all(a==b==c==255 for a,b,c,alpha in pixels);neutral+=bool(pixels)
     if layer=='cold':assert not any(a>160 and a>b*1.8 and b>c*1.2 for a,b,c,alpha in pixels)
    count+=1
 for p in root.rglob('*.svg'):ET.parse(p)
 for p in root.rglob('*.png'):
  with Image.open(p) as im:im.verify()
 tokens=json.loads((root/'tokens.json').read_text());ratios={k:round(contrast(tokens['colors'][k],tokens['colors']['well']),2) for k in ['text','secondary','focus']};assert min(ratios.values())>4.5
 report={'components':len(rows),'auditedLayerPngs':count,'decodedPngs':len(list(root.rglob('*.png'))),'parsedSvgs':len(list(root.rglob('*.svg'))),'nonemptyNeutralMaskExports':neutral,'paletteContrast':ratios,'nativeIntegrated':False,'deviceVerified':False,'scope':'Desktop file and pixel validation only'}
 if (root/'android/res/drawable').exists():
  groups={'battery':[f'battery_{i}' for i in range(0,101,10)],'wifi':[f'wifi_{i}' for i in range(5)]};distinct={}
  for group,names in groups.items():
   fingerprints=[]
   for name in names:
    with Image.open(root/'exports'/f'{name}__compact.idle.preview.png') as im:fingerprints.append(hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest())
   assert len(set(fingerprints))==len(names),'Visually identical state levels in '+group
   distinct[group]=len(names)
  report['distinctRenderedStateLevels']=distinct
 source=root/'source-register/scope-summary.json'
 if source.exists():
  scope=json.loads(source.read_text());assert scope['validDistinctFiles']==3422 and scope['invalidExcluded']==1 and scope['roadmapRows']==103
  report['sourceRegister']=scope
 (root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();verify(a.root.resolve())
