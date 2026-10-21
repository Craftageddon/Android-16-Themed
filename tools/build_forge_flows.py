"""Reference Forge 13: editable Android flow and Thor capability concept artwork.

No system/hardware integration. All scene values are explicit sample fixtures.
Production components remain unlabelled cold geometry plus neutral light masks.
"""
from pathlib import Path
import argparse,base64,copy,hashlib,html,io,json,math,shutil,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import el,add,path,poly,chamfer,render,font,SVG
from forge_library import ForgedPilot,lights,state,unique,xml,raster,symbol,lighting_descriptor
from build_forge_symbols import write_asset
from build_reference_forge import LAYERS

ROOT=Path(__file__).resolve().parents[1]
INK='http://www.inkscape.org/namespaces/inkscape'
EMISSION=['reflection','spill','seam','core']

def component(key):
 sizes={'pin_key':(96,88),'pattern_node':(72,72),'biometric_socket':(160,160),'volume_rail':(80,320),'app_socket':(100,100),'folder_socket':(200,160),'task_card':(240,320),'media_cell':(160,160),'suggestion':(168,64),'chord_link':(240,80),'stick_gate':(184,184),'trigger_gauge':(176,240),'mapping_slot':(240,100),'display_pair':(240,176),'thermal_gauge':(240,150),'charge_limit':(240,120),'rgb_zone':(240,120),'unavailable':(240,96)}
 w,h=sizes[key];o=ForgedPilot((key,key.replace('_',' ').title(),w,h,''))
 if key in ['pattern_node','biometric_socket','stick_gate']:
  o.circle(w/2,h/2,min(w,h)/2-10)
  if key=='pattern_node':
   o.symbol(f'M{w/2-5} {h/2} H{w/2+5} M{w/2} {h/2-5} V{h/2+5}',1.5)
  elif key=='biometric_socket':
   for r in [15,24,33,42]:
    d=f'M{w/2-r} {h/2+24} V{h/2} C{w/2-r} {h/2-r*1.5} {w/2+r} {h/2-r*1.5} {w/2+r} {h/2} V{h/2+18}'
    o.symbol(d,2)
   o.symbol(f'M{w/2} {h/2-12} V{h/2+33}',2)
  else:
   o.symbol('M45 92 H139 M92 45 V139',1.5);o.circle(92,92,22)
 elif key=='volume_rail':
  o.frame(10,6,60,308);path(o.b,'M40 35 V285',stroke='#020509',width=9)
  lights(o.layers,'M40 135 V280',3);o.circle(40,132,19)
 else:
  o.frame(6,6,w-12,h-12)
  if key=='folder_socket':
   for x,y in [(55,55),(115,55),(55,105),(115,105)]:o.frame(x,y,36,30,False)
  elif key=='task_card':
   path(o.b,'M30 66 H210 M30 268 H210',stroke='#4a535a',width=1)
   path(o.b,chamfer(32,86,176,150,8),'#171e25')
  elif key=='media_cell':
   o.symbol('M30 114 L63 70 L91 96 L115 60 L132 114 Z M42 39 h18 v18 H42 Z',2)
  elif key=='chord_link':o.symbol('M94 40 H146 M120 24 V56',2)
  elif key=='trigger_gauge':
   o.symbol('M43 43 H133 L121 85 H55 Z',3)
   for y in range(112,202,18):path(o.b,f'M44 {y} H132',stroke='#4d565d',width=2)
   lights(o.layers,'M44 184 H132 M44 166 H132 M44 148 H132',2)
  elif key=='mapping_slot':o.symbol('M38 50 H90 M76 36 L90 50 L76 64 M140 32 H200 V68 H140 Z',2)
  elif key=='display_pair':
   for y,hh in [(26,65),(105,42)]:o.frame(48,y,144,hh,False)
  elif key=='thermal_gauge':
   o.symbol('M40 106 A80 80 0 0 1 200 106 M120 106 L160 58',3)
  elif key=='charge_limit':
   o.symbol('M35 42 H195 V82 H35 Z M195 55 H207 V69 H195',2)
   lights(o.layers,'M48 62 H148',4)
  elif key=='rgb_zone':
   o.symbol('M37 60 H203',9);lights(o.layers,'M40 60 H200',3)
  elif key=='unavailable':o.symbol('M36 29 V67 M22 48 H50 M24 36 L48 60',2)
 return o.finish(),w,h

