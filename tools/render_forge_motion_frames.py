"""Render explicit motion-sampler frames using retained cold/mask SVG sources."""
from pathlib import Path
import argparse,base64,hashlib,json,re,copy,io,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from forge_library import state,unique,xml,raster
from build_pilot import el,add,font,resvg_py

def build(out,only=None,shard=None):
 payload=json.loads(re.search(r'<script id="motion-data" type="application/json">(.*?)</script>',(out/'index.html').read_text(encoding='utf8'),re.S)[1]);rows=json.loads((out/'verification/evidence/desktop-frame-values.json').read_text(encoding='utf8'))['frames'];byid={r['id']:r for r in payload['recipes']};(out/'desktop-frames').mkdir(exist_ok=True);(out/'previews').mkdir(exist_ok=True)
 if only:rows=[r for r in rows if r['id'] in only]
 if shard:
  index,count=map(int,shard.split('/'));assert 0<=index<count;chosen=[r for i,r in enumerate(byid) if i%count==index];rows=[r for r in rows if r['id'] in chosen]
 for row in rows:
  recipe=byid[row['id']];root=el('svg',width=720,height=460,viewBox='0 0 720 460');add(root,'rect',width=720,height=460,fill='#10151b')
  for i,(layer,t) in enumerate(zip(recipe['layers'],row['frame']['layers'])):
   a=payload['assets'][layer['source']];r=ET.fromstring(a['markup']);w,h=a['width'],a['height']
   for op in t.get('partMutations',[]):
    targets=[n for n in r.iter() if n.get('data-motion-part')==op['part']];assert targets,op['part']
    parents={child:parent for parent in r.iter() for child in parent}
    for n in targets:
     if op.get('layers'):
      owner=n
      while owner is not None and not owner.get('data-forge-layer'):owner=parents.get(owner)
      if owner is None or owner.get('data-forge-layer') not in op['layers']:continue
     for name,value in op['attrs'].items():n.set(name,str(value))
   if layer.get('transformTarget')=='rotor':
    for n in r.iter():
     if n.get('data-motion-part')=='rotor':n.set('transform',f'rotate({t["rotation"]} {w/2} {h/2})')
   q=state(r,{'baseOpacity':1,'gains':t['gains']})
   for g in q.findall('{http://www.w3.org/2000/svg}g'):
    if g.get('id') not in layer.get('allowedLayers',['cold','reflection','spill','seam','core','focus','symbol']):g.set('opacity','0')
   q=unique(q,f'f{i}-');defs=q.find('{http://www.w3.org/2000/svg}defs');clip=add(defs,'clipPath',id=f'frame-reveal-{i}',clipPathUnits='userSpaceOnUse');add(clip,'rect',width=w*t['revealX'],height=h*t['revealY']);body=add(q,'g',clip_path=f'url(#frame-reveal-{i})')
   for n in list(q):
    if n is not defs and n is not body:q.remove(n);body.append(n)
   limits=layer.get('displaySize',[340,260]);s=min(limits[0]/w,limits[1]/h)*layer['legacyPlacement']['scale']*t['scale'];x=360+layer['legacyPlacement']['x']*2+t['x'];y=215+layer['legacyPlacement']['y']*2+t['y'];rotation=0 if layer.get('transformTarget')=='rotor' else t['rotation'];g=add(root,'g',transform=f'translate({x} {y}) rotate({rotation} {(layer['pivot'][0]-w/2)*s if layer.get('pivot') else 0} {(layer['pivot'][1]-h/2)*s if layer.get('pivot') else 0}) scale({s})',opacity=t['opacity']*t['baseOpacity'] if t['visible'] else 0);q.set('x',str(-w/2));q.set('y',str(-h/2));q.set('width',str(w));q.set('height',str(h));q.set('overflow','visible');g.append(q)

   label_owner=g
   if t['revealX']<1 or t['revealY']<1:
    label_defs=add(g,'defs');label_clip=add(label_defs,'clipPath',id=f'live-label-reveal-{i}',clipPathUnits='userSpaceOnUse');add(label_clip,'rect',x=-w/2,y=-h/2,width=w*t['revealX'],height=h*t['revealY']);label_owner=add(g,'g',clip_path=f'url(#live-label-reveal-{i})')
   for label in t.get('liveLabels',[]):
    add(label_owner,'text',opacity=label.get('opacity',1),x=label['x']-w/2,y=label['y']-h/2,text_anchor='middle',font_family='Segoe UI, sans-serif',font_size=min(26,max(14,label.get('fontSize',20)*s))/s,fill='#eee7d9').text=label['text']


  label=recipe.get('label') or ('Y  B  A  X' if recipe.get('controllerButtons') and not any(l.get('liveLabels') for l in recipe['layers']) else '')
  if label:
   if recipe.get('labelAnchor')=='inside':
    i=recipe.get('labelLayer',0);t=row['frame']['layers'][i];p=recipe['layers'][i]['legacyPlacement'];x=360+p['x']*2+t['x'];y=223+p['y']*2+t['y'];opacity=t['opacity']*t['baseOpacity'] if t['visible'] else 0
   else:x,y,opacity=360,430,1
   add(root,'text',x=x,y=y,opacity=opacity,text_anchor='middle',font_family='Segoe UI, sans-serif',font_size=24,fill='#eee7d9').text=label
  key=f"{row['id']}.{int(row['phase']*100):03}.{'on' if row['on'] else 'off'}";Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(root),width=720,skip_system_fonts=True,font_files=['C:/Windows/Fonts/segoeui.ttf'],sans_serif_family='Segoe UI'))).save(out/'desktop-frames'/f'{key}.png')
  exported=copy.deepcopy(root)
  for image in exported.findall('.//{http://www.w3.org/2000/svg}image'):
   href=image.get('href','')
   if href.startswith('data:image/png;base64,'):
    data=base64.b64decode(href.split(',',1)[1]);digest=hashlib.sha256(data).hexdigest();target=out/'source/rasters'/f'{digest}.png';assert target.is_file() and target.read_bytes()==data;image.set('href','../source/rasters/'+digest+'.png')
  (out/'desktop-frames'/f'{key}.svg').write_text(xml(exported),encoding='utf8');print(key,flush=True)
 for id in sorted({r['id'] for r in rows}):
  board=Image.new('RGB',(1800,1050),'#080c11');d=ImageDraw.Draw(board);d.text((24,20),id+' / sampled desktop frames',font=font(28,True),fill='#eee7d9');d.text((24,62),'Cold above / selected masks below / actual JS sampler / not browser or native playback',font=font(18),fill='#b5bdc6')
  for col,phase in enumerate(sorted({int(r['phase']*100) for r in rows if r['id']==id})):
   for yy,on in [(120,False),(580,True)]:
    im=Image.open(out/'desktop-frames'/f"{id}.{phase:03}.{'on' if on else 'off'}.png").convert('RGB');im.thumbnail((350,390),Image.Resampling.LANCZOS);board.paste(im,(col*360,yy));d.text((col*360+15,yy+260),str(phase)+'%',font=font(20),fill='#eee7d9')
  board.save(out/'previews'/f'{id}.frames.png')
 print(json.dumps({'recipes':len({r['id'] for r in rows}),'sampledFrames':len(rows),'method':'Desktop source/SVG frame rendering from actual JS sampler; browser/native/device playback unverified'}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--recipe',action='append');p.add_argument('--shard');a=p.parse_args();build(a.out.resolve(),a.recipe,a.shard)
