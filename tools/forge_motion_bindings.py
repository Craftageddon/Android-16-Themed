"""Explicit retained-atlas dispositions for the current motion redesign.

None means a specific composite still needs artwork; never substitute a generic
panel and count it as completed. Mapped masters still need playback review.
"""
from pathlib import Path

FOLDERS={11:'11-forge-symbol-library',12:'12-forge-controls-and-screens',13:'13-forge-android-and-thor-flows',14:'14-forge-atmosphere',16:'16-forge-motion'}
def icon(name):return (11,name+'__detailed.svg')
def control(name):return (12,'control-'+name+'.svg')
def pilot(name):return (12,'pilot-'+name+'.svg')
def flow(name):return (13,name+'.svg')
def atmosphere(name):return (14,name+'.svg')

MAP={
 'Sigil':{1:atmosphere('forge_crest'),2:atmosphere('loading_aperture'),5:(11,'hero-power_core.svg'),6:icon('restart')},
 'Status':{1:icon('info'),2:icon('success'),3:icon('warning'),4:icon('error'),8:flow('biometric_socket'),9:control('focus_boundary')},
 'Controls':{1:atmosphere('loading_aperture'),2:atmosphere('loading_aperture'),3:(12,'scalable-notification.svg'),4:control('dialog'),5:pilot('quick_tile'),6:control('button_primary'),7:None,8:flow('pattern_node'),9:flow('task_card')},
 'Connectivity':{1:(11,'hero-wifi.svg'),2:icon('bluetooth_on'),3:icon('cellular_4'),4:icon('hotspot_on'),5:icon('airplane_on'),6:icon('vpn'),7:(11,'hero-cast.svg'),8:icon('play'),9:icon('screen_recording')},
 'Navigation':{1:icon('back'),2:icon('home'),3:flow('task_card'),4:flow('display_pair'),5:flow('task_card'),6:icon('rotation'),7:flow('task_card'),8:None,9:control('bottom_sheet')},
 'Surfaces':{1:flow('folder_socket'),2:control('card'),3:icon('sync'),4:icon('accounts'),5:control('card'),6:atmosphere('wallpaper-phone-quiet'),7:icon('audio'),8:icon('display'),9:(12,'scalable-panel.svg')},
 'Input':{1:flow('pattern_node'),2:flow('stick_gate'),3:icon('forward'),4:control('keyboard_letter'),5:None,6:None,7:icon('person'),8:icon('lock'),9:icon('vibration')},
 'Thor':{1:flow('display_pair'),2:icon('display_upper'),3:icon('display_lower'),4:icon('screen_swap'),5:None,6:flow('stick_gate'),7:pilot('controller_prompts'),8:control('shoulder_cap'),9:control('controller_cap')},
 'Performance':{1:(16,'fan_rotor.svg'),2:flow('rgb_zone'),3:icon('fan_quiet'),4:icon('performance_balanced'),5:icon('performance_fast'),6:flow('thermal_gauge'),7:(11,'hero-power_core.svg'),8:icon('usb'),9:icon('display_external')},
 'AndroidSystem':{1:control('toast'),2:control('progress_half'),3:None,4:control('notification_compact'),5:None,6:None,7:flow('media_cell'),8:None,9:control('dialog')},
 'AndroidWindowing':{1:None,2:None,3:flow('task_card'),4:pilot('navigation'),5:None,6:None,7:None,8:atmosphere('loading_aperture'),9:flow('biometric_socket')},
 'ThorAdvanced':{1:None,2:pilot('gaming_menu'),3:None,4:None,5:flow('trigger_gauge'),6:None,7:None,8:flow('rgb_zone'),9:None},
}

