"""Specific missing motion artwork; stationary steel and moving subparts.

Draft components only. These are editable vectors and neutral masks, not a
hardware-control implementation or a physical-device acceptance result.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
from forge_library import ForgedPilot,xml
from build_pilot import add,path

ROOT=Path(__file__).resolve().parents[1]

def fan():
 o=ForgedPilot(('fan_rotor','Stationary fan cage and separate rotor',360,360,''));o.circle(180,180,151);o.circle(180,180,118)
 groups={name:add(g,'g',data_motion_part='rotor') for name,g in o.layers.items()}
 blade='M174 168 C147 126 161 83 193 76 C220 70 236 96 218 119 C204 136 197 151 194 173 Z'
 seam='M178 163 C160 128 169 94 193 87 M198 159 C204 139 215 124 221 111'
 for angle in [0,90,180,270]:
  parents={name:add(g,'g',transform=f'rotate({angle} 180 180)') for name,g in groups.items()}
  path(parents['cold'],blade,'url(#edge)',stroke='#03070b',width=3)
  path(parents['cold'],'M179 158 C167 126 173 98 192 91 C209 86 218 98 207 113 C195 130 190 143 188 164 Z','url(#forged)')
  path(parents['cold'],seam,stroke='#020509',width=4)
  for name,width in [('reflection',6),('spill',4),('seam',1.5),('core',.45)]:path(parents[name],seam,stroke='white',width=width,filter='url(#light-'+name+')' if name in ['reflection','spill'] else None)
 o.circle(180,180,29)
 return o.finish()


def knob(o,x,y,r=15):
 groups={name:add(g,'g',data_motion_part='thumb') for name,g in o.layers.items()}
 add(groups['cold'],'circle',cx=x,cy=y,r=r,fill='url(#edge)',stroke='#03070b',stroke_width=2)
 add(groups['cold'],'circle',cx=x,cy=y,r=r-4,fill='url(#forged)',stroke='#222b32',stroke_width=1)
 for name,width in [('reflection',4),('spill',3),('seam',1.1),('core',.35)]:
  add(groups[name],'circle',cx=x,cy=y,r=r-2,fill='none',stroke='white',stroke_width=width,filter='url(#light-'+name+')' if name in ['reflection','spill'] else None)

def fill_window(o,x,y,w,h,axis):
 defs=o.root.find('{http://www.w3.org/2000/svg}defs')
 clip=add(defs,'clipPath',id='value-fill-window',clipPathUnits='userSpaceOnUse')
 add(clip,'rect',x=x,y=y,width=w,height=h,data_motion_part='fill-window')
 groups={name:add(o.layers[name],'g',clip_path='url(#value-fill-window)') for name in ['cold','reflection','spill','seam','core']}
 add(groups['cold'],'rect',x=x,y=y,width=w,height=h,fill='url(#forged)')
 if axis=='y':
  for yy in range(int(y)+8,int(y+h),18):
   path(groups['cold'],f'M{x+3} {yy} H{x+w-3}',stroke='#02070b',width=5)
   for name,width in [('reflection',4),('spill',3),('seam',1.3),('core',.4)]:path(groups[name],f'M{x+5} {yy} H{x+w-5}',stroke='white',width=width,filter='url(#light-'+name+')' if name in ['reflection','spill'] else None)
 else:
  for name,width in [('reflection',6),('spill',4),('seam',2),('core',.6)]:path(groups[name],f'M{x} {y+h/2} H{x+w}',stroke='white',width=width,filter='url(#light-'+name+')' if name in ['reflection','spill'] else None)

def battery():
 o=ForgedPilot(('charge_vessel','Battery vessel with independent fill',200,300,''));o.frame(71,7,58,29);o.frame(24,30,152,255)
 add(o.b,'rect',x=59,y=63,width=82,height=182,rx=5,fill='#04080c',stroke='#3e4851',stroke_width=2)
 fill_window(o,60,64,80,180,'y');return o.finish()

def progress():
 o=ForgedPilot(('progress_vessel','Progress vessel with independent fill',360,128,''));o.frame(8,8,344,112)
 add(o.b,'rect',x=35,y=58,width=290,height=31,rx=4,fill='#04080c',stroke='#3e4851',stroke_width=2)
 fill_window(o,36,59,288,29,'x');return o.finish()

def slider():
 o=ForgedPilot(('slider_rail','Stationary rail and moving thumb',320,80,''));o.frame(7,7,306,66)
 path(o.b,'M40 40 H280',stroke='#04080c',width=10);path(o.b,'M40 40 H280',stroke='#39434b',width=2)
 fill_window(o,40,35,240,10,'x');knob(o,40,40,18);return o.finish()

def eq_band():
 o=ForgedPilot(('eq_band','Independent equalizer band',80,320,''));o.frame(6,6,68,308)
 path(o.b,'M40 40 V260',stroke='#04080c',width=9);path(o.b,'M40 40 V260',stroke='#4b565f',width=2)
 knob(o,40,260,12);return o.finish()



def mount(o,r,x,y,w,h):
 from forge_library import layer,unique
 ordinal=sum(len(g) for g in o.layers.values())
 for name in o.layers:
  q=unique(layer(r,name),f'm{ordinal}-{name}-');q.set('x',str(x));q.set('y',str(y));q.set('width',str(w));q.set('height',str(h));o.layers[name].append(q)

def emit_part(o,name,draw):
 before={key:len(g) for key,g in o.layers.items()};draw()
 for key,g in o.layers.items():
  if key in ['cold','focus']:continue
  children=list(g)[before[key]:];group=add(g,'g',data_motion_part='emit-'+name)
  for child in children:g.remove(child);group.append(child)


def control_focus(o,name,x,y,w,h):
 g=add(o.layers['focus'],'g',data_motion_part='focus-'+name)
 d=f'M{x+4} {y+12} V{y+4} H{x+12} M{x+w-12} {y+4} H{x+w-4} V{y+12} M{x+4} {y+h-12} V{y+h-4} H{x+12} M{x+w-12} {y+h-4} H{x+w-4} V{y+h-12}'
 path(g,d,stroke='white',width=1.6)
 path(o.layers['symbol'],f'M{x+w/2-6} {y+h-8} H{x+w/2+6}',stroke='white',width=1.6)

def key_rect(o,name,x,y,w,h):
 def draw():o.frame(x,y,w,h);control_focus(o,name,x,y,w,h)
 emit_part(o,name,draw)

def keyboard():
 o=ForgedPilot(('english_keyboard','English keyboard with individual key ownership',620,310,''));o.frame(5,5,610,300)
 for row,letters in enumerate(['qwertyuiop','asdfghjkl']):
  x0=22 if row==0 else 51
  for i,c in enumerate(letters):key_rect(o,'key-'+c,x0+i*58,20+row*72,54,58)
 x=25
 for c,w in [('shift',80)]+[(c,54) for c in 'zxcvbnm']+[('backspace',80)]:key_rect(o,'key-'+c,x,164,w,58);x+=w+4
 x=66
 for c,w in [('numbers',80),('space',300),('enter',100)]:key_rect(o,'key-'+c,x,236,w,58);x+=w+4
 return o.finish()

def selection():
 o=ForgedPilot(('selection_handles','Independent text selection handles',360,150,''));o.frame(18,15,324,104)
 add(o.b,'rect',x=73,y=32,width=214,height=36,fill='#35424d')
 for name,x in [('left-handle',72),('right-handle',288)]:
  groups={key:add(g,'g',data_motion_part=name) for key,g in o.layers.items()}
  path(groups['cold'],f'M{x} 36 V95',stroke='url(#edge)',width=4)
  add(groups['cold'],'circle',cx=x,cy=99,r=11,fill='url(#forged)',stroke='url(#edge)',stroke_width=2)
  for key,width in [('reflection',6),('spill',4),('seam',1.2),('core',.4)]:
   path(groups[key],f'M{x} 36 V95',stroke='white',width=width)
 return o.finish()

def copy_toolbar():
 from forge_library import symbol
 o=ForgedPilot(('copy_toolbar','Independent copy cut and paste actions',332,112,''));o.frame(4,4,324,104)
 for i,(name,icon) in enumerate([('cut','cut'),('copy','copy'),('paste','paste')]):
  x=12+i*104
  def draw(x=x,icon=icon,name=name):
   o.frame(x,10,96,64);control_focus(o,name,x,10,96,64);mount(o,symbol(icon,'detailed'),x+28,21,40,40)
  emit_part(o,name,draw)
 return o.finish()

def privacy_pill():
 from forge_library import symbol
 o=ForgedPilot(('privacy_pill','Steady camera and microphone privacy indicators',300,100,''));o.frame(5,5,290,90)
 emit_part(o,'camera',lambda:mount(o,symbol('camera_on','detailed'),34,18,64,64))
 emit_part(o,'microphone',lambda:mount(o,symbol('microphone_on','detailed'),202,18,64,64))
 path(o.b,'M150 20 V80',stroke='#35414a',width=1)
 return o.finish()

def power_actions():
 from forge_library import symbol
 o=ForgedPilot(('power_actions','Separate power restart and lockdown choices',340,300,''));o.frame(5,5,330,290)
 for i,(name,icon) in enumerate([('power','power'),('restart','restart'),('lockdown','lockdown')]):
  y=28+i*86
  def draw(y=y,icon=icon,name=name):
   o.frame(23,y,294,72);control_focus(o,name,23,y,294,72);mount(o,symbol(icon,'detailed'),38,y+13,46,46)
  emit_part(o,name,draw)
 return o.finish()

def clipboard_panel():
 from forge_library import symbol
 o=ForgedPilot(('clipboard_panel','Clipboard content and independent actions',440,250,''));o.frame(5,5,430,240);o.frame(23,23,394,112)
 for i,(name,icon) in enumerate([('copy','copy'),('share','share'),('delete','delete')]):
  x=23+i*134
  def draw(x=x,icon=icon,name=name):
   o.frame(x,155,126,64);control_focus(o,name,x,155,126,64);mount(o,symbol(icon,'detailed'),x+10,170,34,34)
  emit_part(o,name,draw)
 return o.finish()



def direction_cap():
 o=ForgedPilot(('direction_cap','Direction cap with separately oriented arrow',96,96,''));o.circle(48,48,38)
 groups={key:add(g,'g',data_motion_part='arrow') for key,g in o.layers.items()}
 d='M48 25 L66 46 H55 V68 H41 V46 H30 Z'
 path(groups['cold'],d,'url(#forged)',stroke='url(#edge)',width=2)
 for key,width in [('reflection',4),('spill',3),('seam',1.2),('core',.35)]:path(groups[key],d,stroke='white',width=width)
 return o.finish()

def activity_card():
 o=ForgedPilot(('activity_card','Activity window with title and content ownership',360,240,''));o.frame(5,5,350,230)
 path(o.b,'M20 59 H340',stroke='#35414a',width=1)
 for y,length in [(86,245),(114,190),(142,220),(170,130)]:path(o.b,f'M33 {y} H{length}',stroke='#33424d',width=5)
 o.frame(243,90,84,95);return o.finish()

def pip_card():
 from forge_library import symbol
 o=ForgedPilot(('pip_card','Picture in picture and independent playback controls',360,240,''));o.frame(5,5,350,230)
 path(o.b,'M28 144 L90 70 L149 124 L215 55 L330 144 Z','#25333d')
 before={key:len(g) for key,g in o.layers.items()}
 for i,(name,icon) in enumerate([('play','play'),('pause','pause'),('close','close')]):
  x=64+i*82
  def draw(x=x,name=name,icon=icon):
   o.frame(x,165,68,54);control_focus(o,name,x,165,68,54);mount(o,symbol(icon,'detailed'),x+18,175,32,32)
  emit_part(o,name,draw)
 for key,g in o.layers.items():
  children=list(g)[before[key]:];group=add(g,'g',data_motion_part='pip-controls')
  for child in children:g.remove(child);group.append(child)
 return o.finish()

def quick_tile(kind):
 from forge_library import symbol
 icon={'wifi':'wifi_4','bluetooth':'bluetooth_on','dnd':'dnd_on'}[kind]
 o=ForgedPilot(('quick_'+kind,'Quick setting tile '+kind,160,140,''));o.frame(5,5,150,130);mount(o,symbol(icon,'detailed'),52,21,56,56);return o.finish()

def media_option():
 import xml.etree.ElementTree as ET
 o=ForgedPilot(('media_option','Media option with geometric checked state',160,160,''));mount(o,ET.parse(ROOT/'iterations/13-forge-android-and-thor-flows/masters/media_cell.svg').getroot(),0,0,160,160)
 add(o.b,'circle',cx=131,cy=27,r=12,fill='#10171e',stroke='#5a6770',stroke_width=1)
 path(o.layers['symbol'],'M124 27 L129 32 L138 21',stroke='white',width=2.2)
 return o.finish()

def display_frame(upper):
 w,h=(384,216) if upper else (248,216);name='display_upper_frame' if upper else 'display_lower_frame'
 o=ForgedPilot((name,'Upper display' if upper else 'Lower display',w,h,''));o.frame(5,5,w-10,h-10)
 path(o.b,f'M28 58 H{w-28}',stroke='#34424c',width=1)
 for i in range(3):o.frame(25+i*(w-50)/3,82,(w-68)/3,75)
 return o.finish()

def owner_panel():
 from forge_library import symbol
 o=ForgedPilot(('owner_panel','Controller ownership panel',340,180,''));o.frame(5,5,330,170);mount(o,symbol('controller','detailed'),25,45,82,82);return o.finish()

def touch_targets():
 import xml.etree.ElementTree as ET
 o=ForgedPilot(('touch_targets','Game preview and independent mapping targets',500,300,''));o.frame(5,5,490,290)
 path(o.b,'M28 220 L100 100 L190 175 L305 82 L470 220 Z','#26333e')
 for i,(x,y) in enumerate([(90,188),(330,118),(405,178),(350,235)]):
  groups={key:add(g,'g',data_motion_part='target-'+str(i)) for key,g in o.layers.items()}
  add(groups['cold'],'circle',cx=x,cy=y,r=24,fill='url(#forged)',stroke='url(#edge)',stroke_width=2)
  path(groups['cold'],f'M{x-16} {y} H{x+16} M{x} {y-16} V{y+16}',stroke='#71818b',width=1)
  for key,width in [('reflection',5),('spill',3),('seam',1.1),('core',.35)]:add(groups[key],'circle',cx=x,cy=y,r=21,fill='none',stroke='white',stroke_width=width)
 return o.finish()

def fan_curve():
 o=ForgedPilot(('fan_curve','Fan curve with independent reveal and automatic mode',420,280,''));o.frame(5,5,410,270)
 path(o.b,'M48 42 V201 H377',stroke='#6a7780',width=1.2)
 for y in [80,120,160]:path(o.b,f'M48 {y} H377',stroke='#27343e',width=1)
 defs=o.root.find('{http://www.w3.org/2000/svg}defs');clip=add(defs,'clipPath',id='curve-window',clipPathUnits='userSpaceOnUse');add(clip,'rect',x=50,y=40,width=326,height=154,data_motion_part='curve-window')
 curve='M52 188 C110 184 125 154 170 146 S253 83 287 76 S340 60 373 49'
 for key,g in o.layers.items():
  if key in ['focus','symbol']:continue
  parent=add(g,'g',clip_path='url(#curve-window)')
  path(parent,curve,stroke='#60717d' if key=='cold' else 'white',width=3 if key=='cold' else 6 if key=='reflection' else 4 if key=='spill' else 1.4 if key=='seam' else .4)
  for x,y in [(52,188),(132,164),(220,118),(300,72),(373,49)]:add(parent,'circle',cx=x,cy=y,r=4,fill='url(#forged)' if key=='cold' else 'white')
 o.circle(358,236,13)
 return o.finish()



def hold_charge():
 import math
 o=ForgedPilot(('hold_charge','Separate long press charge arc',240,240,''));o.circle(120,120,100)
 defs=o.root.find('{http://www.w3.org/2000/svg}defs');mask=add(defs,'mask',id='charge-mask',maskUnits='userSpaceOnUse',x=0,y=0,width=240,height=240)
 add(mask,'circle',cx=120,cy=120,r=77,fill='none',stroke='white',stroke_width=30,stroke_dasharray=2*math.pi*77,stroke_dashoffset=2*math.pi*77,transform='rotate(-90 120 120)',data_motion_part='charge-arc')
 for key,width in [('reflection',6),('spill',4),('seam',2),('core',.5)]:
  group=add(o.layers[key],'g',mask='url(#charge-mask)')
  add(group,'circle',cx=120,cy=120,r=77,fill='none',stroke='white',stroke_width=width)
 return o.finish()

def scan_master(key,source=None):
 import xml.etree.ElementTree as ET
 if source:r=ET.parse(source).getroot()
 else:
  from forge_library import symbol
  o=ForgedPilot((key,'Steady face frame and independent scan light',240,240,''));o.frame(5,5,230,230);mount(o,symbol('person','detailed'),45,45,150,150);r=o.finish()
 ns='{http://www.w3.org/2000/svg}';w,h=map(float,r.get('viewBox').split()[2:]);defs=r.find(ns+'defs');clip=add(defs,'clipPath',id='scan-light-window',clipPathUnits='userSpaceOnUse')
 sweep=key=='loading_shimmer';add(clip,'rect',x=-96 if sweep else 0,y=0,width=96 if sweep else w,height=h if sweep else 30,data_motion_part='sweep-window' if sweep else 'scan-window')
 for name in ['reflection','spill','seam','core']:
  g=r.find(ns+'g[@id="'+name+'"]');children=list(g);wrapper=add(g,'g',clip_path='url(#scan-light-window)')
  for child in children:g.remove(child);wrapper.append(child)
 return r

def milestone_track():
 o=ForgedPilot(('milestone_track','Five live update milestones',420,160,''));o.frame(5,5,410,150)
 path(o.b,'M60 78 H360',stroke='#34434f',width=5)
 defs=o.root.find('{http://www.w3.org/2000/svg}defs');clip=add(defs,'clipPath',id='milestone-fill-window',clipPathUnits='userSpaceOnUse')
 add(clip,'rect',x=60,y=73,width=300,height=10,data_motion_part='milestone-window')
 for key,width in [('reflection',6),('spill',4),('seam',2),('core',.5)]:
  group=add(o.layers[key],'g',clip_path='url(#milestone-fill-window)');path(group,'M60 78 H360',stroke='white',width=width)
 for i in range(5):
  x=60+i*75;before={key:len(g) for key,g in o.layers.items()};o.circle(x,78,19)
  path(o.layers['symbol'],f'M{x-6} 104 H{x+6}',stroke='white',width=1.5)
  for key,g in o.layers.items():
   children=list(g)[before[key]:];group=add(g,'g',data_motion_part='step-'+str(i))
   for child in children:g.remove(child);group.append(child)
 return o.finish()

def thermal_meter():
 o=ForgedPilot(('thermal_meter','Fixed thermal dial and separate needle',300,220,''));o.frame(5,5,290,210)
 path(o.b,'M55 140 A95 95 0 0 1 245 140',stroke='url(#edge)',width=6)
 for key,width in [('reflection',5),('spill',4),('seam',1.4),('core',.4)]:path(o.layers[key],'M55 140 A95 95 0 0 1 245 140',stroke='white',width=width)
 for key,g in o.layers.items():
  n=add(g,'g',data_motion_part='needle')
  path(n,'M145 140 L150 65 L155 140 Z','url(#forged)' if key=='cold' else 'white',stroke='url(#edge)' if key=='cold' else 'white',width=1 if key=='cold' else .5)
 o.circle(150,140,12);return o.finish()

def trigger_meter():
 o=ForgedPilot(('trigger_meter','Analog trigger with independent travel bar',176,240,''));o.frame(5,5,166,230)
 o.symbol('M43 40 H133 L121 82 H55 Z',3)
 add(o.b,'rect',x=60,y=102,width=56,height=96,fill='#04080c',stroke='#3d4a55',stroke_width=2)
 fill_window(o,62,104,52,92,'y');return o.finish()


def build(out):
 assert not (out/'complete-assets.zip').exists(),'Packaged checkpoint is immutable';(out/'masters').mkdir(exist_ok=True);source=ROOT/'iterations/13-forge-android-and-thor-flows/source/steel-material.png';target=out/'source/steel-material.png';shutil.copy2(source,target);assert target.read_bytes()==source.read_bytes()
 
 rows=[]
 for key,constructor in [('fan_rotor',fan),('charge_vessel',battery),('progress_vessel',progress),('slider_rail',slider),('eq_band',eq_band),('english_keyboard',keyboard),('selection_handles',selection),('copy_toolbar',copy_toolbar),('privacy_pill',privacy_pill),('power_actions',power_actions),('clipboard_panel',clipboard_panel),('direction_cap',direction_cap),('activity_card',activity_card),('pip_card',pip_card),('quick_wifi',lambda:quick_tile('wifi')),('quick_bluetooth',lambda:quick_tile('bluetooth')),('quick_dnd',lambda:quick_tile('dnd')),('media_option',media_option),('display_upper_frame',lambda:display_frame(True)),('display_lower_frame',lambda:display_frame(False)),('owner_panel',owner_panel),('touch_targets',touch_targets),('fan_curve',fan_curve),('hold_charge',hold_charge),('loading_shimmer',lambda:scan_master('loading_shimmer',ROOT/'iterations/14-forge-atmosphere/masters/loading_aperture.svg')),('milestone_track',milestone_track),('thermal_meter',thermal_meter),('trigger_meter',trigger_meter),('biometric_scan',lambda:scan_master('biometric_scan',ROOT/'iterations/13-forge-android-and-thor-flows/masters/biometric_socket.svg')),('face_scan',lambda:scan_master('face_scan'))]:
  master=constructor();(out/'masters'/f'{key}.svg').write_text(xml(master),encoding='utf8')
  rows.append({'id':key,'size':[float(v) for v in master.get('viewBox').split()[2:]],'motionParts':sorted({n.get('data-motion-part') for n in master.iter() if n.get('data-motion-part')}),'nativeIntegrated':False,'deviceVerified':False,'coldSource':'Original editable geometry with unchanged existing steel material','layers':['cold','reflection','spill','seam','core','focus','symbol']})
 (out/'source/motion-composite-provenance.json').write_text(json.dumps({'components':rows,'materialSha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2)+'\n');print(json.dumps({'newDraftComponents':30,'rotorSeparateInColdAndMaskLayers':True,'fillableVesselsAndIndependentThumbs':True}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args();build(a.out.resolve())
