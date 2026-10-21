"""Author stretch-safe SVG frames and real Android nine-patch layer resources."""
from pathlib import Path
import argparse,copy,io,json,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import el,add,path,poly,chamfer,render,font,INK,SVG,TOKENS

SPECS=[('button',128,64,20,18),('field',160,64,22,18),('panel',160,128,24,24),('notification',192,96,26,22)]
DENSITIES=[('mdpi',1),('hdpi',1.5),('xhdpi',2),('xxhdpi',3)]
LAYERS=['cold','seam','core','focus','symbol']

def xml(r):return ET.tostring(r,encoding='unicode')
def master(name,w,h):
 r=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}');add(r,'title').text='Craftageddon stretch-safe '+name
 add(r,'desc').text='Original SVG geometry; only constant cross-section middle bands may stretch. Labels stay live.'
 defs=add(r,'defs')
 stops=[(0,'#8d979f'),(.12,'#495560'),(.35,'#252f39'),(.65,'#111820'),(.85,'#55616c'),(1,'#202933')]
 for key,x1,y1,x2,y2 in [('top',0,0,0,14),('bottom',0,h-14,0,h),('left',0,0,14,0),('right',w-14,0,w,0)]:
  g=add(defs,'linearGradient',id=key,gradientUnits='userSpaceOnUse',x1=x1,y1=y1,x2=x2,y2=y2)
  for off,c in stops:add(g,'stop',offset=off,stop_color=c)
 groups={}
 for layer in LAYERS:
  g=add(r,'g',id=layer);g.set('{'+INK+'}groupmode','layer');g.set('{'+INK+'}label',layer)
  if layer!='cold':g.set('style','display:none')
  groups[layer]=g
 b=groups['cold'];cut=10 if name=='field' else 14
 path(b,chamfer(1,1,w-2,h-2,cut),'#111820',stroke='#05090e',width=2)
 for key,pts in [('top',[(cut+1,2),(w-cut-1,2),(w-13,14),(13,14)]),('bottom',[(13,h-14),(w-13,h-14),(w-cut-1,h-2),(cut+1,h-2)]),('left',[(2,cut+1),(14,13),(14,h-13),(2,h-cut-1)]),('right',[(w-14,13),(w-2,cut+1),(w-2,h-cut-1),(w-14,h-13)])]:path(b,poly(pts),'url(#'+key+')')
 path(b,chamfer(15,15,w-30,h-30,4),'#10171e',stroke='#03080d',width=2)
 path(b,chamfer(2,2,w-4,h-4,cut),'none',stroke='#6d7a85',width=.65)
 path(b,chamfer(13,13,w-26,h-26,5),'none',stroke='#53606b',width=.7)
 for px,py,sx,sy in [(0,0,1,1),(w,0,-1,1),(0,h,1,-1),(w,h,-1,-1)]:
  q=lambda x,y:(px+x*sx,py+y*sy)
  path(b,poly([q(3,cut),q(cut,3),q(cut+8,5),q(9,12),q(5,cut+7)]),'#694b37',stroke='#151b21',width=1)
  path(b,poly([q(5,cut),q(cut,5),q(cut+2,7),q(7,cut+2)]),'#56636e',stroke='#222c35',width=.6)
  path(b,poly([q(7,cut-1),q(cut-1,7),q(cut+2,8),q(8,cut+2)]),'#26313b')
  path(b,'M'+','.join(map(str,q(cut+4,3)))+' l'+str(3*sx)+' '+str(2*sy)+' l'+str(-2*sx)+' '+str(3*sy),stroke='#0a1016',width=1)
 rails=f'M30 9 H{w-30} M30 {h-9} H{w-30} M9 28 V{h-28} M{w-9} 28 V{h-28}'
 path(b,rails,stroke='#02060a',width=3.6)
 path(groups['seam'],rails,stroke='white',width=1.25)
 path(groups['core'],f'M33 9 h5 M{w-38} {h-9} h5',stroke='white',width=.65)
 path(groups['focus'],chamfer(2,2,w-4,h-4,cut),stroke='white',width=2)
 path(groups['symbol'],poly([(w-25,h-19),(w-21,h-23),(w-17,h-19),(w-21,h-15)]),'white')
 return r

def layer_svg(r,name):
 q=copy.deepcopy(r)
 for g in list(q.findall('{'+SVG+'}g')):
  if g.get('id')!=name:q.remove(g)
  else:g.attrib.pop('style',None)
 return xml(q)

def ninepatch(image,stretch,padding):
 w,h=image.size;out=Image.new('RGBA',(w+2,h+2));out.paste(image,(1,1));d=ImageDraw.Draw(out);black=(0,0,0,255)
 x0,x1,y0,y1=stretch;l,t,r,b=padding
 d.line((x0+1,0,x1,0),fill=black);d.line((0,y0+1,0,y1),fill=black)
 d.line((l+1,h+1,w-r,h+1),fill=black);d.line((w+1,t+1,w+1,h-b),fill=black)
 return out

def bounds(im):
 w,h=im.size
 def run(points):
  ids=[i for i,p in enumerate(points) if p==(0,0,0,255)]
  assert ids and ids==list(range(ids[0],ids[-1]+1)),'Expected one contiguous marker run'
  return ids[0]-1,ids[-1]
 x=run([im.getpixel((i,0)) for i in range(w)]);y=run([im.getpixel((0,i)) for i in range(h)])
 return x,y

