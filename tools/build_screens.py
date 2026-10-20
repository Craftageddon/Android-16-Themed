"""Compose scalable source screens from the pilot, with all labels kept as SVG text."""
from pathlib import Path
import argparse,base64,copy,io,json,math,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import Asset,SPECS,SVG,el,add,path,defs,render,font,fitpaste

def text(root,s,x,y,size=16,color='#eee7d9',anchor='start',family='sans-serif'):
 add(root,'text',x=x,y=y,fill=color,font_family=family,font_size=size,text_anchor=anchor).text=s
def asset(root,key,x,y,w=None,h=None,state='idle',labels=False):
 a=Asset(next(s for s in SPECS if s[0]==key),3).build();n=ET.fromstring(a.doc(state,labels=labels));n.set('x',str(x));n.set('y',str(y));n.set('width',str(w or a.w));n.set('height',str(h or a.h));root.append(n)
def frame(root,x,y,w,h,state='idle'):
 a=Asset(('frame','Frame',w,h,''),3);a.frame(3,3,w-6,h-6);n=ET.fromstring(a.doc(state));n.set('x',str(x));n.set('y',str(y));root.append(n)
def screen(w,h,title):
 r=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}');add(r,'title').text=title
 add(r,'rect',width=w,height=h,fill='#090e14');defs(r,3)
 return r
def header(r,title,w,sub=None):
 text(r,title,24,32,21,family='serif');text(r,'13:20',w-24,30,12,'#b5bdc6','end')
 path(r,f'M24 46 H{w-24}',stroke='#394552',width=1)
 if sub:text(r,sub,24,69,12,'#b5bdc6')
def hero(root,out,kind,x,y,w,h,state='idle'):
 q=ET.parse(out/'hero'/f'{kind}-master.svg').getroot();q.set('x',str(x));q.set('y',str(y));q.set('width',str(w));q.set('height',str(h))
 for g in q.findall('{'+SVG+'}g'):
  if g.get('id')=='cold':g.find('{'+SVG+'}image').set('href','../hero/'+kind+'-cold.png')
  else:
   g.attrib.pop('style',None);g.set('opacity','.9' if state=='selected' else '.4')
   for n in g.iter():
    for attr in ['fill','stroke']:
     if n.get(attr)=='white':n.set(attr,'#ff6b24' if g.get('id')=='seam' else '#ffc078')
 if kind=='primary':text(q,'Launch game',1049,397,70,anchor='middle')
 root.append(q)
def serialize(root,out):
 return ET.tostring(root,encoding='unicode')
