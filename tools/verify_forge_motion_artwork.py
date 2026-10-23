"""Check the current motion artwork graph, actual text poses and neutral exports.
This is offline source/render evidence, not browser or target acceptance.
"""
from pathlib import Path
import argparse,base64,hashlib,io,json,math,re,xml.etree.ElementTree as ET
from PIL import Image,ImageChops
from build_pilot import resvg_py,font
from forge_library import layer,xml,embed
NS='{http://www.w3.org/2000/svg}'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
def mul(a,b):
 return (a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5])
def matrix(value):
 m=(1,0,0,1,0,0)
 for name,args in re.findall(r'(translate|scale|rotate|matrix)\(([^)]*)\)',value):
  v=[float(x) for x in re.split(r'[ ,]+',args.strip())]
  if name=='translate':n=(1,0,0,1,v[0],v[1] if len(v)>1 else 0)
  elif name=='scale':n=(v[0],0,0,v[-1],0,0)
  elif name=='matrix':n=tuple(v)
  else:
   t=math.radians(v[0]);n=(math.cos(t),math.sin(t),-math.sin(t),math.cos(t),0,0)
   if len(v)==3:n=mul(mul((1,0,0,1,v[1],v[2]),n),(1,0,0,1,-v[1],-v[2]))
  m=mul(m,n)
 return m
def point(m,x,y):return (m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5])
def text_poses(doc):
 rows=[]
 def walk(n,m=(1,0,0,1,0,0),alpha=1):
  m=mul(m,matrix(n.get('transform','')));alpha*=float(n.get('opacity',1))
  if n.tag==NS+'text' and n.text and alpha>.01:
   size=float(n.get('font-size',16));f=font(max(1,round(size)));w=f.getlength(n.text);x=float(n.get('x',0));y=float(n.get('y',0))
   # Font-independent conservative baseline box, transformed through its owner.
   pts=[point(m,x+dx,y+dy) for dx in [-w/2,w/2] for dy in [-size,size*.25]]
   rows.append({'text':n.text,'box':[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)],'fontPixels':size*math.hypot(m[0],m[1])})
  for child in n:walk(child,m,alpha)
 walk(doc);return rows
def check(root,export=False):
 errors=[];counts={'masters':0,'layerExports':0,'neutralMasks':0,'frames':0,'textPoses':0,'partTargets':0};repo=Path(__file__).resolve().parents[1]
 def require(condition,detail):
  if not condition:errors.append(detail)
 provenance=json.loads((root/'source/asset-provenance.json').read_text(encoding='utf8'))
 for r in provenance['masters']:
  data=(repo/r['source']).read_bytes();require(hashlib.sha256(data).hexdigest()==r['sha256'],'source hash '+r['source']);require((root/r['originalCopy']).read_bytes()==data,'original copy '+r['source'])
 for row in json.loads((root/'source/portable-source-manifest.json').read_text(encoding='utf8'))['masters']:
  p=root/row['portableCopy'];require(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'portable source hash '+str(p))
  a=ET.parse(repo/row['original']).getroot();b=ET.parse(p).getroot()
  aa=list(a.iter());bb=list(b.iter());require(len(aa)==len(bb),'portable node count '+str(p))
  for original,portable in zip(aa,bb):
   if portable.tag==NS+'image':
    href=portable.get('href','')
    if not href.startswith(('data:','#')):
     target=(p.parent/href).resolve();require(target.is_relative_to(root/'source/rasters') and target.is_file(),'portable raster '+href)
    original.attrib.pop('href',None);portable.attrib.pop('href',None)
   require(original.tag==portable.tag and original.attrib==portable.attrib and original.text==portable.text,'portable geometry changed '+str(p))
 layer_proof=json.loads((root/'verification/evidence/motion-layer-export-checks.json').read_text(encoding='utf8'))
 for name,digest in {**layer_proof['sourceSha256'],**layer_proof['exportSha256']}.items():
  require(hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,'layer export evidence changed '+name)
 for p in root.joinpath('masters').glob('*.svg'):
  doc=ET.parse(p).getroot();counts['masters']+=1;ids=[n.get('id') for n in doc.iter() if n.get('id')];require(len(ids)==len(set(ids)),'duplicate master ID '+p.name);require(not doc.findall('.//'+NS+'text'),'baked text '+p.name)
  for name in LAYERS:
   g=doc.find(NS+'g[@id="'+name+'"]');require(g is not None,'missing layer '+p.name+' '+name)
   if g is None:continue
   if name!='cold':require(g.get('style')=='display:none','mask visible by default '+p.name+' '+name)
   else:require(all(n.get('filter') is None for n in g.iter()),'cold filter '+p.name)
   if export:
    data=(root/'source/steel-material.png').read_bytes();q=embed(layer(doc,name),base64.b64encode(data).decode());width=round(float(doc.get('viewBox').split()[2]))
    for scale in [1,2]:
     im=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(q),width=width*scale,skip_system_fonts=True))).convert('RGBA');target=root/'exports'/f'{p.stem}.{name}@{scale}x.png';target.parent.mkdir(exist_ok=True);im.save(target);counts['layerExports']+=1;require(im.getchannel('A').getextrema()[0]==0,'opaque export '+target.name)
     if name!='cold':
      r,g,b,a=im.split();require(not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox(),'non-neutral mask '+target.name);counts['neutralMasks']+=1
 for row in json.loads((root/'reconciliation.json').read_text(encoding='utf8')):
  for l in row['newLayers']:
   doc=ET.parse(repo/l['source']).getroot()
   for p in l.get('motionParts',[]):
    require(any(n.get('data-motion-part')==p['part'] for n in doc.iter()),'missing part '+row['id']+' '+p['part']);counts['partTargets']+=1
 values=json.loads((root/'verification/evidence/desktop-frame-values.json').read_text(encoding='utf8'))['frames']
 for r in values:
  key=f"{r['id']}.{int(r['phase']*100):03}.{'on' if r['on'] else 'off'}";p=root/'desktop-frames'/f'{key}.svg';require(p.is_file(),'missing frame '+key)
  if not p.is_file():continue
  doc=ET.parse(p).getroot();ids=[n.get('id') for n in doc.iter() if n.get('id')];require(len(ids)==len(set(ids)),'duplicate frame ID '+key);counts['frames']+=1
  for label in text_poses(doc):
   counts['textPoses']+=1;text=label['text'];require(all(not c.isalpha() or c.isascii() for c in text),'non-English script '+key+' '+text);b=label['box'];require(b[0]>=0 and b[1]>=0 and b[2]<=720 and b[3]<=460,'text outside stage '+key+' '+text+' '+str([round(v,1) for v in b]));require(label['fontPixels']>=13.9,'small label '+key+' '+text)
 report={'result':'FAIL' if errors else 'PASS','date':'2026-10-23','counts':counts,'errors':errors,'authoredLocale':'en-US','method':'Parse actual SVG sources and transformed live text; verify byte provenance; render transparent neutral layers at 1x/2x when requested','limits':'No browser, native, device, service or physical control acceptance'}
 (root/'verification/evidence/motion-artwork-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--export',action='store_true');a=p.parse_args();r=check(a.root.resolve(),a.export);raise SystemExit(0 if r['result']=='PASS' else 1)
