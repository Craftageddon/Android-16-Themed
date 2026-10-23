"""Portable current-library sources and contact sheets; preserve every raster byte."""
from pathlib import Path
import argparse,base64,copy,hashlib,io,json,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import resvg_py,font
from forge_library import xml,state,lighting_descriptor
ROOT=Path(__file__).resolve().parents[1];NS='{http://www.w3.org/2000/svg}'
def build(root):
 assert not (root/'complete-assets.zip').exists();dest=root/'current-library';(dest/'masters').mkdir(parents=True,exist_ok=True);(dest/'rasters').mkdir(exist_ok=True);(dest/'previews').mkdir(exist_ok=True)
 catalog=json.loads((root/'canonical-masters.json').read_text());style=json.loads((root/'runtime-style.json').read_text());rows=[];rasters={};metadata={}
 for folder in catalog['sourceDirectories']:
  p=ROOT/'iterations'/folder/'components.json'
  if p.is_file():metadata[folder]={r['id']:r for r in json.loads(p.read_text(encoding='utf8'))}
 cached=[]
 for row in catalog['masters']:
  source=ROOT/row['source'];doc=ET.parse(source).getroot();images=[]
  for n in doc.findall('.//'+NS+'image'):
   href=n.get('href','')
   if href.startswith('#'):continue
   if href.startswith('data:image/png;base64,'):data=base64.b64decode(href.split(',',1)[1],validate=True)
   else:
    p=(source.parent/href).resolve();assert p.is_relative_to(ROOT) and p.suffix=='.png';data=p.read_bytes()
   digest=hashlib.sha256(data).hexdigest();target=dest/'rasters'/f'{digest}.png'
   if target.exists():assert target.read_bytes()==data
   else:target.write_bytes(data)
   rasters[digest]={'path':target.relative_to(root).as_posix(),'sha256':digest,'bytes':len(data)};images.append(digest);n.set('href','../rasters/'+digest+'.png')
  name=row['assetId'].replace('/','__');target=dest/'masters'/f'{name}.svg';target.write_text(xml(doc),encoding='utf8');meta=metadata.get(source.parts[-3],{}).get(source.stem,{});locked=meta.get('emissionLockedOff',False)
  # Keep exact byte provenance and compare all non-image XML geometry.
  original=ET.parse(source).getroot();a=list(original.iter());b=list(doc.iter());assert len(a)==len(b)
  for aa,bb in zip(a,b):
   if aa.tag==NS+'image':aa.attrib.pop('href',None);bb=copy.deepcopy(bb);bb.attrib.pop('href',None)
   assert aa.tag==bb.tag and aa.attrib==bb.attrib and aa.text==bb.text,(name,'Geometry changed')
  item={**row,'portableMaster':target.relative_to(root).as_posix(),'portableSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'rasterSha256':images,'emissionLockedOff':locked};rows.append(item)
  thumbnails=[]
  for st in ['off','on']:
   q=state(doc,lighting_descriptor(style['sampleStates'][st],locked))
   for n in q.findall('.//'+NS+'image'):
    h=n.get('href','')
    if h.startswith('../rasters/'):n.set('href','data:image/png;base64,'+base64.b64encode((target.parent/h).read_bytes()).decode())
   w,h=row['size'];width=round(min(140/w,145/h)*w)
   if row['optical']=='compact':width=24
   png=resvg_py.svg_to_bytes(svg_string=xml(q),width=max(1,width),skip_system_fonts=True);thumbnails.append(Image.open(io.BytesIO(png)).convert('RGBA'))
  cached.append((row,thumbnails));print(name,flush=True)
 for start in range(0,len(cached),24):
  board=Image.new('RGB',(1440,1520),'#080c11');draw=ImageDraw.Draw(board);draw.text((24,15),f'CRAFTAGEDDON / CURRENT MASTER INVENTORY / {start//24+1:02}',font=font(29,True),fill='#eee7d9');draw.text((24,55),'Cold / selected pairs. Compact icons remain 24 px; larger art is fitted for review.',font=font(20),fill='#b5bdc6')
  for i,(row,ims) in enumerate(cached[start:start+24]):
   x=i%4*360;y=100+i//4*234;label=row['assetId'];draw.text((x+12,y),label[:41],font=font(14),fill='#eee7d9')
   for col,im in enumerate(ims):board.paste(im,(x+20+col*175+(140-im.width)//2,y+35+(145-im.height)//2),im)
   draw.text((x+20,y+193),f"{int(row['size'][0])} x {int(row['size'][1])} / {row['optical']}",font=font(15),fill='#b5bdc6')
  board.save(dest/'previews'/f'current-masters-{start//24+1:02}.png')
 (dest/'manifest.json').write_text(json.dumps({'date':'2026-10-23','masters':rows,'rasters':list(rasters.values()),'scope':'472 current production master files; not independent semantic-family count. Geometry and raster bytes preserved; portable image paths only. Historical sources and unchanged copies remain catalogued separately.'},indent=2)+'\n')
 body=''.join(f'<figure><img loading="lazy" src="previews/current-masters-{i:02}.png" alt="Current master sheet {i}"><figcaption>Sheet {i} of 20</figcaption></figure>' for i in range(1,21));(dest/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Craftageddon current visual masters</title><style>body{background:#080c11;color:#eee7d9;font:18px system-ui;margin:24px}img{max-width:100%;height:auto}figure{margin:30px 0}</style><h1>Current visual masters</h1><p>All 472 current source masters, with cold and selected review pairs. Individual portable SVGs are in masters/. Raster bytes are unchanged. Native and physical acceptance are separate.</p>'+body+'</html>',encoding='utf8')
 print(json.dumps({'portableMasters':len(rows),'unchangedSharedRasters':len(rasters),'contactSheets':20}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();build(a.root.resolve())