def inline_images(root,folder):
 q=copy.deepcopy(root)
 for n in q.iter():
  if n.tag==f'{{{SVG}}}image':
   p=(folder/n.attrib['href']).resolve();n.set('href','data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode())
 return ET.tostring(q,encoding='unicode')
def build(out):
 folder=out/'screens';folder.mkdir(exist_ok=True);screens={}
 # Logical grids, explicitly not hardware pixel or Android dp measurements.
 r=screen(960,540,'Thor upper launcher — design composition');header(r,'CRAFTAGEDDON',960,'Library / Recently played')
 frame(r,24,92,560,268,'selected');text(r,'Return to the forge',52,133,26,family='serif');text(r,'Your games, ready on the top display.',52,165,16,'#b5bdc6')
 # Original geometric atmosphere rather than third-party game artwork.
 for i in range(6):path(r,f'M{70+i*70} 274 l28 -69 l28 69 Z',fill='url(#steel)',stroke='#495765',width=1)
 text(r,'ARCADE COLLECTION',52,322,13,'#b5bdc6');frame(r,607,92,329,126);text(r,'Launch on',631,125,16);text(r,'Top screen',631,162,22);text(r,'Change display',631,190,12,'#b5bdc6')
 frame(r,607,232,329,128);text(r,'Current profile',631,265,16);text(r,'Balanced',631,300,22);text(r,'Power / input / display',631,332,12,'#b5bdc6')
 hero(r,out,'primary',24,378,560,146,'selected');text(r,'A  Open     B  Back     X  Options',628,421,14,'#b5bdc6');text(r,'Lower panel: game keeps input',628,454,13,'#b5bdc6');screens['thor-upper-launcher']=r
 r=screen(960,540,'Thor upper shade — design composition');header(r,'Quick controls',960,'Network / sound / device')
 for i,label in enumerate(['Wi-Fi','Bluetooth','Audio','Airplane']):
  x=24+i*232;frame(r,x,91,216,112,'selected' if i<2 else 'idle');text(r,label,x+22,129,17);text(r,'On' if i<2 else 'Off',x+22,175,14,'#b5bdc6')
 asset(r,'slider',24,227,560,86);text(r,'Display brightness',46,230,15);frame(r,607,224,329,86);text(r,'Gaming panel',631,259,17);text(r,'Open on lower display',631,284,13,'#b5bdc6')
 asset(r,'notification',24,334,560,182,labels=True);frame(r,607,334,329,182);text(r,'Sound output',631,372,17);text(r,'Device speakers',631,410,20);text(r,'Profile: Balanced',631,468,14,'#b5bdc6');screens['thor-upper-shade']=r
 r=screen(360,414,'Thor lower control center — logical layout');header(r,'Game controls',360)
 frame(r,14,59,332,66);text(r,'Input stays with game',31,86,16);text(r,'Capture controls',31,110,12,'#b5bdc6')
 for i,label in enumerate(['Input','Display','Profile']):frame(r,14+i*113,140,106,66,'focused' if i==0 else 'idle');text(r,label,67+i*113,180,15,anchor='middle')
 for i,(label,value) in enumerate([('Performance','Balanced'),('Fan','Auto'),('Lights','Ember')]):
  y=223+i*49;frame(r,14,y,332,44);text(r,label,31,y+28,14);text(r,value,324,y+28,14,'#b5bdc6','end')
 text(r,'A Select     B Return to game',180,399,12,'#b5bdc6','middle');screens['thor-lower-dashboard']=r
 r=screen(360,414,'Thor lower calibration — logical layout');header(r,'Input calibration',360)
 text(r,'Left stick',24,77,18);asset(r,'calibration',40,86,280,160,labels=True)
 frame(r,14,264,332,54);text(r,'Dead zone',31,296,15);text(r,'8%',324,296,15,'#b5bdc6','end')
 frame(r,14,331,159,54);frame(r,187,331,159,54,'focused');text(r,'Reset',94,364,15,anchor='middle');text(r,'Apply',266,364,15,anchor='middle');screens['thor-lower-calibration']=r
 r=screen(360,414,'Thor lower profile editor — logical layout');header(r,'Game profile',360)
 text(r,'Arcade collection',24,79,21);text(r,'Per-app profile',24,101,12,'#b5bdc6')
 for i,(label,value) in enumerate([('Launch display','Top'),('Performance','Balanced'),('Input layout','Default'),('Trigger mode','Analog')]):
  y=119+i*54;frame(r,14,y,332,48,'focused' if i==1 else 'idle');text(r,label,31,y+30,14);text(r,value,325,y+30,14,'#b5bdc6','end')
 frame(r,14,350,332,50,'selected');text(r,'Save profile',180,382,16,anchor='middle');screens['thor-lower-profile']=r
 r=screen(540,960,'Lock and charging — atmosphere design');text(r,'CRAFTAGEDDON',270,102,25,anchor='middle',family='serif');text(r,'13:20',270,188,54,anchor='middle');text(r,'Tuesday, 20 October',270,223,16,'#b5bdc6','middle')
 hero(r,out,'ring',95,285,350,350,'selected');text(r,'72%',270,477,41,anchor='middle');text(r,'Charging',270,512,17,'#b5bdc6','middle')
 text(r,'Press power to wake',270,725,16,'#b5bdc6','middle');text(r,'Swipe to unlock',270,844,19,anchor='middle');screens['lock-and-charging']=r
 for key,r in screens.items():
  (folder/f'{key}.svg').write_text(serialize(r,out),encoding='utf-8');(folder/f'{key}.png').write_bytes(render(inline_images(r,folder)))
 board=Image.new('RGBA',(1800,1450),'#090e14');d=ImageDraw.Draw(board)
 d.text((44,30),'CRAFTAGEDDON / THOR SCREEN COMPOSITIONS',font=font(34,True),fill='#eee7d9');d.text((46,85),'ITERATION 03 / LOGICAL DESIGN GRIDS / SAMPLE CONTENT AND VALUES',font=font(17),fill='#b5bdc6')
 boxes=[('thor-upper-launcher',(40,150,960,540)),('thor-upper-shade',(40,790,960,540)),('thor-lower-dashboard',(1050,150,360,414)),('thor-lower-profile',(1050,650,360,414)),('lock-and-charging',(1450,150,300,534))]
 for key,box in boxes:
  x,y,w,h=box;im=Image.open(folder/f'{key}.png').convert('RGBA');im.thumbnail((w,h),Image.Resampling.LANCZOS);board.alpha_composite(im,(x,y));d.text((x,y-28),key.replace('thor-','').replace('-',' ').upper(),font=font(15,True),fill='#b5bdc6')
 d.text((1050,1140),'Controller-first focus',font=font(25,True),fill='#eee7d9');d.text((1050,1184),'Explicit capture / release',font=font(18),fill='#b5bdc6');d.text((1050,1217),'Per-app profiles and display target',font=font(18),fill='#b5bdc6');d.text((1050,1250),'Separate art and hardware owners',font=font(18),fill='#b5bdc6');d.text((45,1392),'Design preview. Display geometry, firmware services, input mapping and performance need device verification.',font=font(18),fill='#b5bdc6')
 board.convert('RGB').save(out/'previews/thor-screen-sheet.png')
 (folder/'layout-metadata.json').write_text(json.dumps({'coordinateSystem':'logical design units, NOT physical pixels or measured dp','upper':[960,540],'lower':[360,414],'lock':[540,960],'targetGeometryVerified':False,'sampleValues':True,'screenCount':len(screens),'nativeIntegration':False},indent=2))
 print('Composed',len(screens),'screens')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();build(a.out.resolve())
