"""Original ES-025..038 symbol geometry with separate detailed/compact optical masters."""
from pathlib import Path
import argparse,copy,io,json,math,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import Asset,SVG,TOKENS,el,add,path,render,font

def circle(x,y,r):return f'M{x-r} {y} a{r} {r} 0 1 0 {r*2} 0 a{r} {r} 0 1 0 {-r*2} 0'
def rect(x,y,w,h):return f'M{x} {y} h{w} v{h} h{-w} Z'
def geometry(name):
 paths=[];fills=[]
 def p(s,fill=False):paths.append(s);fills.append(fill)
 root=name.removesuffix('_off').removesuffix('_on').removesuffix('_connected')
 if name.startswith('battery_'):
  p('M5 5 H18 V21 H5 Z M9 2 H14 V5')
  state=name[8:]
  if state.isdigit():
   level=int(state)
   if level:p(rect(8,19-level*.12,7,level*.12),True)
  elif state=='charging':p('M13 8 L8 14 H12 L10 19 L16 12 H12 Z',True)
  elif state=='saver':p('M8 12 L15 9 L15 16 L9 17 Z M9 16 L15 10')
  elif state=='critical':p('M11.5 8 V14 M11.5 17 V17.2')
  elif state=='unknown':p('M9 10 Q9 7 12 8 Q16 10 12 13 V14 M12 17 V17.1')
  else:raise ValueError(name)
 elif name.startswith('wifi_'):
  state=name[5:];level=int(state) if state.isdigit() else 4
  if level>=4:p('M2 7 Q12 -1 22 7')
  if level>=3:p('M5 11 Q12 5 19 11')
  if level>=2:p('M8 15 Q12 12 16 15')
  p(circle(12,19,1),True)
  if state=='0':p('M2 7 Q12 -1 22 7 L12 20 Z')
  if state in ['off','no_internet']:p('M20 14 V18 M20 21 V21.1' if state=='no_internet' else 'M3 3 L21 21')
 elif name.startswith('cellular_'):
  state=name[9:];level=int(state) if state.isdigit() else 4
  for j in range(4):
   x=3+j*5;height=4+j*4;p(rect(x,21-height,2.7,height),j<level)
  if state=='off':p('M2 2 L22 22')
 elif root=='bluetooth':
  p('M7 6 L17 16 L12 21 V3 L17 8 L7 18')
  if name.endswith('connected'):p('M3 12 h1 M21 12 h1')
 elif root=='nfc':p('M3 21 V3 H8 L16 16 V3 H21 V21 H16 L8 8 V21 Z')
 elif root=='hotspot':p(circle(12,12,2),True);p('M7 7 A7 7 0 0 0 7 17 M17 7 A7 7 0 0 1 17 17 M3.5 3.5 A12 12 0 0 0 3.5 20.5 M20.5 3.5 A12 12 0 0 1 20.5 20.5')
 elif root=='cast':p('M3 8 V4 H21 V20 H16 M3 13 A7 7 0 0 1 10 20 M3 17 A3 3 0 0 1 6 20');p(circle(3,21,1),True)
 elif root=='airplane':p('M12 2 L14 9 L22 14 V16 L14 13 V19 L17 21 V22 L12 20 L7 22 V21 L10 19 V13 L2 16 V14 L10 9 Z',True)
 elif root in ['sim','esim','sim_warning']:
  p('M7 3 H15 L20 8 V21 H4 V6 Z')
  if root=='esim':p('M9 9 H15 V17 H9 Z M7 11 H9 M15 11 H17 M7 15 H9 M15 15 H17')
  elif root=='sim_warning':p('M12 8 V13 M12 17 V17.1')
  else:p('M7 12 H17 V18 H7 Z M12 12 V18')
 elif root in ['mobile_data','mobile_data_saver']:p('M6 21 V3 M2 7 L6 3 L10 7 M18 3 V21 M14 17 L18 21 L22 17')
 elif root.startswith('network_'):
  label=root[8:]
  if label=='4g':p('M7 3 L2 12 H10 M7 3 V21 M21 6 Q13 0 13 12 Q13 24 22 18 V12 H18')
  elif label=='5g':p('M10 3 H2 V11 Q11 7 10 17 Q7 24 2 20 M21 6 Q13 0 13 12 Q13 24 22 18 V12 H18')
  elif label=='lte':p('M2 4 V20 H7 M8 4 H14 M11 4 V20 M23 4 H17 V20 H23 M17 12 H22')
  else:raise ValueError(name)
 elif root in ['camera','screenshot','screen_recording']:
  p('M3 7 H8 L10 4 H15 L17 7 H21 V21 H3 Z' if root=='camera' else rect(3,5,18,15));p(circle(12,13,4),root=='screen_recording')
 elif root=='microphone':p('M9 4 Q12 0 15 4 V12 Q12 16 9 12 Z M6 11 Q6 19 12 19 Q18 19 18 11 M12 19 V22 M8 22 H16')
 elif root in ['location','location_precise']:p('M12 22 Q3 13 5 8 Q8 -1 16 4 Q25 10 12 22 Z');p(circle(12,9,2))
 elif root in ['privacy','security','vpn','shield']:
  p('M12 2 L21 6 V12 Q21 19 12 23 Q3 19 3 12 V6 Z')
  if root=='security':p('M7 12 l4 4 l6 -8')
  elif root=='vpn':p(circle(10,11,3));p('M13 11 H18 M16 11 V14')
  else:p('M8 12 H16 V18 H8 Z M9 12 V9 Q12 5 15 9 V12')
 elif root=='alarm':p(circle(12,13,8));p('M12 8 V13 L16 15 M3 5 L7 2 M17 2 L21 5 M6 20 L4 23 M18 20 L20 23')
 elif root=='dnd':p(circle(12,12,9));p('M7 12 H17')
 elif root in ['audio','volume','mute']:
  p('M3 9 H7 L12 4 V20 L7 15 H3 Z',True)
  if root=='mute':p('M16 8 L22 16 M22 8 L16 16')
  else:p('M16 7 Q22 12 16 17 M18 3 Q28 12 18 21')
 elif root in ['headphones','headset']:
  p('M4 15 V10 A8 8 0 0 1 20 10 V15 M4 12 H7 V20 H3 V13 M20 12 H17 V20 H21 V13')
  if root=='headset':p('M20 18 V22 H14')
 elif root=='vibration':p(rect(8,3,8,18));p('M4 6 L2 9 L4 12 L2 15 L4 18 M20 6 L22 9 L20 12 L22 15 L20 18')
 elif root in ['download','upload']:
  p('M4 17 V22 H20 V17');p('M12 2 V16 M6 10 L12 16 L18 10' if root=='download' else 'M12 17 V3 M6 9 L12 3 L18 9')
 elif root in ['sync','restart']:p('M3 9 A9 9 0 0 1 20 7 M20 2 V7 H15 M21 15 A9 9 0 0 1 4 17 M4 22 V17 H9')
 elif root=='usb':p('M12 22 V3 M9 6 L12 2 L15 6 M12 17 L6 13 V9 M12 13 L18 9 V6');p(circle(6,8,1),True);p(rect(17,4,2,2),True)
 elif root=='storage':p('M3 7 Q12 1 21 7 Q12 13 3 7 V18 Q12 24 21 18 V7 M3 12 Q12 18 21 12')
 elif root in ['controller','gaming']:p('M6 6 H18 Q21 7 23 18 Q22 23 17 17 H7 Q2 23 1 18 Q3 7 6 6 Z M5 11 H11 M8 8 V14');p(circle(17,10,1),True);p(circle(20,13,1),True)
 elif root=='keyboard':p(rect(2,5,20,15));p('M5 9 H7 M10 9 H12 M15 9 H17 M19 9 H20 M5 13 H7 M10 13 H12 M15 13 H19 M7 17 H17')
 elif root=='mouse':p('M6 10 A6 6 0 0 1 18 10 V17 A6 6 0 0 1 6 17 Z M12 3 V10 M6 11 H18')
 elif root in ['display_upper','display_lower','display_external','display']:
  p(rect(2,3,20,14));p('M8 22 H16 M12 17 V22')
  if root=='display_upper':p('M7 10 L12 6 L17 10')
  if root=='display_lower':p('M7 8 L12 12 L17 8')
  if root=='display_external':p('M6 14 L18 5 M12 5 H18 V11')
 elif root in ['screen_swap','app_pairs']:p(rect(2,3,8,8));p(rect(14,13,8,8));p('M14 5 H21 V10 M10 19 H3 V14 M18 2 L21 5 L18 8 M6 16 L3 19 L6 22')
 elif root=='rotation':p('M5 7 A8 8 0 0 1 20 6 M20 1 V6 H15 M19 17 A8 8 0 0 1 4 18 M4 23 V18 H9');p(rect(9,6,6,12))
 elif root in ['fan','fan_auto','fan_quiet']:
  p(circle(12,12,2),True)
  for angle in [0,120,240]:
   a=math.radians(angle);cx=12+5*math.cos(a);cy=12+5*math.sin(a);p(circle(round(cx,2),round(cy,2),3.5))
  if root=='fan_auto':p('M18 20 l2 -4 l2 4 M19 19 H21')
  if root=='fan_quiet':p('M21 15 Q16 18 20 22 Q13 21 17 15')
 elif root in ['performance','performance_balanced','performance_fast']:
  p('M3 18 A9 9 0 0 1 21 18 M6 21 H18');p({'performance':'M12 17 L7 9','performance_balanced':'M12 17 V6','performance_fast':'M12 17 L18 8'}[root]);p(circle(12,17,1.4),True)
 elif root in ['temperature','thermal_warning']:
  p('M10 4 Q12 1 14 4 V15 A4 4 0 1 1 10 15 Z M12 7 V18')
  if root=='thermal_warning':p('M21 6 V12 M21 16 V16.1')
 elif root=='power':p('M12 2 V11 M6 5 A9 9 0 1 0 18 5')
 elif root=='sleep':p('M18 3 A10 10 0 1 0 22 16 A9 9 0 0 1 18 3 Z')
 elif root in ['lock','lockdown']:p(rect(5,10,14,12));p('M8 10 V6 A4 4 0 0 1 16 6 V10 M12 14 V18')
 elif root in ['home','launcher_home']:p('M2 11 L12 2 L22 11 M5 9 V22 H19 V9 M10 22 V15 H14 V22')
 elif root in ['back','forward','up','down']:
  p({'back':'M16 3 L7 12 L16 21','forward':'M8 3 L17 12 L8 21','up':'M3 16 L12 7 L21 16','down':'M3 8 L12 17 L21 8'}[root])
 elif root=='recents':p(rect(3,3,6,18));p(rect(13,3,8,18))
 elif root in ['close','error']:p('M4 4 L20 20 M20 4 L4 20')
 elif root in ['check','success']:p('M3 12 L9 18 L21 5')
 elif root in ['warning','emergency']:p('M12 2 L23 22 H1 Z M12 8 V14 M12 18 V18.1')
 elif root in ['info','about']:p(circle(12,12,10));p('M12 11 V19 M12 6 V6.2')
 elif root in ['settings','system','controls']:
  if root=='controls':p('M5 2 V22 M12 2 V22 M19 2 V22 M2 7 H8 M9 16 H15 M16 10 H22')
  else:
   pts=[]
   for i in range(32):
    r=10 if i%4<2 else 8;a=i*math.pi/16;pts.append((12+r*math.cos(a),12+r*math.sin(a)))
   p('M'+' L'.join(f'{x:.2f} {y:.2f}' for x,y in pts)+' Z');p(circle(12,12,3.5))
 elif root in ['apps','app_drawer']: 
  for x in [3,14]:
   for y in [3,14]:p(rect(x,y,7,7))
 elif root in ['accounts','person','accessibility']:p(circle(12,5,3));p('M4 22 Q4 12 12 12 Q20 12 20 22')
 elif root=='network':p(circle(12,12,10));p('M2 12 H22 M12 2 Q4 12 12 22 Q20 12 12 2 M4 6 H20 M4 18 H20')
 elif root=='search':p(circle(10,10,7));p('M15 15 L22 22')
 elif root=='folder':p('M2 6 H9 L12 9 H22 V22 H2 Z')
 elif root in ['document','file']:p('M5 2 H14 L20 8 V22 H5 Z M14 2 V8 H20 M8 12 H17 M8 16 H17')
 elif root in ['share','copy','paste','cut','delete','edit','save','attach','more','play','pause','stop']:
  if root=='share':p(circle(5,12,2.5));p(circle(19,4,2.5));p(circle(19,20,2.5));p('M7 11 L17 5 M7 13 L17 19')
  if root=='copy':p(rect(7,7,14,15));p('M17 4 V2 H2 V17 H4')
  if root=='paste':p('M7 4 H3 V22 H21 V4 H17 M8 2 H16 V6 H8 Z')
  if root=='cut':p(circle(6,6,3));p(circle(6,18,3));p('M8 8 L21 21 M8 16 L21 3')
  if root=='delete':p('M4 6 H20 M9 3 H15 M6 6 L7 22 H17 L18 6 M10 10 V18 M14 10 V18')
  if root=='edit':p('M3 21 L5 14 L17 2 L22 7 L10 19 Z M14 5 L19 10')
  if root=='save':p('M3 2 H18 L22 6 V22 H3 Z M7 2 V9 H17 V2 M7 22 V14 H18 V22')
  if root=='attach':p('M8 8 L15 2 Q22 1 21 8 L10 20 Q3 25 2 17 L14 5 M6 16 L16 6')
  if root=='more':
   for x in [4,12,20]:p(circle(x,12,1.5),True)
  if root=='play':p('M6 2 L22 12 L6 22 Z',True)
  if root=='pause':p(rect(5,3,4,18),True);p(rect(15,3,4,18),True)
  if root=='stop':p(rect(4,4,16,16),True)
 else:raise ValueError('No authored geometry for '+name)
 if name.endswith('_off') and root not in ['wifi','cellular']:p('M2 2 L22 22')
 return list(zip(paths,fills))