PENDING={
 ('Controls',7):'Separate stationary forged rail and movable thumb; existing half-slider bakes thumb geometry into one master.',
 ('Navigation',8):'Compact English keyboard assembly with live key labels and separate key-press ownership.',
 ('Input',5):'Two independently anchored text-selection handles, with live selection region.',
 ('Input',6):'Copy/cut/paste toolbar assembly with distinct action slots.',
 ('Thor',5):'Four-way direction pad with independently selected direction and stationary surround.',
 ('Performance',1):'Stationary fan cage and separately rotating rotor in both cold and neutral-mask layers.',
 ('AndroidSystem',3):'Privacy pill with camera and microphone indicators; active icons stay steady.',
 ('AndroidSystem',5):'Power menu assembly and separate action ownership.',
 ('AndroidSystem',6):'Independent volume channels/knobs with live values; no fake audio-route backend.',
 ('AndroidSystem',8):'Clipboard preview and separate live action toolbar.',
 ('AndroidWindowing',1):'Source and destination activity cards for predictive back commit.',
 ('AndroidWindowing',2):'Same two-card gesture returning to original bounds on cancellation.',
 ('AndroidWindowing',5):'PiP media card with independently revealed live controls.',
 ('AndroidWindowing',6):'Three-tile edit tray with actual nonoverlapping reorder slots.',
 ('AndroidWindowing',7):'Embedded media grid with selected item marks and live selection count.',
 ('ThorAdvanced',1):'Separate upper/lower screen assemblies with explicit hinge pivot.',
 ('ThorAdvanced',3):'Device/game controller ownership view with neutral focus transfer.',
 ('ThorAdvanced',4):'Touch-mapping preview targets and independent binding slots; capability stays fixture-only.',
 ('ThorAdvanced',6):'Independent two-display destinations and dragged application card.',
 ('ThorAdvanced',7):'Fan-curve points plus independent selected automatic-mode indicator.',
 ('ThorAdvanced',9):'Five independently moving EQ bars/knobs with live values.',
}

NEUTRAL_FOCUS={'accessibility-focus','dual-screen-focus-transfer','controller-focus-transfer','permission-emphasis'}
STEADY_STATUS={'wi-fi-state','bluetooth-state','cellular-signal','hotspot-broadcast','airplane-mode','vpn-tunnel','cast-external-display','camera-microphone-privacy','screen-recording','top-display-wake','bottom-display-wake'}
INSIDE_LABELS={'lock-screen-aod-pulse','notification-arrival','heads-up-lifecycle','expand-collapse','action-button-press','silent-notification','toast-snackbar','tile-activate-deactivate','internet-detail-panel','edge-to-edge-window','widget-pickup-drop','bottom-sheet-rise-dismiss','dialog-destructive-confirm','key-press','suggestion-chip','permission-emphasis','accessibility-focus','live-update-status-chip','permission-choice-panel','desktop-window-open'}