class Scene:
 def __init__(self,key,title,group,states,assets,texture,subtitle='',capability=None,roadmap=None):
  self.key=key;self.title=title;self.group=group;self.states=states;self.assets=assets;self.texture=texture
  self.w=800 if group=='thor' else 600;self.h=800 if group=='thor' else 1000;self.seq=0;self.boxes=[];self.nodes=[];self.buttons=[]
  self.meta={'id':key,'title':title,'group':group,'logicalSize':[self.w,self.h],'fixtureOnly':True,'capability':capability,'roadmap':roadmap or [],'nativeIntegrated':False,'deviceVerified':False,'textBakedIntoMasters':False,'measuredDeviceGeometry':False}
  self.root=el('svg',width=self.w,height=self.h,viewBox=f'0 0 {self.w} {self.h}')
  add(self.root,'title').text='Craftageddon / '+title
  add(self.root,'desc').text='Editable visual concept. Sample content and hardware availability fixtures only. Logical grid, not measured device dp. Production masks are separate.'
  add(self.root,'rect',width=self.w,height=self.h,fill='#080c11')
  path(self.root,f'M24 116 H{self.w-24}',stroke='#4a3b2d',width=1)
  self.text('CRAFTAGEDDON  /  '+('THOR' if group=='thor' else 'ANDROID'),30,31,13,'#a3adb6',spacing=1.4)
  self.text(title,30,79,30,bold=True)
  captions={'app-drawer':'Browse your apps','folder-open':'Your saved shortcuts','widget-picker':'Choose a widget for your home screen','search-results':'Apps and settings','search-empty':'Apps and settings','settings-home':'Personalize your device','settings-display':'Brightness, appearance and text','recents-overview':'Switch between your open apps','recents-empty':'Your recent apps','power-menu':'Choose an action','permission-camera':'Camera access','privacy-dashboard':'Review recent app access','photo-picker':'Choose what to share','file-picker':'Browse documents','file-picker-error':'Choose another location or try again','share-sheet':'Choose how to share','clipboard-history':'Recent copies','screenshot-editor':'Crop, mark up and save a copy','volume-output':'Choose where sound plays','lock-pin':'Enter your device PIN','lock-pattern':'Unlock your device','lock-biometric':'Verify your identity','keyboard-symbols':'Write a message','keyboard-numbers':'Write a message','split-layout':'Arrange your apps','thor-trigger-modes':'Choose how your triggers respond','thor-remap':'Customize your button actions','thor-virtual-mouse':'Control the pointer with your controller','thor-touch-mapping':'Place your on-screen targets','thor-profiles':'Choose a profile for your game','thor-profile-readback':'Review applied and skipped preferences','thor-display-controls':'Adjust each display separately','thor-keyboard-target':'Choose where to type','thor-lid-resume':'Choose what happens on close and wake','thor-capture':'Choose what to capture','thor-performance':'Balance your game and cooling preferences','thor-thermal-warning':'Automatic protection is active','thor-charge-limit':'Manage supported charging options','thor-rgb-zones':'Choose a steady ember preset','thor-diagnostics':'Check sticks, triggers and buttons','thor-controls-unavailable':'Supported controls could not be found','input-prompts':'Direction, tap, hold and chord examples'}
  self.meta['designNotes']=subtitle
  if subtitle:self.text(captions.get(key,subtitle),32,103,15,'#b5bdc6')
  self.text('Design preview  /  sample states',30,self.h-22,13,'#8f9ba7')
  path(self.root,f'M{self.w/2-35} {self.h-40} H{self.w/2+35}',stroke='#7f8b94',width=3)
 def text(self,s,x,y,size=18,color='#eee7d9',bold=False,anchor='start',spacing=0):
  f=font(size,bold);width=f.getlength(s)+max(0,len(s)-1)*spacing
  left=x-width/2 if anchor=='middle' else x-width if anchor=='end' else x
  assert left>=12 and left+width<=self.w-12,(self.key,s,left,width,self.w)
  # Text boxes are recorded independently of any bitmap composition.
  n=add(self.root,'text',x=x,y=y,font_size=size,fill=color,font_family='Segoe UI, sans-serif',font_weight=700 if bold else 400,text_anchor=anchor,letter_spacing=spacing)
  n.text=s;self.boxes.append({'text':s,'bounds':[round(left,2),y-size,round(width,2),size+4]})
  return n
 def paragraph(self,s,x,y,width,size=17,color='#b5bdc6'):
  line=''
  for word in s.split():
   candidate=(line+' '+word).strip()
   if font(size).getlength(candidate)>width and line:self.text(line,x,y,size,color);y+=size+9;line=word
   else:line=candidate
  if line:self.text(line,x,y,size,color);y+=size+9
  return y
 def place(self,r,x,y,w,h,st='off',owner=None):
  self.seq+=1
  for g in r.findall('{'+SVG+'}g'):
   if g.get('id') in LAYERS:g.set('data-forge-layer',g.get('id'))
  q=unique(state(r,self.states[st]),f's{self.seq}-');q.set('x',str(x));q.set('y',str(y));q.set('width',str(w));q.set('height',str(h));q.set('data-state',st)
  if owner:q.set('data-owner',owner)
  self.root.append(q);self.nodes.append({'owner':owner or 'decoration','state':st,'bounds':[x,y,w,h]});return q
 def frame(self,x,y,w,h,st='off',owner=None):
  o=ForgedPilot(('frame','Frame',w,h,''));o.frame(5,5,w-10,h-10)
  return self.place(o.finish(),x,y,w,h,st,owner)
 def asset(self,key,x,y,scale=1,st='off',owner=None):
  r,w,h=self.assets[key];return self.place(copy.deepcopy(r),x,y,w*scale,h*scale,st,owner or key)
 def icon(self,name,x,y,size=42,st='off'):
  return self.place(symbol(name,'detailed'),x,y,size,size,st,name)
 def button(self,label,x,y,w=240,selected=False,focused=False,disabled=False):
  st='disabled' if disabled else 'selected_focused' if selected and focused else 'on' if selected else 'focused_off' if focused else 'off'
  self.frame(x,y,w,64,st,label);self.text(label,x+w/2,y+39,18,'#8f9ba7' if disabled else '#eee7d9',True,'middle')
  self.buttons.append({'label':label,'state':st,'bounds':[x,y,w,64]})
 def row(self,title,detail,y,icon='settings',on=False,value='',x=24,w=None,disabled=False):
  w=w or self.w-48;self.frame(x,y,w,92,'off',title);self.icon(icon,x+18,y+23,44,'off')
  self.text(title,x+80,y+35,21,bold=True);self.text(detail,x+80,y+62,15,'#8f9ba7' if disabled else '#b5bdc6')
  if value:self.text(value,x+w-28,y+41,17,'#b5bdc6',anchor='end')
  else:
   o=ForgedPilot(('ring','State',44,44,''));o.circle(22,22,17)
   self.place(o.finish(),x+w-65,y+24,44,44,'on' if on and not disabled else 'off',title+' state')
   if on and not disabled:self.text('✓',x+w-43,y+54,18,anchor='middle')
 def message(self,title,body,icon='info',y=270):
  self.icon(icon,self.w/2-46,y,92)
  self.text(title,self.w/2,y+139,26,bold=True,anchor='middle')
  self.paragraph(body,70,y+180,self.w-140,18)
 def app(self,label,icon,x,y,selected=False):
  self.asset('app_socket',x,y,1,'on' if selected else 'off',label);self.icon(icon,x+25,y+25,50)
  self.text(label,x+50,y+125,16,anchor='middle')
 def media(self,x,y,w,h,selected=False,variant=0):
  self.frame(x,y,w,h,'on' if selected else 'off','Media selection')
  # Original editable placeholder illustration, not a photo or user data.
  g=add(self.root,'g',data_content='editable-media-placeholder')
  path(g,poly([(x+20,y+h-25),(x+w*.42,y+h*.42),(x+w*.64,y+h*.70),(x+w*.78,y+h*.36),(x+w-20,y+h-25)]),['#2b3943','#303d38','#39363e'][variant%3])
  add(g,'circle',cx=x+w*.28,cy=y+h*.29,r=min(w,h)*.09,fill='#89938d')
  if selected:self.text('✓',x+w-29,y+37,20,anchor='middle')
 def finish(self,out):
  self.meta.update(textBoxes=self.boxes,artworkOwners=self.nodes,actions=self.buttons)
  (out/'screens'/f'{self.key}.svg').write_text(xml(self.root),encoding='utf8')
  im=raster(self.root,self.w,self.texture);im.save(out/'screens'/f'{self.key}.png')
  cold=copy.deepcopy(self.root)
  for n in cold.iter():
   if n.get('data-forge-layer') in EMISSION:n.set('opacity','0')
  (out/'inspections'/f'{self.key}.cold-material.svg').write_text(xml(cold),encoding='utf8')
  raster(cold,self.w,self.texture).save(out/'inspections'/f'{self.key}.cold-material.png')
  return self.meta

