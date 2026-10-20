"""Wrap original generated cold material in separately editable runtime masks.

Copies the original PNG unchanged. SVG owns composition, masks and live labels.
"""
from pathlib import Path
import argparse,base64,copy,json,shutil
from build_pilot import el,add,path,render,SVG,TOKENS
from PIL import Image

def build(source,out,kind):
 out.mkdir(parents=True,exist_ok=True);target=out/f'{kind}-cold.png';shutil.copy2(source,target)
 with Image.open(target) as im:w,h=im.size;assert im.mode=='RGBA';assert im.getchannel('A').getextrema()[0]==0
 root=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}');add(root,'title').text='Craftageddon hero '+kind+' / cold raster with editable neutral masks'
 cold=add(root,'g',id='cold');add(cold,'image',href=target.name,width=w,height=h)
 seam=add(root,'g',id='seam',style='display:none');core=add(root,'g',id='core',style='display:none')
 if kind=='primary':
  # Authored against the 2098 x 749 master. Center channels are separate from copper joints.
  assert (w,h)==(2098,749)
  path(seam,'M325 177 H1746 M325 553 H1746',stroke='white',width=7)
  path(core,'M480 177 h85 M1410 553 h74',stroke='white',width=2)
 else:
  import math
  cx=627;cy=648;r=420
  for a,b in [(-76,-7),(7,22),(40,140),(158,173),(187,255)]:
   point=lambda angle:(cx+r*math.cos(math.radians(angle)),cy+r*math.sin(math.radians(angle)))
   x1,y1=point(a);x2,y2=point(b)
   path(seam,f'M{x1:g} {y1:g} A{r} {r} 0 0 1 {x2:g} {y2:g}',stroke='white',width=4)
  x,y=point(-50);add(core,'circle',cx=x,cy=y,r=2,fill='white')
 import xml.etree.ElementTree as ET
 for name,g in [('cold',cold),('seam',seam),('core',core)]:
  q=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}');layer=copy.deepcopy(g);layer.attrib.pop('style',None);q.append(layer)
  (out/f'{kind}-{name}.svg').write_text(ET.tostring(q,encoding='unicode'),encoding='utf-8')
  if name!='cold':(out/f'{kind}-{name}.png').write_bytes(render(ET.tostring(q,encoding='unicode')))
 root.set('xmlns:inkscape','http://www.inkscape.org/namespaces/inkscape')
 for g in [cold,seam,core]:g.set('inkscape:groupmode','layer');g.set('inkscape:label',g.attrib['id'])
 (out/f'{kind}-master.svg').write_text(ET.tostring(root,encoding='unicode'),encoding='utf-8')
 for state,opacity in [('cold',0),('idle',.4),('selected',.9),('focused',.9),('disabled',0),('reduced',.9)]:
  q=copy.deepcopy(root)
  for g in q.findall('{'+SVG+'}g'):
   name=g.attrib['id'];g.attrib.pop('style',None)
   if name=='cold':
    g.find('{'+SVG+'}image').set('href','data:image/png;base64,'+base64.b64encode(target.read_bytes()).decode())
    if state=='disabled':g.set('opacity','.42')
   else:
    g.set('opacity',str(opacity if name=='seam' else opacity*.8))
    for n in g.iter():
     for attr in ['fill','stroke']:
      if n.get(attr)=='white':n.set(attr,TOKENS['colors']['ember' if name=='seam' else 'hotCore'])
  if kind=='primary':
   add(q,'text',x=w/2,y=h*.53,fill='#eee7d9',font_family='sans-serif',font_size=70,text_anchor='middle').text='Launch game'
  if state=='focused':add(q,'rect',x=12,y=12,width=w-24,height=h-24,rx=12,fill='none',stroke='#d5e7f2',stroke_width=7)
  (out/f'{kind}-{state}.preview.png').write_bytes(render(ET.tostring(q,encoding='unicode'),1024 if kind=='primary' else 512))
 (out/f'{kind}-metadata.json').write_text(json.dumps({'canvas':[w,h],'coldPngUnmodified':True,'maskAuthoring':'Original neutral SVG masks aligned visually to recessed channels','native':'not integrated','limits':'Fixed aspect ratio; do not stretch. Raster rendering and state transitions need target profiling.'},indent=2))
 print(kind,w,h)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--kind',choices=['primary','ring'],required=True);a=p.parse_args();build(a.source,a.out,a.kind)