NAMES=[*[f'battery_{i}' for i in range(0,101,10)],'battery_charging','battery_saver','battery_critical','battery_unknown',*[f'wifi_{i}' for i in range(5)],'wifi_off','wifi_no_internet',*[f'cellular_{i}' for i in range(5)],'cellular_off','sim','sim_off','bluetooth_on','bluetooth_off','bluetooth_connected','nfc_on','nfc_off','hotspot_on','hotspot_off','cast_on','cast_off','airplane_on','airplane_off','camera_on','camera_off','microphone_on','microphone_off','location_on','location_off','privacy','security','vpn','alarm_on','alarm_off','dnd_on','dnd_off','audio','mute','headphones','headset','vibration','download','upload','sync','usb','storage','controller','controller_off','gaming','keyboard','mouse','display_upper','display_lower','display_external','screen_swap','app_pairs','rotation','fan','fan_auto','fan_quiet','performance','performance_balanced','performance_fast','temperature','thermal_warning','power','restart','sleep','lock','lockdown','screenshot','screen_recording','home','back','forward','up','down','recents','close','check','warning','error','success','info','about','settings','system','controls','apps','app_drawer','accounts','person','accessibility','network','display','search','folder','document','share','copy','paste','cut','delete','edit','save','attach','more','play','pause','stop']
NAMES.extend(['esim','sim_warning','mobile_data_on','mobile_data_off','mobile_data_saver','network_4g','network_5g','network_lte'])