def android(scenes,new):
 s=new('app-drawer','App library','android','Browse, search and organize',roadmap=['ES-040'])
 s.frame(24,140,552,72);s.icon('search',40,157,36);s.text('Search apps',96,185,21,'#b5bdc6')
 for i,(name,ico) in enumerate([('Games','gaming'),('Files','folder'),('Settings','settings'),('Gallery','apps'),('Browser','network'),('Music','audio'),('Camera','camera_on'),('Clock','alarm_on'),('Notes','document'),('Recorder','microphone_on'),('Terminal','system'),('Tools','controls')]):s.app(name,ico,30+i%4*146,245+i//4*185,i==0)
 s.text('A–Z',32,895,16,'#b5bdc6');s.text('12 sample apps',568,895,16,'#b5bdc6',anchor='end')
 s=new('folder-open','Games folder','android','Editable folder and app housings',roadmap=['ES-040'])
 s.frame(24,150,552,650);s.text('Games',60,205,25,bold=True);s.icon('edit',500,173,40)
 for i,(n,k) in enumerate([('Library','gaming'),('Streaming','cast_on'),('Arcade','controller'),('Emulator','system'),('Companion','display_lower'),('Add app','apps')]):s.app(n,k,65+i%3*185,250+i//3*210,i==0)
 s.button('Close folder',165,838,270)
 s=new('widget-picker','Widgets','android','Preview sizes before adding',roadmap=['ES-040'])
 s.frame(24,150,552,232);s.text('Clock',58,198,22,bold=True);s.text('10:24',58,300,64,bold=True);s.text('Wednesday, 21 October',60,342,18,'#b5bdc6')
 s.frame(24,410,552,218);s.text('Now playing',58,462,22,bold=True);s.icon('audio',56,493,76);s.text('Select your music',158,535,24);s.text('2 × 2 preview',158,570,17,'#b5bdc6')
 s.button('Add clock',24,668,264,True,True);s.button('Cancel',312,668,264)
 s=new('search-results','Search','android','Apps and settings',roadmap=['ES-040','ES-042'])
 s.frame(24,145,552,74);s.text('display',56,192,23);s.icon('close',510,166,32)
 for i,(t,d,k) in enumerate([('Display','Brightness, text and color','display'),('Screen routing','Upper and lower display','screen_swap'),('Display companion','App','display_lower')]):s.row(t,d,245+i*112,k,value='›')
 s=new('search-empty','Search','android','No matching apps or settings',roadmap=['ES-040','ES-042'])
 s.frame(24,145,552,74);s.text('unmatched query',56,192,23)
 s.message('No results','Try a shorter name or another keyword. Your apps and settings are still available from their home pages.','search')
 s.button('Clear search',150,650,300)
 s=new('settings-home','Settings','android','Quiet text wells, cold category artwork',roadmap=['ES-042'])
 for i,(t,d,k) in enumerate([('Network & internet','Wi-Fi, connectivity','network'),('Connected devices','Bluetooth, USB, controllers','bluetooth_on'),('Display','Brightness, text, screen routing','display'),('Sound & vibration','Volume, outputs, feedback','audio'),('Privacy & security','Permissions, lock and privacy','privacy'),('Apps & storage','Installed apps and files','apps')]):s.row(t,d,145+i*118,k,value='›')
 s=new('settings-display','Display','android','Sample settings; value labels stay live',roadmap=['ES-042'])
 s.row('Adaptive brightness','Adjust for available light',145,'display',on=True)
 s.frame(24,260,552,170);s.text('Brightness',58,308,22,bold=True);s.text('65%',540,308,20,anchor='end')
 path(s.root,'M64 368 H532',stroke='#46515a',width=7);path(s.root,'M64 368 H368',stroke='#bdc4c8',width=5)
 s.asset('pattern_node',332,332,1,'on');s.row('Text size','Default',460,'accessibility',value='›');s.row('Dark appearance','Ember Steel',572,'display',on=True)
 s.button('Preview text',24,720,552)
 s=new('recents-overview','Recent apps','android','Select a task or close it',roadmap=['ES-045'])
 for x,n,k,st in [(36,'Game library','gaming','on'),(314,'Files','folder','off')]:
  s.asset('task_card',x,210,1,st,n);s.icon(k,x+87,310,66);s.text(n,x+120,460,20,anchor='middle');s.icon('close',x+190,225,30)
 s.button('Clear all',174,650,252);s.text('Selected task opens on confirmation',300,770,16,'#b5bdc6',anchor='middle')
 s=new('recents-empty','Recent apps','android','Empty state',roadmap=['ES-045'])
 s.message('All clear','Open an app and it will appear here for quick switching.','recents');s.button('Go home',150,655,300)
 s=new('power-menu','Power controls','android','Selection lights only the chosen action',roadmap=['ES-043'])
 for i,(label,ico) in enumerate([('Power off','power'),('Restart','restart'),('Lockdown','lockdown'),('Cancel','close')]):
  x=32+i%2*280;y=205+i//2*240;s.frame(x,y,256,210,'selected_focused' if i==1 else 'off',label);s.icon(ico,x+86,y+32,84);s.text(label,x+128,y+159,23,bold=True,anchor='middle')
 s=new('permission-camera','Camera permission','android','Platform-owned prompt visual concept',roadmap=['ES-047'])
 s.frame(24,185,552,650);s.icon('camera_on',250,220,100);s.text('Allow camera access?',300,377,27,bold=True,anchor='middle')
 s.paragraph('Sample Camera needs the camera to take a picture. Choose when access is allowed.',68,425,464,19)
 s.button('While using the app',56,555,488,True,True);s.button('Only this time',56,635,488);s.button('Do not allow',56,715,488)
 s=new('privacy-dashboard','Privacy','android','Recent access and permission entry points',roadmap=['ES-047'])
 for i,(t,d,k) in enumerate([('Camera','Sample Camera · just now','camera_on'),('Microphone','Sample Recorder · 18 min ago','microphone_on'),('Location','No recent access','location_on')]):s.row(t,d,160+i*118,k,value='›')
 s.frame(24,550,552,170);s.text('You control access',60,600,24,bold=True);s.paragraph('Review each app before changing its permissions. Denied access stays denied until you choose otherwise.',60,640,480,18)
 s=new('photo-picker','Choose photos','android','Selected media only / sample thumbnails',roadmap=['ES-048'])
 s.text('Recent',32,165,22,bold=True);s.text('2 selected',568,165,18,'#b5bdc6',anchor='end')
 for i in range(9):s.media(24+i%3*188,195+i//3*190,176,174,i in [0,4],i)
 s.button('Add 2 photos',24,815,352,True,True);s.button('Cancel',392,815,184)
 s=new('file-picker','Choose a file','android','Document provider list',roadmap=['ES-048'])
 s.frame(24,145,552,72);s.icon('folder',42,160,40);s.text('Downloads',104,190,22)
 for i,(n,d) in enumerate([('Game notes.txt','Text document · sample'),('Save backup.zip','Archive · sample'),('Screenshot.png','Image · sample'),('Profile.json','Document · sample')]):s.row(n,d,245+i*115,'document',value='›')
 s.button('Cancel',174,785,252)
 s=new('file-picker-error','Storage unavailable','android','Recoverable provider error',roadmap=['ES-048'])
 s.message('Could not open storage','The document provider did not respond. Retry, or choose another location. No file was selected.','error')
 s.button('Retry',24,665,264,True,True);s.button('Other location',312,665,264)
 s=new('share-sheet','Share screenshot','android','Sample destinations; choose before sending',roadmap=['ES-046'])
 s.media(24,155,552,220);s.text('Screenshot.png',42,418,23,bold=True);s.text('Choose an app',32,490,20,'#b5bdc6')
 for i,(n,k) in enumerate([('Save file','folder'),('Notes','document'),('Nearby','share')]):s.app(n,k,54+i*194,525)
 s.button('Copy image',24,750,264);s.button('Cancel',312,750,264)
 s=new('clipboard-history','Clipboard','android','Editable sample entries',roadmap=['ES-049'])
 for i,(t,d) in enumerate([('Game notes','Remember the display layout.'),('Link','https://example.org/sample'),('Profile name','Evening session')]):
  s.frame(24,160+i*165,552,145,'on' if i==0 else 'off',t);s.text(t,58,203+i*165,22,bold=True);s.text(d,58,246+i*165,18,'#b5bdc6');s.icon('paste',504,185+i*165,40)
 s.button('Clear history',24,720,552)
 s=new('screenshot-editor','Edit screenshot','android','Crop handles and markup controls',roadmap=['ES-050'])
 s.media(24,155,552,510);path(s.root,'M64 235 H536 V585 H64 Z',stroke='#c2d0d9',width=1.5)
 for x,y in [(64,235),(536,235),(64,585),(536,585)]:path(s.root,f'M{x-10} {y} H{x+10} M{x} {y-10} V{y+10}',stroke='#e6e7de',width=3)
 for i,(n,k) in enumerate([('Crop','cut'),('Draw','edit'),('Undo','back')]):s.icon(k,65+i*190,710,54,'on' if i==0 else 'off');s.text(n,92+i*190,792,18,anchor='middle')
 s.button('Save copy',24,845,264,True,True);s.button('Cancel',312,845,264)
 s=new('volume-output','Sound output','android','Live volume and route labels',roadmap=['ES-052'])
 s.asset('volume_rail',48,180,1,'on');s.text('Media',88,555,19,anchor='middle');s.text('60%',88,591,25,bold=True,anchor='middle')
 s.row('Speakers','Selected output',185,'audio',on=True,x=160,w=416);s.row('Headphones','Not connected',300,'headphones',x=160,w=416,disabled=True);s.row('Bluetooth','Choose a device',415,'bluetooth_on',value='›',x=160,w=416)
 s.row('Mute media','Off',660,'mute',on=False);s.button('Done',174,810,252)
 s=new('lock-pin','Enter PIN','android','Credential visual study / sample entry',roadmap=['ES-044'])
 s.icon('lock',265,142,70);s.text('Unlock',300,261,28,bold=True,anchor='middle');s.text('● ● ○ ○ ○ ○',300,319,25,anchor='middle')
 for i,n in enumerate(['1','2','3','4','5','6','7','8','9','','0','⌫']):
  if n:
   x=112+i%3*140;y=368+i//3*115;s.asset('pin_key',x,y,1,'selected_focused' if n=='5' else 'off');s.text(n,x+48,y+55,30,bold=True,anchor='middle')
 s.button('Emergency',174,866,252)
 s=new('lock-pattern','Draw pattern','android','Sample path lights only chosen nodes',roadmap=['ES-044'])
 s.icon('lock',268,150,64);s.text('Draw your pattern',300,283,27,bold=True,anchor='middle')
 path(s.root,'M156 416 L300 416 L444 560 L300 704',stroke='#89969e',width=3)
 for i in range(9):s.asset('pattern_node',120+i%3*144,380+i//3*144,1,'on' if i in [0,1,5,7] else 'off')
 s.button('Use PIN',174,836,252)
 s=new('lock-biometric','Unlock','android','Platform authentication visual concept',roadmap=['ES-044'])
 s.asset('biometric_socket',220,260,1,'on');s.text('Touch the sensor',300,495,28,bold=True,anchor='middle');s.paragraph('Use your enrolled biometric or enter your device PIN.',84,550,432,20);s.button('Use PIN',150,710,300)
 for key,title,lines in [('keyboard-symbols','Symbols keyboard',['! @ # $ % ^ & * ( )','~ ` _ - + = { } [ ]',': ; " \' < > ? / |']),('keyboard-numbers','Numbers keyboard',['1 2 3','4 5 6','7 8 9','. 0 ⌫'])]:
  s=new(key,title,'android','Labels and suggestions remain editable',roadmap=['ES-051']);s.frame(24,160,552,190);s.text('Message',56,210,19,'#b5bdc6');s.text('A sample entry…',56,268,25)
  for i,n in enumerate(['Steel','Ember','Forge']):s.asset('suggestion',30+i*190,408,1,'on' if i==0 else 'off');s.text(n,114+i*190,448,19,anchor='middle')
  numeric=key=='keyboard-numbers';y=492 if numeric else 510
  for row in lines:
   labels=row.split();ww=(552-(len(labels)-1)*5)/len(labels)
   for i,n in enumerate(labels):s.frame(24+i*(ww+5),y,ww,72 if numeric else 78);s.text(n,24+i*(ww+5)+ww/2,y+46,22,anchor='middle')
   y+=84 if numeric else 94
  footer=846 if numeric else 822
  s.button('ABC',24,footer,128);s.button('Space',166,footer,248);s.button('Enter',428,footer,148,True,True)
 s=new('split-layout','Choose layout','android','Logical window arrangements',roadmap=['ES-054'])
 for i,(n,k) in enumerate([('Side by side','app_pairs'),('Stacked','display'),('Single app','apps')]):s.row(n,'Preview arrangement',165+i*128,k,on=i==0)
 s.frame(24,590,552,220);s.frame(44,610,246,180);s.frame(310,610,246,180);s.text('App 1',168,709,24,anchor='middle');s.text('App 2',432,709,24,anchor='middle');s.button('Use layout',150,848,300,True,True)

def thor(scenes,new):
 cap='Illustrative supported case; hardware service and physical mapping unverified'
 def panel(key,title,subtitle='Supported-case concept',ids=None):return new(key,title,'thor',subtitle,capability=cap,roadmap=ids or [])
 s=panel('thor-trigger-modes','Trigger modes',ids=['TH-004'])
 for x,n,st in [(60,'Left trigger','off'),(500,'Right trigger','on')]:s.asset('trigger_gauge',x,170,1,st);s.text(n,x+88,451,23,bold=True,anchor='middle')
 s.button('Analog',40,510,224,True,True);s.button('Digital',288,510,224);s.button('Default',536,510,224);s.paragraph('Analog triggers use the full trigger range. Digital mode treats each trigger as a button.',44,630,712,19)
 s=panel('thor-remap','Button mapping',ids=['TH-004','TH-001'])
 for i,(n,d) in enumerate([('A','Primary action'),('B','Back / cancel'),('L1','Shoulder action'),('R1','Shoulder action')]):s.row(n,d,150+i*115,'controller',value='Edit')
 s.button('Save profile',40,650,344,True,True);s.button('Restore defaults',416,650,344)
 s=panel('thor-virtual-mouse','Virtual mouse',ids=['TH-006'])
 s.row('Virtual mouse','Enabled for this sample profile',150,'mouse',on=True);s.asset('stick_gate',74,285,1,'on');s.text('Pointer',166,508,22,anchor='middle')
 s.frame(318,285,458,230);s.text('Right stick',352,334,24,bold=True);s.text('Move pointer',352,374,21);s.text('Primary action · click',352,421,19,'#b5bdc6');s.text('Back action · exit capture',352,462,19,'#b5bdc6');s.row('Pointer speed','Medium',550,'mouse',value='›')
 s=panel('thor-touch-mapping','Touch mapping',ids=['TH-007'])
 s.frame(24,148,752,365);s.text('Sample game surface',400,200,24,anchor='middle');s.asset('stick_gate',90,265,1,'on');s.asset('pin_key',580,320,1,'on');s.text('A',628,375,30,bold=True,anchor='middle');s.text('Drag handles to place targets',400,480,18,'#b5bdc6',anchor='middle')
 s.button('Save layout',24,550,352,True,True);s.button('Release capture',400,550,376);s.paragraph('Save this layout for the current game. Release capture to return control to your device.',40,665,720,18)
 s=panel('thor-profiles','Game profiles',ids=['TH-008','TH-009'])
 for i,(n,d) in enumerate([('Evening session','Sample Game · selected'),('Quiet session','Sample Game · saved'),('Default','All other apps')]):s.row(n,d,155+i*132,'gaming',on=i==0)
 s.button('Preview changes',24,600,352,True,True);s.button('New profile',400,600,376)
 s=panel('thor-profile-readback','Profile result','Mixed-result example',ids=['TH-009'])
 s.row('Display layout','Applied and read back',150,'success',value='Applied');s.row('Input layout','Applied and read back',267,'controller',value='Applied');s.row('Fan preference','Service unavailable; unchanged',384,'fan',value='Skipped',disabled=True)
 s.paragraph('Two preferences were applied and confirmed. The fan preference was skipped and keeps its previous value.',44,545,712,19);s.button('Review skipped',24,645,352,True,True);s.button('Restore previous',400,645,376)
 s=panel('thor-display-controls','Displays',ids=['TH-012'])
 for x,n,v,st in [(24,'Upper display','70%','on'),(412,'Lower display','40%','off')]:
  s.frame(x,150,364,320,st,n);s.icon('display_upper' if x==24 else 'display_lower',x+126,180,112);s.text(n,x+182,335,24,bold=True,anchor='middle');s.text(v,x+182,387,36,bold=True,anchor='middle')
 s.row('Linked brightness','Off · adjust each display separately',500,'display',on=False);s.button('Keyboard destination',24,640,752)
 s=panel('thor-keyboard-target','Keyboard destination',ids=['TH-012'])
 s.row('Focused app','Follow the current text field',170,'keyboard',on=True);s.row('Upper display','Choose before opening the keyboard',295,'display_upper');s.row('Lower display','Choose before opening the keyboard',420,'display_lower');s.button('Use selection',224,600,352,True,True)
 s=panel('thor-lid-resume','Lid & resume',ids=['TH-013'])
 s.row('When the lid closes','Sleep',150,'sleep',value='›');s.row('On resume','Restore previous layout',270,'screen_swap',on=True);s.row('Active input capture','Ask before resuming after wake',390,'controller',on=True);s.paragraph('Your layout will return when the device wakes. Input capture will wait for your confirmation.',44,550,712,19);s.button('Done',224,650,352)
 s=panel('thor-capture','Capture displays',ids=['TH-014'])
 for i,(n,k) in enumerate([('Upper','display_upper'),('Lower','display_lower'),('Both','app_pairs')]):
  x=24+i*256;s.frame(x,165,240,300,'selected_focused' if i==2 else 'off',n);s.icon(k,x+55,205,130);s.text(n,x+120,412,24,bold=True,anchor='middle')
 s.button('Take screenshot',24,525,352,True,True);s.button('Recording options',400,525,376);s.paragraph('Both displays are selected. Review your screenshot before sharing it.',40,655,720,18)
 s=panel('thor-performance','Performance & cooling',ids=['TH-015'])
 s.asset('thermal_gauge',36,150,1,'off');s.text('Sample: 42°C',156,337,22,anchor='middle');s.row('Balanced','Selected performance mode',155,'performance_balanced',on=True,x=315,w=461)
 s.row('Automatic fan','Selected cooling policy',275,'fan_auto',on=True,x=315,w=461);s.row('Quiet fan','Available sample mode',395,'fan_quiet',x=315,w=461);s.paragraph('Automatic cooling adjusts to demand. Thermal protection may override your preferences when needed.',40,570,720,19);s.button('Restore automatic',24,650,752)
 s=panel('thor-thermal-warning','Cooling required','Warning state / sample values',ids=['TH-015'])
 s.message('Let the device cool','Thermal protection has priority over your profile. Performance changes are temporarily unavailable in this sample state.','thermal_warning',170);s.button('Keep automatic cooling',100,610,600)
 s=panel('thor-charge-limit','Charging preferences',ids=['TH-016'])
 s.asset('charge_limit',280,160,1,'on');s.row('Charge limit','Sample target: 80%',325,'battery_charging',on=True);s.row('Charging bypass','Unavailable',445,'usb',disabled=True);s.paragraph('The selected charge limit applies while connected to power. Charging bypass is unavailable in this example.',40,585,720,19)
 s=panel('thor-rgb-zones','Lighting zones',ids=['TH-017'])
 s.asset('rgb_zone',80,180,1,'on');s.asset('rgb_zone',480,180,1,'off');s.text('Left · ember',200,343,24,anchor='middle');s.text('Right · off',600,343,24,anchor='middle');s.row('Link zones','Off',405,'controls');s.row('Effect','Steady ember · selected preset',525,'settings',on=True)
 s=panel('thor-diagnostics','Controller diagnostics','Sample input fixture / no live device',ids=['TH-003','TH-018'])
 s.asset('stick_gate',66,160,1,'off');s.asset('stick_gate',335,160,1,'on');s.text('Left X 0.00 / Y 0.00',158,390,18,anchor='middle');s.text('Right X 0.25 / Y 0.00',427,390,18,anchor='middle');s.asset('trigger_gauge',610,155,.78,'on');s.text('RT 0.50',678,390,19,anchor='middle');s.row('Button input','A · sample pressed',440,'controller',on=True);s.button('Reset sample',24,610,352);s.button('Calibration guide',400,610,376)
 s=panel('thor-controls-unavailable','Controls unavailable','Unverified hardware / safe visual fallback',ids=['TH-004','TH-006','TH-007','TH-015','TH-016','TH-017','TH-018'])
 s.meta['capability']='Unavailable fixture; all feature controls cold, no active toggle'
 for i,(n,d,k) in enumerate([('Input features','No compatible input service','controller'),('Cooling & performance','No supported hardware values','fan'),('Charge controls','No supported charging service','battery_unknown'),('Lighting zones','No supported lighting service','controls')]):s.row(n,d,145+i*118,k,value='Unavailable',disabled=True)
 s.button('View requirements',224,650,352)

def prompt_sheet(out,assets,states,texture):
 # Direction glyphs are live scene geometry; no physical event code is invented.
 s=Scene('input-prompts','Input prompt language','thor',states,assets,texture,'Directions, tap, hold and chord / logical mapping only',roadmap=['TH-001','TH-002','TH-005'])
 for i,(n,angle) in enumerate([('Up',0),('Up-right',45),('Right',90),('Down-right',135),('Down',180),('Down-left',225),('Left',270),('Up-left',315)]):
  x=28+i%4*194;y=150+i//4*155;s.asset('pin_key',x+42,y,1,'selected_focused' if i==2 else 'off',n)
  d=path(s.root,'M0 14 V-14 M-10 -4 L0 -14 L10 -4',stroke='#d1d7d8',width=3);d.set('transform',f'translate({x+90} {y+44}) rotate({angle})');s.text(n,x+90,y+120,17,anchor='middle')
 for i,(n,label) in enumerate([('Tap','A'),('Hold','B'),('Chord','L + R'),('Capture','Menu')]):
  x=28+i*194;s.frame(x,505,176,96,'on' if i==1 else 'off',n);s.text(label,x+88,563,24,bold=True,anchor='middle');s.text(n,x+88,642,19,anchor='middle')
 s.text('Prompt labels are examples; confirm physical mappings before use.',400,710,17,'#b5bdc6',anchor='middle')
 return s

def sheets(out,metadata):
 for group in ['android','thor']:
  rows=[m for m in metadata if m['group']==group]
  for start in range(0,len(rows),9):
   part=rows[start:start+9];tw=340 if group=='android' else 440;th=650 if group=='android' else 520;cols=3
   board=Image.new('RGB',(cols*tw+40,math.ceil(len(part)/cols)*th+125),'#080c11');d=ImageDraw.Draw(board)
   d.text((24,18),f'REFERENCE FORGE 13 / {group.upper()} / {start//9+1:02}',font=font(27,True),fill='#eee7d9');d.text((24,63),'Editable concept scenes / cold steel with state-owned ember layers / sample data',font=font(17),fill='#b5bdc6')
   for i,m in enumerate(part):
    x=20+i%cols*tw;y=112+i//cols*th;im=Image.open(out/'screens'/f"{m['id']}.png").convert('RGBA');im.thumbnail((tw-22,th-95),Image.Resampling.LANCZOS);board.paste(im,(x+(tw-22-im.width)//2,y),im)
    d.text((x+5,y+th-73),m['title'],font=font(17,True),fill='#eee7d9');d.text((x+5,y+th-43),m['id'],font=font(12),fill='#a8b5c0')
   board.save(out/'previews'/f'{group}-screens-{start//9+1:02}.png')
 # Cold material inspection vs actual sample scene, clearly separate from off-value geometry.
 board=Image.new('RGB',(1640,1040),'#080c11');d=ImageDraw.Draw(board);d.text((25,18),'COLD MATERIAL / SELECTED EMBER',font=font(31,True),fill='#eee7d9')
 for col,key in enumerate(['settings-display','thor-trigger-modes']):
  for row,folder in enumerate(['inspections','screens']):
   file=key+('.cold-material.png' if folder=='inspections' else '.png');im=Image.open(out/folder/file).convert('RGBA');im.thumbnail((770,420),Image.Resampling.LANCZOS)
   x=25+col*820;y=130+row*450;board.paste(im,(x+(770-im.width)//2,y),im)
   d.text((x,y-36),'Light layers hidden (inspection)' if row==0 else 'Selected/on sample lighting',font=font(21),fill='#b5bdc6')
 board.save(out/'previews/cold-and-selected-scenes.png')

def build(out,resume=False,only=None):
 assert not out.exists() or (resume and not (out/'complete-assets.zip').exists()),'Existing packaged checkpoints are immutable'
 for sub in ['source','masters','exports','previews','screens','inspections','verification/evidence']:(out/sub).mkdir(parents=True,exist_ok=True)
 inp=ROOT/'iterations/11-forge-symbol-library/source'
 for f in ['steel-material.png','steel-material-original.png']:shutil.copy2(inp/f,out/'source'/f)
 shutil.copy2(ROOT/'iterations/12-forge-controls-and-screens/runtime-style.json',out/'runtime-style.json');shutil.copy2(ROOT/'tools/state_driver_v2.cjs',out/'source/state_driver_v2.cjs')
 provenance={'date':'2026-10-21','newRasterGeneration':False,'method':'Original editable geometry using unchanged existing cold material through SVG patterns. No generated source repainted.','inputs':[{'file':f,'sha256':hashlib.sha256((out/'source'/f).read_bytes()).hexdigest(),'from':'iterations/11-forge-symbol-library/source/'+f,'modified':False} for f in ['steel-material.png','steel-material-original.png']]}
 (out/'source/material-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 style=json.loads((out/'runtime-style.json').read_text());states=style['sampleStates'];texture=base64.b64encode((out/'source/steel-material.png').read_bytes()).decode();assets={};rows=[]
 for key in ['pin_key','pattern_node','biometric_socket','volume_rail','app_socket','folder_socket','task_card','media_cell','suggestion','chord_link','stick_gate','trigger_gauge','mapping_slot','display_pair','thermal_gauge','charge_limit','rgb_zone','unavailable']:
  r,w,h=component(key);assets[key]=(r,w,h)
  if resume:rows.append(next(v for v in json.loads((out/'components.json').read_text()) if v['id']==key))
  else:rows.append(write_asset(out,key,r,states,[w,w*2],texture,metadata={'type':'flow-component','canonicalId':key+'_off' if key=='unavailable' else key,'size':[w,h],'labelsBaked':False,'fixedAspect':True}))
  print('component',key,flush=True)
 scenes=[]
 def new(key,title,group,subtitle='',**kw):
  s=Scene(key,title,group,states,assets,texture,subtitle,**kw);scenes.append(s);return s
 android(scenes,new);thor(scenes,new);scenes.append(prompt_sheet(out,assets,states,texture));metadata=[]
 old={r['id']:r for r in json.loads((out/'screens/layout-metadata.json').read_text())} if only else {}
 for s in scenes:
  if only and s.key not in only:metadata.append(old[s.key]);continue
  metadata.append(s.finish(out));print('scene',s.key,flush=True)
 (out/'components.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'screens/layout-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
 sheets(out,metadata)
 cards='\n'.join(f'<article data-group="{m["group"]}" data-name="{html.escape(m["title"].lower())}"><h2>{html.escape(m["title"])}</h2><img loading="lazy" src="screens/{m["id"]}.png" alt="{html.escape(m["title"])} sample scene"><p>{m["group"].title()} · visual concept</p><a href="screens/{m["id"]}.svg">Editable SVG</a> · <a href="inspections/{m["id"]}.cold-material.png">Cold material inspection</a></article>' for m in metadata)
 (out/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Craftageddon — Reference Forge 13</title><style>body{background:#080c11;color:#eee7d9;font:18px system-ui;margin:30px}h1{font-size:32px}p{color:#b5bdc6;max-width:80ch}input,select{background:#161e26;color:#eee7d9;border:1px solid #737a7e;padding:14px;font:inherit;margin:8px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}article{border:1px solid #4a3b2d;padding:16px}h2{font-size:21px}img{width:100%;height:440px;object-fit:contain;background:#080c11}a{color:#d7e1e8}article[hidden]{display:none}</style><h1>Reference Forge 13</h1><p>Android flows and Thor panels. Cold steel when off; separate ember lighting when selected or on. Sample scenes only. Thor feature availability and physical mappings are unverified.</p><label>Find a screen <input id="search" type="search"></label><label>Collection <select id="group"><option value="all">All screens</option><option value="android">Android</option><option value="thor">Thor</option></select></label><p id="count" aria-live="polite"></p><main>'''+cards+'''</main><script>const search=document.querySelector('#search'),group=document.querySelector('#group'),cards=[...document.querySelectorAll('article')];function filter(){let n=0;for(const card of cards){card.hidden=!(card.dataset.name.includes(search.value.toLowerCase())&&(group.value==='all'||group.value===card.dataset.group));if(!card.hidden)n++}document.querySelector('#count').textContent=n+' screens shown'}search.addEventListener('input',filter);group.addEventListener('change',filter);filter();</script></html>''',encoding='utf8')
 coverage={'iteration':13,'sceneCount':len(metadata),'componentMasters':len(rows),'scope':'New editable flow concepts, not production OS integration','roadmapEvidence':{k:[m['id'] for m in metadata if k in m['roadmap']] for k in sorted({k for m in metadata for k in m['roadmap']})},'remaining':['Full permission variants, deny/revoke outcomes, picker empty and provider states','PIN rejection/lockout, biometric failure/unavailable and pattern errors','Complete IME interaction, suggestion rejection and alternate language layouts','Thor per-feature unavailable/pending/error/apply/restore/capture arbitration and recording variants','Wallpapers, boot/recovery/loading, full charging scenes and motion','Installed-app-specific icons and retained historical source reconciliation','Native SystemUI/launcher/IME/settings integration, device accessibility and performance']}
 (out/'coverage-map.json').write_text(json.dumps(coverage,indent=2)+'\n')
 print(json.dumps({'scenes':len(metadata),'masters':len(rows),'output':str(out)}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--resume-scenes',action='store_true',help='Rebuild only draft scene layouts after review; never rewrites a packaged checkpoint');p.add_argument('--scene',action='append',help='Only re-render named scenes during an unpackaged draft review');a=p.parse_args();assert not a.scene or a.resume_scenes;build(a.out.resolve(),a.resume_scenes,a.scene)
