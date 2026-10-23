"""Preserve all current screen/example SVG compositions in the visual handoff."""
from pathlib import Path
import argparse,base64,copy,hashlib,io,json,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import resvg_py,font
from forge_library import xml
ROOT=Path(__file__).resolve().parents[1];NS='{http://www.w3.org/2000/svg}'
GROUPS=[('12-forge-controls-and-screens','screens'),('12-forge-controls-and-screens','examples'),('13-forge-android-and-thor-flows','screens'),('14-forge-atmosphere','scenes'),('15-forge-journey-states','screens')]
def build(root):
 assert not (root/'complete-assets.zip').exists();dest=root/'current-library';out=dest/'compositions';out.mkdir(exist_ok=True);rows=[];thumbs=[];rasters={}
 for folder,sub in GROUPS:
  for original in sorted((ROOT/'iterations'/folder/sub).glob('*.svg')):
   source=ET.parse(original).getroot();doc=copy.deepcopy(source);images=[]
   for image in doc.findall('.//'+NS+'image'):
    href=image.get('href','')
    if href.startswith('#'):continue
    if href.startswith('data:image/png;base64,'):data=base64.b64decode(href.split(',',1)[1],validate=True)
    else:
     p=(original.parent/href).resolve();assert p.is_relative_to(ROOT) and p.suffix=='.png';data=p.read_bytes()
    digest=hashlib.sha256(data).hexdigest();p=dest/'rasters'/f'{digest}.png'
    if p.exists():assert p.read_bytes()==data
    else:p.write_bytes(data)
    rasters[digest]={'path':p.relative_to(root).as_posix(),'sha256':digest,'bytes':len(data)};image.set('href','../rasters/'+digest+'.png');images.append(digest)
   name=folder.split('-')[0]+'__'+sub+'__'+original.stem;p=out/(name+'.svg');p.write_text(xml(doc),encoding='utf8')
   a=list(source.iter());b=list(doc.iter());assert len(a)==len(b)
   for aa,bb in zip(a,b):
    if aa.tag==NS+'image':aa.attrib.pop('href',None);bb=copy.deepcopy(bb);bb.attrib.pop('href',None)
    assert aa.tag==bb.tag and aa.attrib==bb.attrib and aa.text==bb.text
   rows.append({'id':name,'original':original.relative_to(ROOT).as_posix(),'originalSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'portable':p.relative_to(root).as_posix(),'portableSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rasters':images,'role':'Editable review composition with live SVG text and sample state; never a production cold base','nativeIntegrated':False,'deviceVerified':False})
   for image in doc.findall('.//'+NS+'image'):
    href=image.get('href','')
    if href.startswith('../rasters/'):image.set('href','data:image/png;base64,'+base64.b64encode((p.parent/href).read_bytes()).decode())
   w,h=[float(doc.get(k)) for k in ['width','height']];width=max(1,round(min(328/w,310/h)*w));data=resvg_py.svg_to_bytes(svg_string=xml(doc),width=width,skip_system_fonts=True,font_files=['C:/Windows/Fonts/segoeui.ttf'],sans_serif_family='Segoe UI');thumbs.append((name,Image.open(io.BytesIO(data)).convert('RGBA')));print(name,flush=True)
 assert len(rows)==189
 for start in range(0,len(thumbs),12):
  board=Image.new('RGB',(1440,1250),'#080c11');draw=ImageDraw.Draw(board);draw.text((22,15),f'CRAFTAGEDDON / CURRENT COMPOSITIONS / {start//12+1:02}',font=font(28,True),fill='#eee7d9')
  for i,(name,im) in enumerate(thumbs[start:start+12]):
   x=i%4*360;y=80+i//4*390;draw.text((x+8,y),name[:43],font=font(13),fill='#eee7d9');board.paste(im,(x+(360-im.width)//2,y+40+(310-im.height)//2),im)
  board.save(dest/'previews'/f'current-compositions-{start//12+1:02}.png')
 (dest/'compositions.json').write_text(json.dumps({'date':'2026-10-23','compositions':rows,'count':len(rows),'scope':'8 retained compositions, 2 live-label examples, 42 flow concepts, 17 atmosphere states and 120 journey states. These are current visual comparison sources, not installed platform screens.'},indent=2)+'\n')
 index=dest/'index.html';s=index.read_text(encoding='utf8');section='<h2>Current screen and input compositions</h2><p>189 editable review compositions. State lighting and sample text belong to these review views; production cold masters and masks remain separate.</p>'+''.join(f'<figure><img loading="lazy" src="previews/current-compositions-{i:02}.png" alt="Composition sheet {i}"><figcaption>Composition sheet {i} of 16</figcaption></figure>' for i in range(1,17));s=s.replace('</html>',section+'</html>');index.write_text(s,encoding='utf8');print(json.dumps({'portableCompositions':len(rows),'compositionSheets':16,'sharedRasterBytesUnchanged':True}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();build(a.root.resolve())