class Symbol(Asset):
 def __init__(self,name,optical):
  self.name=name;self.optical=optical;size=24 if optical=='compact' else 64
  super().__init__((name,name.replace('_',' '),size,size,''),5)
 def build(self):
  shapes=geometry(self.name);scale=self.w/24
  for group in self.layers.values():group.set('transform',f'scale({scale})')
  for d,fill in shapes:
   if self.optical=='detailed':
    path(self.b,d,'url(#steel)' if fill else 'none',stroke='#171f28',width=3.4)
    path(self.b,d,'url(#steel)' if fill else 'none',stroke='url(#steel)',width=2.5)
    path(self.g,d,'#a9b7c4' if fill else 'none',stroke='#b8c6d1',width=.7)
   else:path(self.g,d,'#c9d4de' if fill else 'none',stroke='#c9d4de',width=1.7 if fill else 2)
  # Neutral localized seam: never wash the entire status glyph orange.
  if self.optical=='detailed':path(self.s,shapes[0][0],stroke='white',width=.45,stroke_dasharray='3 19')
  return self
 def doc(self,state='master',layer=None,labels=False):
  s=super().doc(state,layer,False)
  if layer is None and state!='master':
   r=ET.fromstring(s)
   for node in list(r):
    if node.tag=='{'+SVG+'}rect' and node.get('stroke')=='#d5e7f2' or node.tag=='{'+SVG+'}path' and node.get('stroke')=='#c8d4df':r.remove(node)
   # Status glyphs are steady and keep a bounded local highlight.
   for g in r.findall('{'+SVG+'}g'):
    if g.get('id') in ['seam','core']:g.set('opacity','0' if state in ['cold','disabled'] else '.32')
    if g.get('id','').endswith('-bloom'):r.remove(g)
   s=ET.tostring(r,encoding='unicode')
  return s