def stretch(im,size):
 (x0,x1),(y0,y1)=bounds(im);src=im.crop((1,1,im.width-1,im.height-1));w,h=src.size;tw,th=size
 assert tw>=w-(x1-x0)+1 and th>=h-(y1-y0)+1,'Target smaller than fixed caps'
 sx=[0,x0,x1,w];sy=[0,y0,y1,h];dx=[0,x0,tw-(w-x1),tw];dy=[0,y0,th-(h-y1),th];out=Image.new('RGBA',size)
 for row in range(3):
  for col in range(3):
   p=src.crop((sx[col],sy[row],sx[col+1],sy[row+1]));p=p.resize((dx[col+1]-dx[col],dy[row+1]-dy[row]),Image.Resampling.NEAREST);out.paste(p,(dx[col],dy[row]))
 return out

def composite(layers,size,state):
 result=Image.new('RGBA',size)
 settings={'cold':(1,0,0,0,0),'idle':(1,.34,.18,0,0),'hovered':(1,.5,.35,0,0),'selected':(1,.72,.65,0,1),'focused':(1,.58,.45,1,0),'selected_focused':(1,.72,.65,1,1),'pressed':(1,1,1,1,1),'disabled':(.42,0,0,0,0),'reduced':(1,.72,.65,1,1)}[state]
 for name,opacity in zip(LAYERS,settings):
  if opacity==0:continue
  im=stretch(layers[name],size)
  if name!='cold':
   color={'seam':'#ff6b24','core':'#ffc078','focus':'#d5e7f2','symbol':'#eee7d9'}[name];t=Image.new('RGBA',size,color);t.putalpha(im.getchannel('A'));im=t
  im.putalpha(im.getchannel('A').point(lambda a:round(a*opacity)));result.alpha_composite(im)
 return result

def build(out):
 assert not out.exists(),'Preserve previous checkpoints'
 for n in ['masters','layers','exports','android/res/drawable-mdpi','android/res/drawable-hdpi','android/res/drawable-xhdpi','android/res/drawable-xxhdpi','previews','verification/evidence']:(out/n).mkdir(parents=True)
 rows=[];preview_rows=[]
 for name,w,h,px,py in SPECS:
  r=master(name,w,h);(out/'masters'/f'{name}.svg').write_text(xml(r),encoding='utf8');layers={}
  for layer in LAYERS:
   s=layer_svg(r,layer);(out/'layers'/f'{name}.{layer}.svg').write_text(s,encoding='utf8')
   for density,scale in DENSITIES:
    iw,ih=round(w*scale),round(h*scale);im=Image.open(io.BytesIO(render(s,iw))).convert('RGBA');assert im.height==ih
    (out/'exports'/f'{name}.{layer}@{scale:g}x.png').write_bytes(render(s,iw))
    st=[round((w/2-2)*scale),round((w/2+2)*scale),round((h/2-2)*scale),round((h/2+2)*scale)];pad=[round(px*scale),round(py*scale),round(px*scale),round(py*scale)]
    nine=ninepatch(im,st,pad);nine.save(out/'android/res'/f'drawable-{density}'/f'cg_es_{name}_{layer}.9.png')
    if scale==1:layers[layer]=nine
  rows.append({'id':name,'size':[w,h],'minimumSize':[w-3,h-3],'stretch':[w//2-2,w//2+2,h//2-2,h//2+2],'padding':[px,py,px,py],'layers':LAYERS,'densityScales':dict(DENSITIES),'nativeIntegrated':False,'deviceVerified':False})
  preview_rows.append((name,layers,w,h))
 board=Image.new('RGB',(1680,1180),'#090e14');d=ImageDraw.Draw(board);d.text((30,24),'CRAFTAGEDDON / SCALABLE STEEL / 07',font=font(32,True),fill='#eee7d9');d.text((32,78),'Real nine-patch layers / Fixed corners / Separate runtime light / Live labels',font=font(18),fill='#b5bdc6')
 for idx,(name,layers,w,h) in enumerate(preview_rows):
  y=135+idx*230;d.text((35,y),name.upper(),font=font(21,True),fill='#eee7d9')
  for x,tw,th,state,label in [(35,270,max(h,80),'idle','Idle'),(355,450,max(h,104),'selected_focused','Selected + focused'),(865,480,max(h,156),'pressed','Hold A to confirm'),(1400,240,max(h,80),'disabled','Disabled')]:
   im=composite(layers,(tw,th),state);board.paste(im,(x,y+35),im)
   dr=ImageDraw.Draw(board);f=font(18);box=dr.textbbox((0,0),label,font=f);dr.text((x+(tw-(box[2]-box[0]))/2,y+35+th/2-12),label,font=f,fill='#eee7d9' if state!='disabled' else '#8b9299')
  for state in ['cold','idle','hovered','selected','focused','selected_focused','pressed','disabled','reduced']:composite(layers,(max(w,360),max(h,88)),state).save(out/'exports'/f'{name}.{state}.preview.png')
 d.text((35,1110),'Pixel checks preserve fixed caps and constant stretch bands. Native/device comparison remains pending.',font=font(19),fill='#b5bdc6')
 board.save(out/'previews/scalable-frame-sheet.png');(out/'components.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'tokens.json').write_text(json.dumps(TOKENS,indent=2)+'\n');print(json.dumps({'families':len(rows),'ninePatchLayers':80,'svgFiles':24}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(a.out.resolve())
