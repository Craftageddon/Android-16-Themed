"""Inspect nine-patch metadata, fixed caps, neutral light and Android compile/link."""
from pathlib import Path
import argparse,hashlib,json,subprocess,xml.etree.ElementTree as ET
from PIL import Image
from build_scalable_frames import bounds,stretch,LAYERS,DENSITIES

def validate(im):
 assert im.mode=='RGBA'
 w,h=im.size;corners=[(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
 assert all(im.getpixel(p)==(0,0,0,0) for p in corners),'Corner metadata pixels must be transparent'
 edges=[im.getpixel((x,y)) for x in range(w) for y in [0,h-1]]+[im.getpixel((x,y)) for y in range(h) for x in [0,w-1]]
 assert all(p[3]==0 or p==(0,0,0,255) for p in edges),'Metadata border contains non-black pixels'
 (x0,x1),(y0,y1)=bounds(im);src=im.crop((1,1,w-1,h-1));w,h=src.size
 # Every column/row inside the allowed stretch band must have the same cross-section.
 assert len({src.crop((x,0,x+1,h)).tobytes() for x in range(x0,x1)})==1,'Nonuniform horizontal stretch band'
 assert len({src.crop((0,y,w,y+1)).tobytes() for y in range(y0,y1)})==1,'Nonuniform vertical stretch band'
 assert stretch(im,(w,h)).tobytes()==src.tobytes(),'Identity stretch changed source pixels'
 for tw,th in [(w+137,h),(w,h+83),(w+219,h+127)]:
  result=stretch(im,(tw,th))
  for sb,db in [((0,0,x0,y0),(0,0,x0,y0)),((x1,0,w,y0),(tw-(w-x1),0,tw,y0)),((0,y1,x0,h),(0,th-(h-y1),x0,th)),((x1,y1,w,h),(tw-(w-x1),th-(h-y1),tw,th))]:assert src.crop(sb).tobytes()==result.crop(db).tobytes(),'Fixed corner changed'
 for edge in ['bottom','right']:
  ps=[im.getpixel((i,im.height-1)) for i in range(im.width)] if edge=='bottom' else [im.getpixel((im.width-1,i)) for i in range(im.height)]
  ids=[i for i,p in enumerate(ps) if p==(0,0,0,255)];assert ids and ids==list(range(ids[0],ids[-1]+1)),'Invalid content padding run'
 return src

def verify(a):
 root=a.root.resolve();files=sorted((root/'android/res').rglob('*.9.png'));assert len(files)==80;neutral=0
 for p in files:
  with Image.open(p) as im:
   src=validate(im)
   if any('_'+name+'.9.png' in p.name for name in ['seam','core','focus','symbol']):
    colors=[px for px in src.get_flattened_data() if px[3]>0];assert colors and all(r==g==b==255 for r,g,b,alpha in colors);neutral+=1
   if '_cold.' in p.name:assert not any(r>150 and r>g*1.8 and g>b*1.2 for r,g,b,alpha in src.get_flattened_data() if alpha>64)
 # Mutation checks ensure the validator rejects broken metadata, not merely our builder's filenames.
 bad=Image.open(files[0]).convert('RGBA');bad.putpixel((3,0),(255,0,0,255));rejected=False
 try:validate(bad)
 except AssertionError:rejected=True
 assert rejected
 for p in root.rglob('*.svg'):ET.parse(p)
 for p in root.rglob('*.png'):
  with Image.open(p) as im:im.verify()
 work=a.work.resolve();work.mkdir(parents=True,exist_ok=False);compiled=work/'compiled';compiled.mkdir()
 def run(args):
  p=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert p.returncode==0,f'Compiler exit {p.returncode}: '+p.stdout+p.stderr;return p.stdout+p.stderr
 version=run([a.aapt2,'version']);run([a.aapt2,'compile','--dir',root/'android/res','-o',compiled]);flats=sorted(compiled.glob('*.flat'));assert len(flats)==80
 manifest=work/'AndroidManifest.xml';manifest.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.craftageddon.resourcesmoke"><uses-sdk android:minSdkVersion="26" android:targetSdkVersion="36"/><application android:label="Resource link smoke"/></manifest>')
 run([a.aapt2,'link','--manifest',manifest,'-I',a.android_jar,'-o',work/'resources.ap_',*flats])
 dump=run([a.aapt2,'dump','resources',work/'resources.ap_']);resources=[line for line in dump.splitlines() if 'resource 0x' in line and 'drawable/' in line];assert len(resources)==20
 report={'components':4,'ninePatchLayers':80,'densityVariants':4,'neutralMaskLayers':neutral,'identityStretchesChecked':80,'resizedFixedCornerChecks':960,'nonuniformBandChecks':160,'invalidBorderRejected':True,'parsedSvgs':len(list(root.rglob('*.svg'))),'decodedPngs':len(list(root.rglob('*.png'))),'aapt2Version':version.strip(),'compiledDensityResources':80,'linkedLogicalDrawables':20,'nativeIntegrated':False,'deviceVerified':False,'scope':'Desktop pixel/metadata checks and Android resource compile/link; runtime V3 pending.'}
 report['date']='2026-10-21'
 (root/'verification/evidence/technical.json').write_text(json.dumps(report,indent=2)+'\n');(root/'verification/evidence/resource-table.txt').write_text(dump);print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--work',type=Path,required=True);p.add_argument('--aapt2',type=Path,required=True);p.add_argument('--android-jar',type=Path,required=True);verify(p.parse_args())