def vector(name):
 ns='http://schemas.android.com/apk/res/android';ET.register_namespace('android',ns)
 r=ET.Element('vector',{f'{{{ns}}}width':'24dp',f'{{{ns}}}height':'24dp',f'{{{ns}}}viewportWidth':'24',f'{{{ns}}}viewportHeight':'24'})
 for d,fill in geometry(name):ET.SubElement(r,'path',{f'{{{ns}}}pathData':d,f'{{{ns}}}fillColor':'#C9D4DE' if fill else '#00000000',f'{{{ns}}}strokeColor':'#C9D4DE',f'{{{ns}}}strokeWidth':'1.7' if fill else '2',f'{{{ns}}}strokeLineCap':'round',f'{{{ns}}}strokeLineJoin':'round'})
 return ET.tostring(r,encoding='unicode')
def build(out):
 if out.exists():raise SystemExit('Preserved checkpoint already exists')
 for n in ['masters','layers','exports','previews','android/res/drawable','verification/evidence']:(out/n).mkdir(parents=True,exist_ok=True)
 rows=[];assets=[]
 for name in NAMES:
  (out/'android/res/drawable'/f'cg_es_{name}.xml').write_text(vector(name),encoding='utf8')
  for optical in ['compact','detailed']:
   a=Symbol(name,optical).build();a.key=name+'__'+optical;assets.append(a)
   (out/'masters'/f'{a.key}.svg').write_text(a.doc(),encoding='utf8')
   for layer in ['cold','seam','core','symbol']:
    s=a.doc(layer=layer);(out/'layers'/f'{a.key}.{layer}.svg').write_text(s,encoding='utf8')
    for d in [1,2]:(out/'exports'/f'{a.key}.{layer}@{d}x.png').write_bytes(render(s,a.w*d))
   for state in ['cold','idle','selected','disabled','reduced']:(out/'exports'/f'{a.key}.{state}.preview.png').write_bytes(render(a.doc(state),a.w*2))
   rows.append({'id':a.key,'symbol':name,'optical':optical,'size':[a.w,a.h],'layers':['cold','seam','core','symbol'],'focusOwnedByContainer':True,'nativeIntegrated':False,'deviceVerified':False})
 for start in range(0,len(NAMES),48):
  names=NAMES[start:start+48];board=Image.new('RGBA',(1800,1100),'#090e14');dr=ImageDraw.Draw(board);dr.text((35,25),f'CRAFTAGEDDON / SYSTEM SYMBOLS / {start//48+1:02}',font=font(31,True),fill='#eee7d9');dr.text((37,75),'24-unit compact + 64-unit detailed / Original semantic geometry / Steady status light',font=font(15),fill='#b5bdc6')
  for i,name in enumerate(names):
   x=30+i%8*222;y=120+i//8*155
   for optical,xx,width in [('compact',x+20,24),('detailed',x+90,64)]:
    a=Symbol(name,optical).build();im=Image.open(io.BytesIO(render(a.doc('idle'),width))).convert('RGBA');board.alpha_composite(im,(xx,y+10))
   label=name.replace('_',' ');dr.text((x+10,y+91),label[:25],font=font(12),fill='#c4d0da')
  board.convert('RGB').save(out/'previews'/f'symbols-page-{start//48+1:02}.png')
 (out/'components.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'tokens.json').write_text(json.dumps(TOKENS,indent=2)+'\n')
 (out/'README.md').write_text(f'# Iteration 05 — system symbol families\n\n{len(NAMES)} named symbols, each with separately authored compact and detailed optical treatment ({len(rows)} masters). Includes settings categories; battery/Wi-Fi/cellular state families; connectivity; privacy; audio; transfer; input; display routing; power; fan/performance; and common actions. This is defined-family coverage, not an installed-app icon collection.\n\nEvery original SVG separates cold/seam/core/symbol. Transparent PNG layers are supplied at 1x/2x. Status lighting is steady; focus belongs to the interactive container, not to the status glyph. Native XML exports contain the compact semantic geometry only. They do not reproduce detailed gradient steel, and compilation is not native integration. No unsupported device feature is implied by the availability of an icon.\n',encoding='utf8')
 print(json.dumps({'namedSymbols':len(NAMES),'opticalMasters':len(rows),'svgFiles':len(list(out.rglob('*.svg'))),'pngFiles':len(list(out.rglob('*.png'))),'androidVectors':len(NAMES)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(a.out.resolve())