def bind(recipe,repo):
 layers=[];pending=[]
 for old in recipe['legacyLayers']:
  atlas,cell=old['atlas'],old['cell'];entry=MAP[atlas][cell] if atlas not in ['Battery','Progress'] else None
  if atlas in ['Battery','Progress']:
   reason='Live '+atlas.lower()+' fill, fixed percentage bounds and stationary vessel; requires an actual neutral fill mask, not clipping the whole cold assembly.';pending.append(reason);source=None
  elif entry is None:reason=PENDING[(atlas,cell)];pending.append(reason);source=None
  else:
   version,name=entry;source=repo/'iterations'/FOLDERS[version]/'masters'/name;assert source.is_file(),source;source=source.relative_to(repo).as_posix()
  layers.append({'legacyAtlas':atlas,'legacyCell':cell,'source':source,'legacyPlacement':{'x':old['x'],'y':old['y'],'scale':old['scale']},'playbackReviewed':False,'status':'NEEDS_COMPOSITE_ARTWORK' if source is None else 'SOURCE_MAPPED_PLAYBACK_PENDING'})
  if source and source.endswith('/fan_rotor.svg'):layers[-1]['transformTarget']='rotor'

 if recipe['id'] in ['battery-charging','low-battery-warning','charging-direct-power']:
  old=next(l for l in recipe['legacyLayers'] if l['atlas']=='Battery');target=old['cell']/100
  vessel={'source':'iterations/16-forge-motion/masters/charge_vessel.svg','legacyPlacement':{'x':old['x'],'y':old['y'],'scale':old['scale']},'targetFill':target,'startFill':target if recipe['kind']=='Warn' else 0,'motionParts':[{'part':'fill-window','mode':'fill-y','x':60,'bottom':244,'width':80,'height':180}],'liveLabels':[{'format':'percent','x':100,'y':270,'fontSize':22}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}
  layers=[vessel]+([layers[1]] if recipe['id']=='charging-direct-power' else []);pending=[]
 if recipe['id']=='progress-notification':
  layers=[{'source':'iterations/16-forge-motion/masters/progress_vessel.svg','legacyPlacement':{'x':0,'y':0,'scale':1},'targetFill':.76,'startFill':0,'motionParts':[{'part':'fill-window','mode':'fill-x','x':36,'y':59,'width':288,'height':29}],'liveLabels':[{'format':'percent','x':180,'y':43,'fontSize':24}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id'] in ['brightness-slider','volume-slider']:
  old=recipe['legacyLayers'][0];target=.6 if recipe['id']=='brightness-slider' else .42
  layers=[{'source':'iterations/16-forge-motion/masters/slider_rail.svg','legacyPlacement':{'x':8,'y':12,'scale':.9},'targetFill':target,'startFill':.18,'motionParts':[{'part':'fill-window','mode':'fill-x','x':40,'y':35,'width':240,'height':10},{'part':'thumb','mode':'move-x','range':240}],'liveLabels':[{'format':'percent','x':160,'y':110,'fontSize':22}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'},layers[-1]];pending=[]
  layers[-1]['legacyPlacement']={'x':-95,'y':12,'scale':.26};layers[-1]['stationary']=True
 if recipe['id']=='five-band-eq-preset':
  layers=[]
  for i,(title,target) in enumerate(zip(['Bass','Low mids','Mids','High mids','Treble'],[.30,.65,.50,.80,.40])):
   gain=round(target*20-10);value=('+' if gain>0 else '')+str(gain)+' dB'
   layers.append({'source':'iterations/16-forge-motion/masters/eq_band.svg','legacyPlacement':{'x':(i-2)*38,'y':0,'scale':.9},'targetFill':target,'startFill':.5,'motionParts':[{'part':'thumb','mode':'move-y','range':-220}],'liveLabels':[{'text':title,'x':40,'y':342,'fontSize':18},{'format':'gain','x':40,'y':298,'fontSize':18}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'})
  pending=[]


 if recipe['id']=='keyboard-ime-slide':
  labels=[];owners=[]
  for row,letters in enumerate(['qwertyuiop','asdfghjkl']):
   x0=22 if row==0 else 51
   for i,c in enumerate(letters):labels.append({'text':c,'x':x0+i*58+27,'y':58+row*72,'fontSize':22});owners.append(c)
  x=25
  for name,text,w in [('shift','Shift',80)]+[(c,c,54) for c in 'zxcvbnm']+[('backspace','Back',80)]:
   labels.append({'text':text,'x':x+w/2,'y':202,'fontSize':20});owners.append(name);x+=w+4
  x=66
  for name,text,w in [('numbers','123',80),('space','Space',300),('enter','Enter',100)]:
   labels.append({'text':text,'x':x+w/2,'y':274,'fontSize':22});owners.append(name);x+=w+4
  layers=[{'source':'iterations/16-forge-motion/masters/english_keyboard.svg','legacyPlacement':{'x':0,'y':8,'scale':1.4},'liveLabels':labels,'motionParts':[{'part':prefix+'key-'+name,'mode':'opacity','value':1 if name=='a' else 0} for prefix in ['emit-','focus-'] for name in owners],'sampleSelectedKey':'a','playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='text-selection-handles':
  layers=[{'source':'iterations/16-forge-motion/masters/selection_handles.svg','legacyPlacement':{'x':0,'y':0,'scale':1.2},'stationary':True,'liveLabels':[{'text':'Craftageddon','x':180,'y':59,'fontSize':24}],'motionParts':[{'part':'left-handle','mode':'travel-x','from':108,'to':0},{'part':'right-handle','mode':'travel-x','from':-108,'to':0}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='copy-paste-toolbar':
  layers=[{'source':'iterations/16-forge-motion/masters/copy_toolbar.svg','legacyPlacement':{'x':0,'y':0,'scale':1.25},'liveLabels':[{'text':word,'x':60+i*104,'y':96,'fontSize':20} for i,word in enumerate(['Cut','Copy','Paste'])],'motionParts':[{'part':prefix+name,'mode':'opacity','value':1 if name=='copy' else 0} for prefix in ['emit-','focus-'] for name in ['cut','copy','paste']],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='camera-microphone-privacy':
  layers=[{'source':'iterations/16-forge-motion/masters/privacy_pill.svg','legacyPlacement':{'x':0,'y':0,'scale':.9},'liveLabels':[{'text':'In use','x':150,'y':121,'fontSize':21}],'motionParts':[{'part':'emit-camera','mode':'opacity','value':1},{'part':'emit-microphone','mode':'opacity','value':1}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='power-menu':
  layers=[{'source':'iterations/16-forge-motion/masters/power_actions.svg','legacyPlacement':{'x':0,'y':0,'scale':1},'liveLabels':[{'text':word,'x':196,'y':73+i*86,'fontSize':24} for i,word in enumerate(['Power off','Restart','Lockdown'])],'motionParts':[{'part':prefix+name,'mode':'opacity','value':1 if name=='restart' else 0} for prefix in ['emit-','focus-'] for name in ['power','restart','lockdown']],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='clipboard-overlay':
  labels=[{'text':'Copied text','x':220,'y':62,'fontSize':24},{'text':'Circuit ready','x':220,'y':108,'fontSize':21}]
  labels.extend({'text':word,'x':100+i*134,'y':195,'fontSize':18} for i,word in enumerate(['Copy','Share','Clear']))
  layers=[{'source':'iterations/16-forge-motion/masters/clipboard_panel.svg','legacyPlacement':{'x':0,'y':0,'scale':1.2},'liveLabels':labels,'motionParts':[{'part':prefix+name,'mode':'opacity','value':1 if name=='copy' else 0} for prefix in ['emit-','focus-'] for name in ['copy','share','delete']],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='expanded-volume-mixer':
  layers=[]
  for i,(name,target) in enumerate(zip(['Media','Ring','Alarm'],[.6,.35,.7])):
   layers.append({'source':'iterations/16-forge-motion/masters/eq_band.svg','legacyPlacement':{'x':(i-1)*45,'y':0,'scale':1},'targetFill':target,'startFill':target,'motionParts':[{'part':'thumb','mode':'move-y','range':-220}],'liveLabels':[{'text':name,'x':40,'y':342,'fontSize':18},{'format':'percent','x':40,'y':298,'fontSize':18}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'})
  pending=[]


 if recipe['id']=='d-pad-direction-press':
  layers=[]
  for i,(word,x,y,angle) in enumerate([('Up',0,-50,0),('Right',50,0,90),('Down',0,50,180),('Left',-50,0,270)]):
   layers.append({'source':'iterations/16-forge-motion/masters/direction_cap.svg','legacyPlacement':{'x':x,'y':y,'scale':1},'displaySize':[84,84],'selected':i==0,'stationary':i!=0,'focusable':i==0,'liveLabels':[{'text':word,'x':48,'y':116,'fontSize':18}],'motionParts':[{'part':'arrow','mode':'fixed-rotate','angle':angle,'cx':48,'cy':48}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'})
  pending=[]
 if recipe['id'] in ['predictive-back-activity','predictive-back-cancel']:
  layers=[]
  for role,title in [('back-target','Library'),('back-source','Sample game')]:
   layers.append({'source':'iterations/16-forge-motion/masters/activity_card.svg','legacyPlacement':{'x':0,'y':0,'scale':1},'displaySize':[340,227],'semanticRole':role,'focusable':role=='back-source','liveLabels':[{'text':title,'x':180,'y':43,'fontSize':24,**({'showAtCommit':True} if role=='back-target' and recipe['id']=='predictive-back-activity' else {'opacity':0} if role=='back-target' else {})}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'})
  pending=[]
 if recipe['id']=='pip-controls-reveal':
  layers=[{'source':'iterations/16-forge-motion/masters/pip_card.svg','legacyPlacement':{'x':0,'y':0,'scale':1},'stationary':True,'motionParts':[{'part':'pip-controls','mode':'opacity','from':0,'to':1}]+[{'part':prefix+name,'mode':'opacity','value':1 if name=='play' else 0} for prefix in ['emit-','focus-'] for name in ['play','pause','close']],'controlLabels':['Play','Pause','Close'],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='quick-settings-edit-tray':
  layers=[]
  for i,(key,title,target) in enumerate([('wifi','Wi-Fi',2),('bluetooth','Bluetooth',0),('dnd','Quiet',1)]):
   layers.append({'source':'iterations/16-forge-motion/masters/quick_'+key+'.svg','legacyPlacement':{'x':(i-1)*72,'y':0,'scale':1},'displaySize':[116,102],'semanticRole':'reorder-tile','fromSlot':i,'toSlot':target,'slotStep':144,'dragged':i==0,'selected':i==0,'focusable':i==0,'liveLabels':[{'text':title,'x':80,'y':115,'fontSize':19}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'})
  pending=[]
 if recipe['id']=='embedded-photo-picker':
  layers=[]
  for i in range(6):
   labels=[{'format':'selectionCount','count':2,'x':278.620689655,'y':-36,'fontSize':22}] if i==0 else []
   layers.append({'source':'iterations/16-forge-motion/masters/media_option.svg','legacyPlacement':{'x':(i%3-1)*72,'y':-35+i//3*70,'scale':1},'displaySize':[116,116],'selected':i in [0,4],'focusable':i==0,'liveLabels':labels,'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'})
  pending=[]
 if recipe['id']=='hinge-posture-angle':
  layers=[{'source':'iterations/16-forge-motion/masters/display_upper_frame.svg','legacyPlacement':{'x':0,'y':-42.5,'scale':1},'displaySize':[280,158],'semanticRole':'hinge-upper','pivot':[192,216],'liveLabels':[{'text':'Upper','x':192,'y':42,'fontSize':24}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'},{'source':'iterations/16-forge-motion/masters/display_lower_frame.svg','legacyPlacement':{'x':0,'y':36.25,'scale':1},'displaySize':[181,158],'stationary':True,'pivot':[124,0],'liveLabels':[{'text':'Lower','x':124,'y':42,'fontSize':24},{'format':'angle','x':124,'y':243,'fontSize':22}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='controller-focus-transfer':
  layers=[]
  for i,title in enumerate(['Device control','Game control']):
   layers.append({'source':'iterations/16-forge-motion/masters/owner_panel.svg','legacyPlacement':{'x':0,'y':-46+i*92,'scale':.85},'stationary':True,'liveLabels':[{'text':title,'x':211,'y':99,'fontSize':24}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'})
  pending=[]
 if recipe['id']=='touch-mapping-editor':
  layers=[{'source':'iterations/16-forge-motion/masters/touch_targets.svg','legacyPlacement':{'x':0,'y':0,'scale':1.4},'motionParts':[{'part':'target-'+str(i),'mode':'emission','value':1 if i==0 else 0} for i in range(4)],'liveLabels':[{'text':'A','x':90,'y':196,'fontSize':20},{'text':'B','x':330,'y':126,'fontSize':20},{'text':'X','x':405,'y':186,'fontSize':20},{'text':'Y','x':350,'y':243,'fontSize':20}],'capabilityFixture':True,'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='dual-screen-app-drag':
  layers=[{'source':'iterations/16-forge-motion/masters/display_upper_frame.svg','legacyPlacement':{'x':0,'y':-52.5,'scale':1},'displaySize':[260,147],'stationary':True,'selected':False,'focusable':False,'liveLabels':[{'text':'Upper','x':192,'y':42,'fontSize':24}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'},{'source':'iterations/16-forge-motion/masters/display_lower_frame.svg','legacyPlacement':{'x':0,'y':47.5,'scale':1},'displaySize':[168,147],'stationary':True,'selected':False,'focusable':False,'liveLabels':[{'text':'Lower','x':124,'y':42,'fontSize':24}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'},{'source':'iterations/16-forge-motion/masters/activity_card.svg','legacyPlacement':{'x':0,'y':-43.5,'scale':1},'displaySize':[100,67],'semanticRole':'screen-drag-card','liveLabels':[],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='fan-curve-auto-mode':
  layers=[{'source':'iterations/16-forge-motion/masters/fan_curve.svg','legacyPlacement':{'x':0,'y':0,'scale':1.2},'stationary':True,'targetFill':1,'startFill':0,'motionParts':[{'part':'curve-window','mode':'fill-x','x':50,'y':40,'width':326,'height':154}],'liveLabels':[{'text':'Fan speed','x':110,'y':29,'fontSize':18},{'text':'Temperature','x':210,'y':224,'fontSize':18},{'text':'Auto','x':300,'y':243,'fontSize':22}],'capabilityFixture':True,'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]


 if recipe['id']=='long-press':
  import math
  layers=[{'source':'iterations/16-forge-motion/masters/hold_charge.svg','legacyPlacement':{'x':0,'y':0,'scale':1},'stationary':True,'motionParts':[{'part':'charge-arc','mode':'stroke-arc','length':2*math.pi*77}],'liveLabels':[{'text':'Hold','x':120,'y':130,'fontSize':24}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='loading-shimmer-sync':
  layers=[{'source':'iterations/16-forge-motion/masters/loading_shimmer.svg','legacyPlacement':{'x':0,'y':0,'scale':.9},'stationary':True,'motionParts':[{'part':'sweep-window','mode':'sweep-x','size':512,'band':96}],'liveLabels':[{'text':'Syncing','x':256,'y':276,'fontSize':32}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='live-update-milestones':
  labels=[{'text':str(i+1),'x':60+i*75,'y':85,'fontSize':20} for i in range(5)]+[{'format':'milestone','count':3,'total':5,'x':210,'y':135,'fontSize':21}]
  parts=[{'part':'milestone-window','mode':'fill-x','x':60,'y':73,'width':300,'height':10}]+[{'part':'step-'+str(i),'mode':'step-emission','index':i,'count':5} for i in range(5)]
  layers=[{'source':'iterations/16-forge-motion/masters/milestone_track.svg','legacyPlacement':{'x':0,'y':0,'scale':1.2},'stationary':True,'targetFill':.5,'startFill':0,'motionParts':parts,'liveLabels':labels,'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='thermal-throttling-state':
  layers=[{'source':'iterations/16-forge-motion/masters/thermal_meter.svg','legacyPlacement':{'x':0,'y':0,'scale':1},'stationary':True,'targetFill':.78,'startFill':.2,'motionParts':[{'part':'needle','mode':'needle','cx':150,'cy':140,'minAngle':-70,'maxAngle':70}],'liveLabels':[{'text':'Thermal limit','x':150,'y':31,'fontSize':20},{'format':'temperature','x':150,'y':188,'fontSize':24}],'capabilityFixture':True,'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='analog-trigger-calibration':
  layers=[]
  for i,(title,target) in enumerate([('Left trigger',1),('Right trigger',.72)]):
   layers.append({'source':'iterations/16-forge-motion/masters/trigger_meter.svg','legacyPlacement':{'x':-53+i*106,'y':0,'scale':.9},'stationary':True,'targetFill':target,'startFill':0,'motionParts':[{'part':'fill-window','mode':'fill-y','x':62,'bottom':196,'width':52,'height':92}],'liveLabels':[{'text':title,'x':88,'y':28,'fontSize':18},{'format':'percent','x':88,'y':219,'fontSize':20}],'capabilityFixture':True,'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'})
  pending=[]
 if recipe['id'] in ['fingerprint-authentication','face-scan-framing']:
  face=recipe['id']=='face-scan-framing';size=240 if face else 160
  layers=[{'source':'iterations/16-forge-motion/masters/'+('face_scan.svg' if face else 'biometric_scan.svg'),'legacyPlacement':{'x':0,'y':0,'scale':1},'stationary':True,'motionParts':[{'part':'scan-window','mode':'sweep-y','size':size,'band':30}],'liveLabels':[],'capabilityFixture':True,'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='system-update-cycle':
  layers=[{'source':'iterations/11-forge-symbol-library/masters/sync__detailed.svg','legacyPlacement':{'x':0,'y':-45,'scale':1},'displaySize':[120,120],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'},{'source':'iterations/16-forge-motion/masters/progress_vessel.svg','legacyPlacement':{'x':0,'y':55,'scale':1},'stationary':True,'targetFill':.76,'startFill':0,'motionParts':[{'part':'fill-window','mode':'fill-x','x':36,'y':59,'width':288,'height':29}],'liveLabels':[{'format':'percent','x':180,'y':43,'fontSize':24}],'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}];pending=[]
 if recipe['id']=='face-button-cluster':
  layers=[]
  for i,letter in enumerate('ABXY'):
   layers.append({'source':'iterations/16-forge-motion/masters/direction_cap.svg','legacyPlacement':{'x':(i-1.5)*43,'y':0,'scale':1},'displaySize':[64,64],'selected':i==0,'stationary':i!=0,'focusable':i==0,'motionParts':[{'part':'arrow','mode':'opacity','value':0}],'liveLabels':[{'text':letter,'x':48,'y':56,'fontSize':24}],'buttonOrderFixture':True,'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'})
  pending=[]

 if recipe['id'] in ['boot-crest-assembly','restart-reignition']:
  source='iterations/14-forge-atmosphere/masters/'+('forge_crest.svg' if recipe['id']=='boot-crest-assembly' else 'charge_chamber.svg')
  # One exact aligned body, seam and core assembly; never stack unrelated full
  # emblems on top of one another and obscure the approved cold silhouette.
  layers=[{'source':source,'allowedLayers':allowed,'legacyPlacement':{'x':0,'y':0,'scale':.92},'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'} for allowed in [['cold','focus','symbol'],['reflection','spill','seam'],['core']]]
 if recipe['id']=='shutdown-collapse':layers=[{'source':'iterations/14-forge-atmosphere/masters/forge_crest.svg','legacyPlacement':{'x':0,'y':0,'scale':.92},'playbackReviewed':False,'status':'SOURCE_MAPPED_PLAYBACK_PENDING'}]
 result={'id':recipe['id'],'kind':recipe['kind'],'durationMillis':recipe['durationMillis'],'repeat':recipe['repeat'],'label':None if any(l.get('liveLabels') for l in layers) else recipe['label'],'labelAnchor':'inside' if recipe['id'] in INSIDE_LABELS else 'below','labelLayer':len(layers)-1 if recipe['id']=='permission-emphasis' else 0,'authoredLocale':'en-US','focusNeutralOnly':recipe['id'] in NEUTRAL_FOCUS,'steadyStatus':recipe['id'] in STEADY_STATUS,'newLayers':layers,'pendingArtwork':pending,'status':'PENDING','nativeIntegrated':False,'deviceVerified':False}

 result['originalKind']=recipe['kind'];result['originalTitle']=recipe['title']
 result['disposition']='steady-status' if recipe['id'] in STEADY_STATUS else 'animated'
 result['dispositionReason']='Confirmed status glyph stays steady; container/in-flight effects belong to their own controls.' if recipe['id'] in STEADY_STATUS else 'Dedicated geometry/mask timeline with lifecycle and reduced-motion ownership.'
 if recipe['id'] in ['rgb-breathing-cycle','rgb-mode-color-select']:
  result['title']='Ember breathing cycle' if recipe['id']=='rgb-breathing-cycle' else 'Ember lighting selection'
  result['description']='Selected lighting uses separate ember-intensity masks. Cold steel and hue stay fixed; reduced motion is steady.'
 if result['label'] and result['labelAnchor']=='inside':
  import xml.etree.ElementTree as ET
  index=result['labelLayer'];layer=layers[index];w,h=map(float,ET.parse(repo/layer['source']).getroot().get('viewBox').split()[2:]);limits=layer.get('displaySize',[340,260]);s=min(limits[0]/w,limits[1]/h)*layer['legacyPlacement']['scale']
  layer.setdefault('liveLabels',[]).append({'text':result['label'],'x':w/2,'y':h/2+8/s,'fontSize':24/s});result['label']=None
 return result
