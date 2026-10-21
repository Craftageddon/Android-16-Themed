"""Assemble unchanged generated cold material into stretch-safe SVG/Android layers."""
from pathlib import Path
import argparse,base64,copy,hashlib,io,json,shutil,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import el,add,path,poly,chamfer,render,font,INK,SVG,TOKENS
from build_scalable_frames import ninepatch,stretch,DENSITIES

LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
SPECS=[('button',192,112,42,34),('field',224,112,42,34),('panel',224,176,42,38),('notification',288,128,44,36)]
LIGHT_COLORS={'reflection':'#dd6e32','spill':'#ff5c12','seam':'#ff782a','core':'#ffdda5','focus':'#d5e7f2','symbol':'#ffe5bc'}
STATES={'cold':[1,0,0,0,0,0,0],'idle':[1,.08,.12,.28,.12,0,0],'hovered':[1,.18,.30,.55,.32,0,0],'selected':[1,.22,.42,.78,.55,0,1],'selected_focused':[1,.22,.42,.78,.55,1,1],'pressed':[1,.60,1,1,1,0,1],'disabled':[.42,0,0,0,0,0,0],'reduced':[1,.22,.42,.78,.55,0,1]}

def xml(r):return ET.tostring(r,encoding='unicode')
def build_master(name,w,h,sw,sh):
 r=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}');add(r,'title').text='Craftageddon rich forged steel / scalable '+name
 add(r,'desc').text='Original cold PNG stays unchanged. SVG fixes corners and repeats constant rail cross-sections. Separate neutral runtime light masks; live content not baked.'
 defs=add(r,'defs');add(defs,'image',id='material-source',href='../source/cold-frame.png',width=sw,height=sh)
 add(defs,'image',id='material-strip',href='../source/cold-frame.png',width=sw,height=sh,image_rendering='optimizeSpeed')
 for key,sigma in [('soft-spill',2.2),('reflected-light',1.5)]:
  f=add(defs,'filter',id=key,x='-100%',y='-100%',width='300%',height='300%');add(f,'feGaussianBlur',stdDeviation=sigma)
 groups={}
 for layer in LAYERS:
  g=add(r,'g',id=layer);g.set('{'+INK+'}groupmode','layer');g.set('{'+INK+'}label',layer)
  if layer!='cold':g.set('style','display:none')
  groups[layer]=g
 b=groups['cold'];s=96/sh;scw=round(sw*.22);sch=sh/2;cw=scw*s;ch=48
 def region(sx,sy,ww,hh,x,y,ow,oh,pixelated=False):
  q=add(b,'svg',x=x,y=y,width=ow,height=oh,viewBox=f'{sx} {sy} {ww} {hh}',preserveAspectRatio='none',overflow='hidden')
  add(q,'use',href='#material-strip' if pixelated else '#material-source')
 # Four whole material corners preserve their proportions. Rails use one-pixel cross-sections,
 # held constant along their stretch direction. The source bitmap is never rewritten.
 for sx,sy,x,y in [(0,0,0,0),(sw-scw,0,w-cw,0),(0,sh-sch,0,h-ch),(sw-scw,sh-sch,w-cw,h-ch)]:region(sx,sy,scw,sch,x,y,cw,ch)
 region(sw//2,0,1,sch,cw,0,w-2*cw,ch,True);region(sw//2,sh-sch,1,sch,cw,h-ch,w-2*cw,ch,True)
 region(0,sh//2,scw,1,0,ch,cw,h-2*ch,True);region(sw-scw,sh//2,scw,1,w-cw,ch,cw,h-2*ch,True)
 add(b,'rect',x=cw,y=ch,width=w-2*cw,height=h-2*ch,fill='#151b21')
 path(b,chamfer(35,34,w-70,h-68,6),'#151b21')
 # Rail centers are visually aligned to the source's deep dark recessed channels.
 top=26.3;left=24.5;rails=f'M43 {top} H{w-43} M43 {h-top} H{w-43} M{left} 42 V{h-42} M{w-left} 42 V{h-42}'
 path(groups['seam'],rails,stroke='white',width=2.1)
 path(groups['core'],rails,stroke='white',width=.62)
 path(groups['core'],f'M48 {top} h8 M{w-56} {h-top} h8',stroke='white',width=1.15)
 path(groups['spill'],rails,stroke='white',width=4.6,filter='url(#soft-spill)')
 reflected=f'M43 20 H{w-43} M43 {h-20} H{w-43} M18.5 42 V{h-42} M{w-18.5} 42 V{h-42}'
 path(groups['reflection'],reflected,stroke='white',width=1.9,filter='url(#reflected-light)')
 for x,y,sx,sy in [(0,0,1,1),(w,0,-1,1),(0,h,1,-1),(w,h,-1,-1)]:
  path(groups['focus'],f'M{x+6*sx} {y+27*sy} L{x+6*sx} {y+19*sy} L{x+20*sx} {y+6*sy} L{x+29*sx} {y+12*sy}',stroke='white',width=1)
 path(groups['symbol'],poly([(w-43,h-39),(w-39,h-43),(w-35,h-39),(w-39,h-35)]),'white')
 return r

def layer(r,name):
 q=copy.deepcopy(r)
 for g in list(q.findall('{'+SVG+'}g')):
  if g.get('id')!=name:q.remove(g)
  else:g.attrib.pop('style',None)
 return q

def embedded(r,data):
 q=copy.deepcopy(r)
 for n in q.findall('.//{'+SVG+'}image'):n.set('href','data:image/png;base64,'+data)
 return xml(q)

def composite(layers,size,state):
 out=Image.new('RGBA',size)
 for name,gain in zip(LAYERS,STATES[state]):
  if gain==0:continue
  im=stretch(layers[name],size)
  if name!='cold':
   tint=LIGHT_COLORS[name]
   q=Image.new('RGBA',size,tint);q.putalpha(im.getchannel('A'));im=q
  im.putalpha(im.getchannel('A').point(lambda v:round(v*gain)));out.alpha_composite(im)
 return out

def write_runtime_style(out):
 spec={'schema':1,'layerOrder':LAYERS,'colors':LIGHT_COLORS,'bodyWell':'#151b21','sampleStateLayerGains':{name:dict(zip(LAYERS,gains)) for name,gains in STATES.items()},'focusOwner':'Interactive owner applies the focus layer independently, including during press. Pressed sample is unfocused.','selectedCue':'Separate geometric symbol; do not rely on emission color alone.','animationImplemented':False,'reducedMotion':'Static selected appearance; no motion or breathing.','coldInspection':'Draw only cold material; preserve original cold pixels.'}
 (out/'runtime-style.json').write_text(json.dumps(spec,indent=2)+'\n')
 tokens=copy.deepcopy(TOKENS);tokens['date']='2026-10-21';tokens['colors'].update(well='#151b21',ember=LIGHT_COLORS['seam'],hotCore=LIGHT_COLORS['core'],reflection=LIGHT_COLORS['reflection'],spill=LIGHT_COLORS['spill']);tokens['states']={name:gains[3] for name,gains in STATES.items()};tokens['runtimeStyle']='runtime-style.json contains the authoritative per-layer gains and tints for this iteration.'
 (out/'tokens.json').write_text(json.dumps(tokens,indent=2)+'\n')

def build(a):
 out=a.out.resolve();assert not out.exists();
 for d in ['source','masters','layers','exports','previews','verification/evidence']:(out/d).mkdir(parents=True)
 for den,_ in DENSITIES:(out/'android/res'/f'drawable-{den}').mkdir(parents=True)
 shutil.copy2(a.source,out/'source/cold-frame.png');data=base64.b64encode(a.source.read_bytes()).decode()
 with Image.open(a.source) as im:sw,sh=im.size;assert im.mode=='RGBA' and im.getpixel((0,0))[3]==0
 rows=[];collections={}
 for name,w,h,px,py in SPECS:
  r=build_master(name,w,h,sw,sh);(out/'masters'/f'{name}.svg').write_text(xml(r),encoding='utf8');at2={}
  for key in LAYERS:
   q=layer(r,key);(out/'layers'/f'{name}.{key}.svg').write_text(xml(q),encoding='utf8');svg=embedded(q,data)
   for den,scale in DENSITIES:
    iw,ih=round(w*scale),round(h*scale);png=render(svg,iw);im=Image.open(io.BytesIO(png)).convert('RGBA');assert im.size==(iw,ih)
    (out/'exports'/f'{name}.{key}@{scale:g}x.png').write_bytes(png)
    st=[round((w/2-2)*scale),round((w/2+2)*scale),round((h/2-2)*scale),round((h/2+2)*scale)];pad=[round(px*scale),round(py*scale),round(px*scale),round(py*scale)]
    nine=ninepatch(im,st,pad);nine.save(out/'android/res'/f'drawable-{den}'/f'cg_es_rich_{name}_{key}.9.png')
    if scale==2:at2[key]=nine
  collections[name]=at2
  for state in STATES:composite(at2,(800,max(224,h*2)),state).save(out/'exports'/f'{name}.{state}.preview.png')
  rows.append({'id':name,'size':[w,h],'minimumSize':[w-3,h-3],'padding':[px,py,px,py],'layers':LAYERS,'sourceColdUnmodified':True,'sourceColdSha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'scaling':'Fixed photographic corners, constant sampled rail cross-sections, neutral runtime masks','nativeIntegrated':False,'deviceVerified':False})
 board=Image.new('RGB',(2520,2000),'#090e14');d=ImageDraw.Draw(board);d.text((55,30),'CRAFTAGEDDON / FORGED STEEL CONTROLS',font=font(43,True),fill='#eee7d9');d.text((58,92),'Thick steel facets + copper joints / Fixed corners / Independent ember light',font=font(24),fill='#b5bdc6')
 cols=[(55,'cold','COLD STEEL'),(895,'selected','SELECTED'),(1735,'pressed','EMBER GLOW / PRESS')]
 for x,_,label in cols:d.text((x,157),label,font=font(26,True),fill='#eee7d9')
 for i,(name,w,h,px,py) in enumerate(SPECS):
  y=220+i*420;d.text((55,y),name.upper(),font=font(23,True),fill='#b5bdc6')
  for x,state,_ in cols:
   im=composite(collections[name],(730,max(224,h*2)),state);board.paste(im,(x,y+45),im)
   # Sheet labels are illustrative live content, never included in material layers.
   label={'button':'Launch game','field':'Search games','panel':'Game profile','notification':'Game session paused'}[name];f=font(27);box=d.textbbox((0,0),label,font=f);d.text((x+(730-(box[2]-box[0]))/2,y+45+im.height/2-17),label,font=f,fill='#eee7d9')
 d.text((58,1920),'Actual layered asset renders. Cold material stays unchanged; masks supply all ember light.',font=font(23),fill='#b5bdc6')
 board.save(out/'previews/selected-and-ember-sheet.png')
 close=Image.new('RGB',(2040,880),'#090e14');dr=ImageDraw.Draw(close);dr.text((50,30),'SAME CONTROL / COLD → SELECTED → EMBER GLOW',font=font(35,True),fill='#eee7d9')
 for i,(state,title) in enumerate([('cold','Cold forged steel'),('selected','Selected — ember channels'),('pressed','Pressed — hotter core and spill')]):
  y=100+i*250;im=composite(collections['button'],(1240,224),state);close.paste(im,(740,y),im);dr.text((50,y+77),title,font=font(29),fill='#eee7d9');f=font(32);box=dr.textbbox((0,0),'Launch game',font=f);dr.text((740+(1240-(box[2]-box[0]))/2,y+90),'Launch game',font=f,fill='#eee7d9')
 close.save(out/'previews/button-state-closeup.png')
 (out/'components.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'tokens.json').write_text(json.dumps(TOKENS,indent=2)+'\n');(out/'source/provenance.json').write_text(json.dumps({'tool':'Built-in OpenAI image generation','coldSourcePreserved':True,'canvas':[sw,sh],'sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'maskAuthoring':'Original SVG masks aligned to dark rails; preview-only tint and blend'},indent=2)+'\n')
 write_runtime_style(out)
 print(json.dumps({'families':4,'layers':len(LAYERS),'ninePatchConfigurations':112,'sourceCanvas':[sw,sh],'pngFiles':len(list(out.rglob('*.png')))}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);build(p.parse_args())
