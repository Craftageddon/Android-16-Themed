"""Preserve generated cold rasters unchanged; compose live light/content in SVG."""
from pathlib import Path
import argparse,base64,copy,hashlib,json,shutil,xml.etree.ElementTree as ET
from build_pilot import el,add,path,render,SVG,TOKENS
from PIL import Image
from build_symbols import geometry

def xml(r):return ET.tostring(r,encoding='unicode')
def text(r,x,y,value,size=28,color='#eee7d9',anchor='start'):
 add(r,'text',x=x,y=y,fill=color,font_family='sans-serif',font_size=size,text_anchor=anchor).text=value
def material(source,out,kind):
 out.mkdir(parents=True);target=out/f'{kind}-cold.png';shutil.copy2(source,target)
 with Image.open(source) as im:w,h=im.size;assert im.mode=='RGBA' and im.getpixel((0,0))[3]==0
 r=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}')
 add(r,'title').text=f'Craftageddon {kind}: unchanged cold raster and separate neutral masks'
 cold=add(r,'g',id='cold');add(cold,'image',href=target.name,width=w,height=h)
 seam=add(r,'g',id='seam',style='display:none');core=add(r,'g',id='core',style='display:none');symbol=add(r,'g',id='symbol')
 if kind=='notification':
  path(seam,'M755 190 H1880 M755 525 H1880',stroke='white',width=10)
  path(core,'M850 190 h110 M1640 525 h100',stroke='white',width=3)
 else:
  path(seam,'M315 206 H940 M315 1044 H940 M175 345 V535 M175 650 V890 M1078 345 V535 M1078 650 V890',stroke='white',width=9)
  path(core,'M450 206 h90 M715 1044 h90',stroke='white',width=3)
 r.set('xmlns:inkscape','http://www.inkscape.org/namespaces/inkscape')
 for g in [cold,seam,core,symbol]:g.set('inkscape:groupmode','layer');g.set('inkscape:label',g.get('id'))
 (out/f'{kind}-master.svg').write_text(xml(r),encoding='utf8')
 for name,g in [('cold',cold),('seam',seam),('core',core),('symbol',symbol)]:
  q=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}');q.set('xmlns:inkscape','http://www.inkscape.org/namespaces/inkscape');g=copy.deepcopy(g);g.attrib.pop('style',None);q.append(g)
  (out/f'{kind}-{name}.svg').write_text(xml(q),encoding='utf8')
  if name!='cold':(out/f'{kind}-{name}.png').write_bytes(render(xml(q)))
 (out/f'{kind}-metadata.json').write_text(json.dumps({'canvas':[w,h],'coldPngUnmodified':True,'coldSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'fixedAspectOnly':True,'ninePatchReady':False,'nativeIntegrated':False,'deviceVerified':False,'maskAlignment':'Visually authored within dark straight rail channels; curved decorative rim remains unlit.'},indent=2))
 return r
def state(r,kind,state,label=None,secondary=None):
 q=copy.deepcopy(r);w,h=map(int,[q.get('width'),q.get('height')]);defs=add(q,'defs');f=add(defs,'filter',id='glow',x='-100%',y='-100%',width='300%',height='300%');add(f,'feGaussianBlur',stdDeviation=9)
 for g in list(q.findall('{'+SVG+'}g')):
  name=g.get('id');g.attrib.pop('style',None)
  if name=='cold':
   im=g.find('{'+SVG+'}image');im.set('href','data:image/png;base64,'+base64.b64encode((CURRENT/kind/im.get('href')).read_bytes()).decode())
   if state=='disabled':g.set('opacity','.42')
  if name in ['seam','core']:
   g.set('opacity',str(0 if state in ['cold','disabled'] else .42 if state=='idle' else .95))
   for n in g.iter():
    if n.get('stroke')=='white':n.set('stroke','#ed691e' if name=='seam' else '#ffd69e')
   if name=='seam':b=copy.deepcopy(g);b.set('filter','url(#glow)');q.insert(1,b)
 if label:
  icon='controller' if kind=='notification' else {'Wi-Fi':'wifi_4','Bluetooth':'bluetooth_on','Performance':'performance_balanced','Screen route':'display_upper','Mapping':'controller','Display':'screen_swap','Fan mode':'fan_auto'}.get(label,'wifi_4')
  g=add(q,'g',transform='translate(235 248) scale(9)' if kind=='notification' else 'translate(542 325) scale(7)')
  for d,fill in geometry(icon):path(g,d,'#c9d4de' if fill else 'none',stroke='#c9d4de',width=1.8)
  cx=w*.61 if kind=='notification' else w/2
  text(q,cx,h*.46 if kind=='notification' else h*.5,label,82 if kind=='notification' else 90,anchor='middle')
  if secondary:text(q,cx,h*.62,secondary,48 if kind=='notification' else 56,'#c7cdd4','middle')
 if state=='focused':add(q,'rect',x=8,y=8,width=w-16,height=h-16,rx=12,fill='none',stroke='#d5e7f2',stroke_width=9)
 return q
def place(r,asset,x,y,w):
 a=copy.deepcopy(asset);h=w*int(a.get('height'))/int(a.get('width'));a.set('x',str(x));a.set('y',str(y));a.set('width',str(w));a.set('height',str(h));r.append(a)
def screen(w,h,title):
 r=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}');add(r,'rect',width=w,height=h,fill='#090e14');text(r,40,54,title,30);return r
def build(a):
 global CURRENT
 out=a.out.resolve();assert not out.exists();CURRENT=out/'materials';CURRENT.mkdir(parents=True)
 (out/'previews').mkdir();(out/'screens').mkdir();(out/'verification/evidence').mkdir(parents=True)
 assets={k:material(s,CURRENT/k,k) for k,s in [('notification',a.notification),('tile',a.tile)]}
 for kind,r in assets.items():
  for st in ['cold','idle','hovered','selected','focused','pressed','disabled','reduced']:
   q=state(r,kind,st,'Game ready' if kind=='notification' else 'Wi-Fi','Tap to resume' if kind=='notification' else 'Connected')
   (CURRENT/kind/f'{kind}-{st}.preview.png').write_bytes(render(xml(q),1024 if kind=='notification' else 512))
 shade=screen(1280,720,'Quick settings / upper display concept')
 for i,(label,sub) in enumerate([('Wi-Fi','Connected'),('Bluetooth','Gamepad'),('Performance','Balanced'),('Screen route','Upper')]):place(shade,state(assets['tile'],'tile','focused' if i==2 else 'selected',label,sub),60+i*295,85,265)
 place(shade,state(assets['notification'],'notification','idle','Game session paused','A to resume  ·  B to dismiss'),50,360,1180)
 lower=screen(800,600,'Game companion / lower display concept')
 for i,(label,sub) in enumerate([('Mapping','Profile 01'),('Display','Swap'),('Fan mode','Auto')]):place(lower,state(assets['tile'],'tile','focused' if i==0 else 'idle',label,sub),25+i*255,100,240)
 text(lower,45,420,'A  Select      B  Back      LB / RB  Switch section',23)
 text(lower,45,470,'Focus moves only while this panel owns controller input.',22,'#b5bdc6')
 text(lower,45,510,'Release capture before returning control to the game.',22,'#b5bdc6')
 screens=[('upper-quick-settings',shade),('lower-game-companion',lower)]
 for name,r in screens:
  (out/'screens'/f'{name}.svg').write_text(xml(r),encoding='utf8');(out/'previews'/f'{name}.png').write_bytes(render(xml(r)))
 board=screen(1800,1320,'CRAFTAGEDDON / MATERIAL EXPANSION / 06')
 place(board,state(assets['notification'],'notification','cold'),55,100,1100);place(board,state(assets['tile'],'tile','cold'),1250,95,470)
 place(board,shade,40,600,1050);place(board,lower,1110,600,650)
 text(board,55,530,'Cold originals preserved; light and labels remain independent.',26)
 text(board,55,1270,'Logical compositions only. Fixed-aspect artwork; no stretch or target-device validation.',23,'#b5bdc6')
 (out/'previews/material-expansion-sheet.png').write_bytes(render(xml(board)))
 print(json.dumps({'materials':2,'screenConcepts':2,'pngFiles':len(list(out.rglob('*.png'))),'svgFiles':len(list(out.rglob('*.svg')))}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--notification',type=Path,required=True);p.add_argument('--tile',type=Path,required=True);p.add_argument('--out',type=Path,required=True);build(p.parse_args())
