"""Forge 15: missing journey states, editable scene sources and an offline flow viewer.

All capability, permission, authentication and hardware results are fixtures.
The viewer changes design scenes only; it never invokes a native device action.
"""
from pathlib import Path
import argparse,base64,copy,hashlib,html,json,math,shutil,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import add,path,font,SVG
from build_forge_flows import Scene
from forge_library import xml

ROOT=Path(__file__).resolve().parents[1]

class FlowScene(Scene):
 def __init__(self,key,title,group,states,assets,texture,subtitle='',**kw):
  super().__init__(key,title,group,states,assets,texture,subtitle,**kw);self.links=[];self.meta['authoredLocale']='en-US'
 def action(self,id,label,target,x,y,w=240,**kw):
  self.button(label,x,y,w,**kw);self.links.append({'id':id,'label':label,'target':target,'bounds':[x,y,w,64]})
 def text(self,s,x,y,size=18,color='#eee7d9',bold=False,anchor='start',spacing=0):
  assert all(not c.isalpha() or c.isascii() for c in s),'Authored UI text must be English'
  return super().text(s,x,y,size,color,bold,anchor,spacing)
 def finish(self,out):
  self.meta.update(flowActions=self.links,textBoxes=self.boxes,artworkOwners=self.nodes,actions=self.buttons)
  cold=copy.deepcopy(self.root)
  for n in cold.iter():
   if n.get('data-forge-layer') in ['reflection','spill','seam','core']:n.set('opacity','0')
  normal=out/'screens'/f'{self.key}.svg';inspection=out/'inspections'/f'{self.key}.cold-material.svg'
  if normal.exists() and inspection.exists() and normal.with_suffix('.png').exists() and inspection.with_suffix('.png').exists() and normal.read_text(encoding='utf8')==xml(self.root) and inspection.read_text(encoding='utf8')==xml(cold):return self.meta
  return super().finish(out)

def spec(id,title,family,kind,subtitle,body='',icon='info',actions=None,**extra):
 return {'id':id,'title':title,'family':family,'kind':kind,'subtitle':subtitle,'body':body,'icon':icon,'actions':actions or [],**extra}

def definitions():
 # Targets are explicit state ids, never device commands or external destinations.
 r=[]
 def s(*args,**kw):r.append(spec(*args,**kw))
 s('permission-request','Camera access','permission','permission','Choose when this app may use your camera',icon='camera_on',actions=[('allow','While using the app','permission-allowed'),('once','Only this time','permission-once'),('deny','Do not allow','permission-denied')])
 s('permission-allowed','Camera permission','permission','message','Access follows your choice','Camera access is allowed while Sample Camera is in use. You can change this in Settings.','camera_on',[('revoke','Remove access','permission-revoked'),('again','Review choices','permission-request')])
 s('permission-once','One-time access','permission','message','Temporary camera permission','Access lasts for the current session. Closing the session removes access.','camera_on',[('close','End session','permission-revoked'),('review','Review choices','permission-request')])
 s('permission-denied','Camera access denied','permission','message','You can keep using other features','The camera remains unavailable. You can retry the request or review this app in Settings.','camera_off',[('retry','Try again','permission-request'),('settings','Open app settings','permission-settings')])
 s('permission-settings','App permissions','permission','settings','Review Sample Camera access',actions=[('request','Review camera choice','permission-request'),('revoke','Remove access','permission-revoked')])
 s('permission-revoked','Access removed','permission','message','Camera permission is off','Camera access is removed. Other features remain available.','privacy',[('request','Request access again','permission-request')])
 s('location-choice','Location access','location','location','Choose accuracy and duration',icon='location_on',actions=[('precise','Use precise location','location-precise'),('approx','Use approximate','location-approximate'),('deny','Do not allow','location-denied')])
 s('location-precise','Location permission','location','message','Precise location selected','Location is allowed while Sample Maps is in use. You can switch to approximate location or remove access.','location_on',[('change','Change choice','location-choice'),('revoke','Remove access','location-denied')])
 s('location-approximate','Location permission','location','message','Approximate location selected','Sample Maps receives an approximate location while in use.','location_on',[('change','Change choice','location-choice'),('revoke','Remove access','location-denied')])
 s('location-denied','Location access off','location','message','Your choice has been kept','No location is shared. You can choose again when a feature needs it.','location_off',[('review','Review choices','location-choice')])
 s('notification-permission','Notifications','notifications','permission','Allow Sample Game to send notifications?',icon='alarm_on',actions=[('allow','Allow notifications','notifications-allowed'),('deny','Do not allow','notifications-denied')])
 s('notifications-allowed','Notifications allowed','notifications','message','You control future alerts','Sample Game can send notifications.','alarm_on',[('remove','Turn notifications off','notifications-denied'),('back','Review choices','notification-permission')])
 s('notifications-denied','Notifications off','notifications','message','Alerts will stay silent','Other app features remain available. You can change this choice in notification settings.','alarm_off',[('review','Review choices','notification-permission')])
 s('picker-empty','Choose photos','picker','empty-grid','No photos in this location','Choose another source, or cancel without sharing any media.','apps',[('source','Choose another source','picker-loading'),('cancel','Cancel','picker-cancelled')])
 s('picker-loading','Choose photos','picker','loading','Opening the selected source','Waiting for the photo provider.','folder',[('ready','Preview loaded source','picker-results'),('empty','Preview empty source','picker-empty'),('error','Preview provider error','picker-error'),('cancel','Cancel','picker-cancelled')])
 s('picker-results','Choose photos','picker','photo-grid','Only selected media will be shared',actions=[('select','Select two photos','picker-selected'),('empty','Open empty source','picker-empty'),('cancel','Cancel','picker-cancelled')])
 s('picker-selected','Choose photos','picker','photo-grid','Two photos selected',actions=[('add','Add two photos','picker-complete'),('clear','Clear selection','picker-results'),('cancel','Cancel','picker-cancelled')],selectedMedia=True)
 s('picker-error','Source unavailable','picker','message','The photo provider did not respond','No photo was selected. Retry the source or leave without sharing media.','error',[('retry','Retry','picker-loading'),('cancel','Cancel','picker-cancelled')])
 s('picker-cancelled','No photos selected','picker','message','Nothing was shared','You left the photo picker without choosing media.','privacy',[('open','Choose photos','picker-loading')])
 s('picker-complete','Photos selected','picker','message','Two photos are ready','Only the selected media are returned to the requesting app.','success',[('again','Choose different photos','picker-results')])
 s('file-provider','Choose a document','files','file-list','Browse a document source',actions=[('select','Open sample document','file-selected'),('offline','Preview offline source','file-offline'),('cancel','Cancel','file-cancelled')])
 s('file-offline','Source is offline','files','message','Connect before trying again','The document source cannot be reached. No file was selected.','error',[('retry','Retry source','file-provider'),('cancel','Cancel','file-cancelled')])
 s('file-selected','Document selected','files','file-preview','Review before using the file',actions=[('use','Use this document','file-complete'),('back','Choose another','file-provider')])
 s('file-complete','Document ready','files','message','Selection completed','Sample notes.txt is selected for the requesting app.','document',[('again','Choose another','file-provider')])
 s('file-cancelled','No document selected','files','message','Nothing was opened','You left the document picker.','document',[('open','Choose a document','file-provider')])
 s('pin-entry','Enter PIN','pin','pin','Unlock your device',actions=[('wrong','Preview wrong PIN','pin-error'),('lockout','Preview lockout','pin-lockout'),('right','Preview accepted PIN','unlock-complete')])
 s('pin-error','Try your PIN again','pin','pin','That PIN was not accepted',actions=[('retry','Try again','pin-entry'),('lockout','Preview lockout','pin-lockout')],authError=True)
 s('pin-lockout','Try again later','pin','pin-locked','Too many attempts','Try again in 30 seconds. This is a sample lockout duration.','lock',[('elapsed','Preview wait completed','pin-entry')])
 s('unlock-complete','Unlocked','pin','message','Your session is ready','Your device is unlocked and ready to use.','success',[('lock','Preview locked device','pin-entry')])
 s('pattern-entry','Draw pattern','pattern','pattern','Unlock your device',actions=[('wrong','Preview wrong pattern','pattern-error'),('pin','Use PIN instead','pin-entry')])
 s('pattern-error','Pattern not recognized','pattern','pattern','Try your pattern again',actions=[('retry','Try again','pattern-entry'),('pin','Use PIN instead','pin-entry')],authError=True)
 s('biometric-prompt','Unlock','biometric','biometric','Touch your enrolled sensor',actions=[('fail','Preview failed match','biometric-failed'),('missing','Preview unavailable','biometric-unavailable'),('locked','Preview lockout','biometric-locked'),('pin','Use PIN','pin-entry')])
 s('biometric-failed','Not recognized','biometric','biometric','Try again or use your PIN',actions=[('retry','Try again','biometric-prompt'),('pin','Use PIN','pin-entry')],authError=True)
 s('biometric-unavailable','Sensor unavailable','biometric','biometric','Use your device PIN to continue',actions=[('pin','Use PIN','pin-entry')],unavailable=True)
 s('biometric-locked','Use your PIN','biometric','biometric','Biometric unlock is temporarily locked',actions=[('pin','Enter PIN','pin-entry')],unavailable=True)
 s('share-choices','Share','share','share','Choose a destination',actions=[('select','Choose Sample Notes','share-confirm'),('missing','Preview no destinations','share-empty'),('cancel','Cancel','share-cancelled')])
 s('share-empty','No sharing apps','share','message','No compatible destination was found','Save a copy locally, or return without sharing it.','share',[('save','Save a local copy','screenshot-saved'),('back','Back','share-choices')])
 s('share-confirm','Share with Sample Notes?','share','file-preview','Review the selected destination',actions=[('confirm','Share this copy','share-complete'),('cancel','Cancel','share-cancelled')])
 s('share-complete','Sharing complete','share','message','Your copy was shared','You can return to your app or choose another destination.','success',[('back','Choose another destination','share-choices')])
 s('share-cancelled','Sharing cancelled','share','message','Nothing was shared','Your local copy is still available.','privacy',[('back','Back to sharing','share-choices')])
 s('clipboard-empty','Clipboard','clipboard','message','Nothing to paste','Copied text and supported images appear here.','copy',[('sample','Load sample entry','clipboard-sensitive')])
 s('clipboard-sensitive','Clipboard','clipboard','sensitive','Sensitive content is hidden',actions=[('paste','Preview paste','clipboard-pasted'),('clear','Clear sample entry','clipboard-empty')])
 s('clipboard-pasted','Pasted','clipboard','message','Sample entry pasted','The clipboard content stays hidden in this preview.','paste',[('clear','Clear clipboard','clipboard-empty')])
 s('screenshot-saved','Screenshot saved','screenshot','file-preview','A local copy is ready',actions=[('share','Share copy','share-choices'),('error','Preview full storage','screenshot-storage-full')])
 s('screenshot-storage-full','Could not save','screenshot','message','Storage is full','Free some space, then try saving the copy again.','storage',[('retry','Preview retry','screenshot-saved')])
 s('audio-route','Sound output','audio','audio','Choose where media plays',actions=[('connect','Choose headphones','audio-connected'),('lost','Preview disconnected route','audio-disconnected')])
 s('audio-connected','Headphones selected','audio','audio','Media uses the selected output',actions=[('lost','Preview connection lost','audio-disconnected'),('speaker','Use speakers','audio-route')],connected=True)
 s('audio-disconnected','Output disconnected','audio','audio','Choose another available output',actions=[('speaker','Use speakers','audio-route'),('retry','Preview reconnection','audio-connected')],routeUnavailable=True)
 s('power-actions','Power controls','power','power','Choose an action',actions=[('off','Power off','power-confirm'),('restart','Restart','restart-confirm')])
 s('power-confirm','Power off device?','power','message','Your current session will end','Save your work before powering off.','power',[('confirm','Confirm power off','power-ended'),('cancel','Cancel','power-actions')],destructive=True)
 s('restart-confirm','Restart device?','power','message','Your apps may close','Save your work before restarting.','restart',[('confirm','Confirm restart','power-ended'),('cancel','Cancel','power-actions')],destructive=True)
 s('power-ended','Power action selected','power','message','Your choice is confirmed','The chosen power action ends this session.','power',[('back','Return to power menu','power-actions')])
 s('multiwindow-unavailable','Layout unavailable','multiwindow','message','This app cannot use the requested layout','Keep the app in a single window or choose another app.','app_pairs',[('single','Use a single window','multiwindow-single')])
 s('multiwindow-single','Single window','multiwindow','display-pair','The current app stays in one window',actions=[('choose','Choose a two-app layout','multiwindow-ready'),('unsupported','Preview unsupported app','multiwindow-unavailable')])
 s('multiwindow-ready','Two-app layout','multiwindow','display-pair','Both apps fit the selected arrangement',actions=[('single','Use a single window','multiwindow-single'),('unsupported','Preview unsupported app','multiwindow-unavailable')],paired=True)
 # English modifier/input-type/suggestion states; all text stays live.
 for id,title,layout in [('keyboard-lower','Text keyboard','lower'),('keyboard-upper','Shift keyboard','upper'),('keyboard-caps','Caps lock','caps'),('keyboard-symbols-2','More symbols','symbols'),('keyboard-email','Email keyboard','email'),('keyboard-url','Website address','url')]:
  s(id,title,'keyboard','keyboard','Choose letters and suggestions',layout=layout,actions=[('lower','Lowercase','keyboard-lower'),('upper','Shift','keyboard-upper'),('caps','Caps lock','keyboard-caps'),('symbols','More symbols','keyboard-symbols-2'),('email','Email keyboard','keyboard-email'),('url','Website keyboard','keyboard-url'),('accept','Accept suggestion','suggestion-accepted'),('reject','Dismiss suggestion','suggestion-rejected')])
 s('suggestion-accepted','Suggestion accepted','keyboard','keyboard','The chosen word is inserted',layout='lower',accepted=True,actions=[('edit','Keep typing','keyboard-lower'),('undo','Undo suggestion','suggestion-rejected')])
 s('suggestion-rejected','Suggestion dismissed','keyboard','keyboard','Your typed word is kept',layout='lower',rejected=True,actions=[('edit','Keep typing','keyboard-lower'),('choose','Choose suggestion','suggestion-accepted')])
 # Hardware results are explicit fixtures, with no guessed privileged implementation.
 def th(id,title,family,kind,subtitle,body='',icon='controller',actions=None,**kw):s(id,title,family,kind,subtitle,body,icon,actions,group='thor',**kw)
 th('mapping-edit','Button mapping','mapping','mapping','Choose a control to remap',actions=[('listen','Listen for a control','mapping-listening'),('save','Review changes','mapping-review'),('restore','Restore defaults','mapping-restore'),('unsupported','Preview unavailable','mapping-unavailable')])
 th('mapping-listening','Press a control','mapping','input-listen','Waiting for controller input',actions=[('input','Preview captured control','mapping-review'),('conflict','Preview duplicate binding','mapping-conflict'),('cancel','Cancel','mapping-edit')],pending=True)
 th('mapping-conflict','Binding conflict','mapping','message','That action already has a binding','Choose another action, or replace the existing binding after review.',actions=[('review','Review replacement','mapping-review'),('cancel','Keep current binding','mapping-edit')])
 th('mapping-review','Review mapping','mapping','mapping','A → primary action; B → back',actions=[('apply','Apply changes','mapping-pending'),('cancel','Keep current mapping','mapping-edit')])
 th('mapping-pending','Applying mapping','mapping','loading','Waiting for the input service',actions=[('success','Preview confirmed result','mapping-applied'),('error','Preview apply failure','mapping-error')],pending=True)
 th('mapping-applied','Mapping applied','mapping','mapping','The new values were read back',actions=[('edit','Edit mapping','mapping-edit'),('restore','Restore previous','mapping-restore')],applied=True)
 th('mapping-error','Mapping not applied','mapping','message','The input service did not confirm the change','The previous mapping remains selected.',icon='error',actions=[('retry','Retry','mapping-pending'),('back','Keep previous mapping','mapping-edit')])
 th('mapping-restore','Restore mapping?','mapping','message','Review before replacing your bindings','The saved previous mapping will replace the current mapping.',actions=[('confirm','Restore previous mapping','mapping-restored'),('cancel','Cancel','mapping-edit')])
 th('mapping-restored','Mapping restored','mapping','mapping','The previous mapping was confirmed',actions=[('edit','Edit mapping','mapping-edit')],applied=True)
 th('mapping-unavailable','Mapping unavailable','mapping','unavailable','No supported input service was found',actions=[('back','Back to preferences','mapping-edit')],unavailable=True)
 th('profile-review','Review game profile','profiles','profile','Review requested changes before applying',actions=[('apply','Apply profile','profile-pending'),('conflict','Preview ownership conflict','profile-conflict'),('restore','Review restore','profile-restore')])
 th('profile-pending','Applying profile','profiles','loading','Waiting for confirmed values',actions=[('all','Preview full confirmation','profile-applied'),('partial','Preview partial result','profile-partial'),('error','Preview failure','profile-error')],pending=True)
 th('profile-applied','Profile applied','profiles','profile','All requested values were confirmed',actions=[('restore','Restore previous','profile-restore'),('review','Review profile','profile-review')],applied=True)
 th('profile-partial','Profile partly applied','profiles','profile','Two values applied; one was skipped',actions=[('retry','Retry skipped preference','profile-pending'),('restore','Restore previous','profile-restore'),('keep','Keep confirmed changes','profile-review')],partial=True)
 th('profile-error','Profile not applied','profiles','message','The service did not confirm the change','Keep previous preferences, or retry when the service is ready.',icon='error',actions=[('retry','Retry','profile-pending'),('review','Keep previous','profile-review')])
 th('profile-conflict','Another profile is active','profiles','message','Choose who controls these preferences','Review replacement before applying a different game profile.',actions=[('replace','Review replacement','profile-review'),('keep','Keep active profile','profile-applied')])
 th('profile-restore','Restore preferences?','profiles','profile','Restore the values saved before this profile',actions=[('restore','Restore previous values','profile-restoring'),('cancel','Cancel','profile-review')])
 th('profile-restoring','Restoring preferences','profiles','loading','Waiting for readback of previous values',actions=[('ready','Preview restored values','profile-restored'),('error','Preview restore failure','profile-restore-error')],pending=True)
 th('profile-restored','Previous values restored','profiles','profile','Saved values were applied and confirmed',actions=[('review','Review profile','profile-review')],applied=True,restored=True)
 th('profile-restore-error','Restore not confirmed','profiles','message','Some previous values could not be restored','Review the result before retrying. Do not assume a rollback succeeded.',icon='error',actions=[('retry','Retry restore','profile-restoring'),('review','Review current values','profile-partial')])
 th('capture-choose','Capture displays','capture','capture','Choose the displays to include',actions=[('record','Recording options','recording-options'),('shot','Preview screenshot','capture-saved'),('unavailable','Preview missing display','capture-unavailable')])
 th('recording-options','Recording options','capture','record-options','Choose audio before recording',actions=[('start','Review capture request','capture-consent'),('cancel','Cancel','capture-choose')])
 th('capture-consent','Start recording?','capture','message','Confirm the selected displays and audio','Recording includes the displays and audio sources you selected.',icon='screen_recording',actions=[('allow','Start recording','record-countdown'),('deny','Do not record','capture-denied')])
 th('capture-denied','Recording not started','capture','message','Capture permission was not granted','No display or audio was recorded.',icon='privacy',actions=[('again','Review options','recording-options'),('back','Back','capture-choose')])
 th('record-countdown','Recording begins soon','capture','countdown','Starting in 3',actions=[('ready','Preview recording started','record-active'),('cancel','Cancel','capture-choose')],pending=True)
 th('record-active','Recording','capture','record-active','Upper and lower displays · 00:24',actions=[('pause','Pause','record-paused'),('stop','Stop and save','capture-saved'),('fail','Preview storage error','capture-storage-error')],active=True)
 th('record-paused','Recording paused','capture','record-active','Recording time is paused',actions=[('resume','Resume','record-active'),('stop','Stop and save','capture-saved')])
 th('capture-saved','Capture saved','capture','file-preview','A local copy is ready',actions=[('again','Capture again','capture-choose'),('error','Preview full storage','capture-storage-error')])
 th('capture-storage-error','Capture not saved','capture','message','Storage is full or unavailable','Your capture could not be saved. Review storage before recording again.',icon='storage',actions=[('review','Review capture options','capture-choose')])
 th('capture-unavailable','Display capture unavailable','capture','unavailable','The requested capture path is unavailable',actions=[('back','Choose another capture','capture-choose')],unavailable=True)
 th('input-capture','Input capture','input-capture','input-listen','Controller input is captured for this game',actions=[('release','Release capture','input-released'),('lid','Preview lid close and wake','input-resume-check')],active=True)
 th('input-released','Input released','input-capture','message','Your device has controller focus again','Your controller is available to system navigation again.',actions=[('capture','Review capture again','input-capture')])
 th('input-resume-check','Resume controller capture?','input-capture','message','The device has resumed','Choose whether to return controller input to the game.',actions=[('resume','Resume capture','input-capture'),('release','Keep device control','input-released')])
 th('touch-unsupported','Touch mapping unavailable','touch-mapping','unavailable','No supported mapping path was found',actions=[('back','Review available controls','input-released')],unavailable=True)
 th('display-route','Display routing','display-route','display-pair','Choose a supported destination',actions=[('swap','Preview screen swap','display-pending'),('missing','Preview unavailable app','display-unavailable')],paired=True)
 th('display-pending','Moving the app','display-route','loading','Waiting for the display owner',actions=[('success','Preview confirmed route','display-applied'),('fail','Preview route failure','display-error')],pending=True)
 th('display-applied','Display route changed','display-route','display-pair','The requested destination was confirmed',actions=[('restore','Restore previous layout','display-route'),('choose','Choose another route','display-route')],paired=True,applied=True)
 th('display-error','App could not move','display-route','message','The previous layout remains active','Choose another app or destination.',icon='error',actions=[('retry','Retry','display-pending'),('back','Keep current layout','display-route')])
 th('display-unavailable','Destination unavailable','display-route','unavailable','The app or requested display is unavailable',actions=[('back','Choose another destination','display-route')],unavailable=True)
 # Every hardware family gets a distinct availability/apply/error/readback view.
 for family,title,icon in [('fan','Cooling preference','fan'),('charging','Charge limit','battery_charging'),('lighting','Lighting zones','controls')]:
  th(family+'-ready',title,family,'hardware','Review a supported preference',icon=icon,actions=[('apply','Apply preference',family+'-pending'),('missing','Preview unavailable',family+'-unavailable')],feature=family)
  th(family+'-pending','Applying preference',family,'loading','Waiting for the hardware service',icon=icon,actions=[('confirm','Preview readback confirmed',family+'-applied'),('error','Preview service error',family+'-error')],pending=True,feature=family)
  th(family+'-applied',title+' applied',family,'hardware','The reported value matches your choice',icon=icon,actions=[('change','Choose another value',family+'-ready'),('restore','Restore previous value',family+'-restored')],applied=True,feature=family)
  th(family+'-error','Preference not applied',family,'message','The service did not confirm the change','The previous value remains in effect.',icon='error',actions=[('retry','Retry',family+'-pending'),('keep','Keep previous',family+'-ready')],feature=family)
  th(family+'-unavailable',title+' unavailable',family,'unavailable','No supported hardware value was reported',icon=icon,actions=[('back','Back to preferences',family+'-ready')],unavailable=True,feature=family)
  th(family+'-restored','Previous preference restored',family,'hardware','The saved previous value was confirmed',icon=icon,actions=[('review','Review preference',family+'-ready')],applied=True,restored=True,feature=family)
 return r

def render_body(s,d):
 k=d['kind'];thor=s.group=='thor';w=s.w;bottom=630 if thor else 790
 if k in ['message','unavailable','loading','countdown']:
  y=160 if thor else 210;s.icon('info' if k=='loading' else d['icon'],w/2-44,y,88,'on' if d.get('active') or d.get('pending') else 'off')
  title='Waiting for confirmation' if k=='loading' else '3' if k=='countdown' else d['subtitle']
  s.text(title,w/2,y+135,28 if k!='countdown' else 60,bold=True,anchor='middle')
  s.paragraph(d['body'] or ('This preference is unavailable until a supported service reports it.' if k=='unavailable' else 'Please wait while the result is confirmed.'),60,y+185,w-120,18)
  if k=='unavailable':s.frame(38,470,w-76,94,'off','Unavailable preference');s.text('Unavailable',w/2,529,23,'#a6b0b8',anchor='middle')
 elif k in ['permission','location']:
  s.frame(24,160,w-48,535);s.icon(d['icon'],w/2-48,195,96);s.text(d['title'],w/2,350,28,bold=True,anchor='middle');s.paragraph('Sample app requests access for the feature you selected. You can decline and keep using other features.',66,406,w-132,19)
  if k=='location':
   s.frame(56,520,228,112,'on','Precise location');s.frame(316,520,228,112,'off','Approximate location');s.text('Precise',170,584,21,anchor='middle');s.text('Approximate',430,584,21,anchor='middle')
 elif k=='settings':
  for i,(title,detail,icon,on) in enumerate([('Camera','While using the app','camera_on',True),('Microphone','Not allowed','microphone_off',False),('Location','Not allowed','location_off',False)]):s.row(title,detail,165+i*120,icon,on=on)
 elif k=='empty-grid':
  for i in range(6):s.frame(24+i%3*188,165+i//3*160,176,140)
  s.text('No photos yet',w/2,590,27,bold=True,anchor='middle');s.paragraph(d['body'],60,640,w-120,19)
 elif k=='photo-grid':
  for i in range(6):s.media(24+i%3*188,175+i//3*240,176,222,d.get('selectedMedia') and i in [0,4],i)
  s.text('2 selected' if d.get('selectedMedia') else 'Select photos',32,715,23)
 elif k=='file-list':
  for i,(name,detail) in enumerate([('Sample notes.txt','Text document · sample'),('Save backup.zip','Archive · sample'),('Screenshot.png','Image · sample')]):s.row(name,detail,170+i*125,'document',value='›')
 elif k=='file-preview':
  s.frame(24,155,w-48,350 if not thor else 290);s.icon('document' if d['family']=='files' else 'screenshot',w/2-68,195,136);s.text('Sample notes.txt' if d['family']=='files' else 'Capture preview',w/2,410 if not thor else 390,25,bold=True,anchor='middle');s.paragraph('Local sample file · no personal content',60,550 if not thor else 495,w-120,18)
 elif k in ['pin','pin-locked']:
  s.icon('lock',268,140,64);s.text('Try again in 30 seconds' if k=='pin-locked' else 'PIN not accepted' if d.get('authError') else 'Enter your device PIN',w/2,270,26,bold=True,anchor='middle');s.text('○ ○ ○ ○ ○ ○',w/2,324,26,anchor='middle')
  for i,n in enumerate(['1','2','3','4','5','6','7','8','9','','0','⌫']):
   if n:
    x=112+i%3*140;y=355+i//3*103;s.asset('pin_key',x,y,.90,'disabled' if k=='pin-locked' else 'off');s.text(n,x+43.2,y+51,27,'#9ba5ae' if k=='pin-locked' else '#eee7d9',True,'middle')
  bottom=810
 elif k=='pattern':
  s.icon('lock',268,145,64);s.text('Pattern not recognized' if d.get('authError') else 'Draw your pattern',w/2,290,26,bold=True,anchor='middle')
  for i in range(9):s.asset('pattern_node',120+i%3*144,355+i//3*144,1,'off')
  if d.get('authError'):s.text('Try again or use your PIN',w/2,750,20,'#b5bdc6',anchor='middle')
 elif k=='biometric':
  s.asset('biometric_socket',220,230,1,'off' if d.get('unavailable') or d.get('authError') else 'on');s.text('Use your PIN' if d.get('unavailable') else 'Try the sensor again' if d.get('authError') else 'Touch the sensor',w/2,470,29,bold=True,anchor='middle');s.paragraph(d['subtitle'],70,535,w-140,20)
 elif k=='sensitive':
  s.frame(24,160,w-48,230);s.icon('privacy',56,189,62);s.text('Sensitive content',142,225,25,bold=True);s.text('••••••••••••••••',64,318,31);s.paragraph('The contents are hidden from this preview. Clear the entry when you no longer need it.',60,470,w-120,19)
 elif k=='share':
  s.media(24,155,w-48,260);s.text('Choose an app',32,478,24,bold=True)
  for i,(name,icon) in enumerate([('Notes','document'),('Files','folder'),('Nearby','share')]):s.app(name,icon,52+i*194,525)
 elif k=='audio':
  s.row('Speakers','Selected output' if not d.get('connected') else 'Available',170,'audio',on=not d.get('connected'));s.row('Headphones','Selected output' if d.get('connected') else 'Disconnected',292,'headphones',on=d.get('connected',False),disabled=not d.get('connected'));s.row('Media volume','60% · sample value',414,'audio',value='›')
 elif k=='power':
  for i,(label,icon) in enumerate([('Power off','power'),('Restart','restart')]):
   x=32+i*280;s.frame(x,225,256,260);s.icon(icon,x+80,275,96);s.text(label,x+128,438,25,bold=True,anchor='middle')
 elif k=='keyboard':
  layout=d.get('layout','lower');s.frame(24,145,552,160);s.text('Email address' if layout=='email' else 'Website address' if layout=='url' else 'Message',54,190,18,'#b5bdc6');s.text('Steel' if d.get('accepted') else 'Stee' if d.get('rejected') else 'name@example.com' if layout=='email' else 'https://example.com' if layout=='url' else 'Write a message…',54,253,25)
  for i,label in enumerate(['Steel','Ember','Forge']):s.frame(24+i*188,344,176,64,'on' if d.get('accepted') and i==0 else 'off',label);s.text(label,112+i*188,383,19,anchor='middle')
  layouts={'lower':['q w e r t y u i o p','a s d f g h j k l','⇧ z x c v b n m ⌫'],'upper':['Q W E R T Y U I O P','A S D F G H J K L','⇧ Z X C V B N M ⌫'],'caps':['Q W E R T Y U I O P','A S D F G H J K L','⇪ Z X C V B N M ⌫'],'symbols':['~ ` | # % ^ * + = $','! ? & ( ) - : ; /','\" \' [ ] < > _ ⌫']}
  if layout in ['email','url']:layouts[layout]=layouts['lower']
  for row,line in enumerate(layouts[layout]):
   labels=line.split()
   cw=(552-(len(labels)-1)*5)/len(labels)
   for i,label in enumerate(labels):
    x=24+i*(cw+5);s.frame(x,449+row*94,cw,78,'on' if label in ['⇧','⇪'] and layout in ['upper','caps'] else 'off',label);s.text(label,x+cw/2,498+row*94,23,anchor='middle')
  for x,label,cw in [(24,'@' if layout=='email' else '/' if layout=='url' else '123',95),(132,'.com' if layout=='url' else 'Space',298),(443,'Go' if layout=='url' else '↵',133)]:s.frame(x,751,cw,72);s.text(label,x+cw/2,797,21,anchor='middle')
  s.meta['keyboardLayout']=layout;s.meta['textDirection']='ltr';s.meta['authoredLocale']='en-US';bottom=862
 elif k in ['mapping','profile','hardware']:
  if k=='mapping':items=[('A','Primary action','controller'),('B','Back / cancel','controller'),('Left stick','Movement','controller')]
  elif k=='profile':items=[('Display layout','Previous layout' if d.get('restored') else 'Game on upper display','display_upper'),('Input mapping','Selected saved bindings','controller'),('Fan preference','Skipped · unavailable' if d.get('partial') else 'Automatic cooling','fan')]
  else:
   feature=d['feature'];items={'fan':[('Cooling mode','Automatic','fan_auto'),('Thermal protection','Always authoritative','thermal_warning')],'charging':[('Charge limit','80% · sample choice','battery_charging'),('Charging bypass','Unavailable','usb')],'lighting':[('Left zone','Steady ember','controls'),('Right zone','Off','controls')]}[feature]
  for i,(name,detail,icon) in enumerate(items):s.row(name,detail,155+i*117,icon,on=(d.get('applied',False) or d.get('partial',False) and i<2) and not ('Off' in detail or 'Unavailable' in detail or 'Skipped' in detail),disabled='Unavailable' in detail or 'Skipped' in detail)
  if d.get('partial'):s.text('Applied: display and input. Fan was unchanged.',42,565,22,'#b5bdc6')
 elif k=='input-listen':
  s.asset('stick_gate',308,170,1,'on' if d.get('active') else 'off');s.text('Game has controller input' if d.get('active') else 'Press a button to assign it',w/2,435,27,bold=True,anchor='middle');s.paragraph('You can leave this screen without replacing the current mapping.',60,500,w-120,19)
 elif k in ['display-pair','capture']:
  for i,(name,icon) in enumerate([('Upper display','display_upper'),('Lower display','display_lower')]):
   cw=(w-72)/2;x=24+i*(cw+24);s.frame(x,170,cw,300,'on' if d.get('paired') or (k=='capture' and i==0) else 'off',name);s.icon(icon,x+cw/2-55,215,110);s.text(name,x+cw/2,420,23,bold=True,anchor='middle')
  s.paragraph('Choose an available display for this app.',42,530,w-84,18)
 elif k=='record-options':
  for i,(name,detail,icon,on) in enumerate([('Upper + lower','Selected display scope','app_pairs',True),('Device audio','Enabled','audio',True),('Microphone','Off','microphone_off',False)]):s.row(name,detail,160+i*120,icon,on=on)
 elif k=='record-active':
  s.icon('screen_recording',w/2-65,170,130,'on' if d.get('active') else 'off');s.text('00:24',w/2,385,52,bold=True,anchor='middle');s.text('Recording' if d.get('active') else 'Paused',w/2,450,27,anchor='middle');s.paragraph('Your recording is saved when you stop.',60,515,w-120,19)
 else:raise AssertionError(k)
 # Fixture outcomes live in the viewer. Product scenes show only actual choices.
 actions=d['actions'];shown=[a for a in actions if not a[1].lower().startswith(('preview','load sample'))][:2]
 if k in ['permission','location']:shown=actions[:3];bottom=725 if len(shown)==3 else bottom
 if k=='keyboard':shown=[a for a in actions if a[0] in ['accept','reject','edit','undo']][:2]
 for i,(id,label,target) in enumerate(actions):
  if (id,label,target) in shown:
   j=shown.index((id,label,target));x=24;y=bottom+j*72;cw=w-48
   if len(shown)==2:x=24+j*(w/2);y=bottom;cw=w/2-48
   # Long labels get a full-width row rather than a crowded half-width button.
   if len(shown)==2 and any(font(18,True).getlength(a[1])>w/2-80 for a in shown):x=24;y=bottom+j*72;cw=w-48
   s.action(id,label,target,x,y,cw,focused=(j==0),disabled=False)
  else:s.links.append({'id':id,'label':label,'target':target,'viewerOnly':True})
 s.meta.update(family=d['family'],kind=k,unavailable=d.get('unavailable',False),pending=d.get('pending',False),sampleState=d['id'],destructiveConfirmation=d.get('destructive',False))

def build(out,resume=False,only=None):
 assert not out.exists() or (resume and not (out/'complete-assets.zip').exists()),'Packaged checkpoints are immutable'
 for sub in ['source','masters','screens','inspections','previews','verification/evidence']:(out/sub).mkdir(parents=True,exist_ok=True)
 prior=ROOT/'iterations/13-forge-android-and-thor-flows';assets={}
 for name in ['steel-material.png','steel-material-original.png']:shutil.copy2(prior/'source'/name,out/'source'/name)
 for f in (prior/'masters').glob('*.svg'):
  r=ET.parse(f).getroot();w,h=map(float,r.get('viewBox').split()[2:]);assets[f.stem]=(r,w,h);shutil.copy2(f,out/'masters'/f.name)
 shutil.copy2(prior/'runtime-style.json',out/'runtime-style.json');states=json.loads((out/'runtime-style.json').read_text())['sampleStates'];texture=base64.b64encode((out/'source/steel-material.png').read_bytes()).decode()
 defs=definitions();assert len({r['id'] for r in defs})==len(defs);old={r['id']:r for r in json.loads((out/'screens/layout-metadata.json').read_text())} if only else {};metadata=[]
 for d in defs:
  if only and d['id'] not in only:metadata.append(old[d['id']]);continue
  s=FlowScene(d['id'],d['title'],d.get('group','android'),states,assets,texture,d['subtitle'],capability='Explicit fixture; native owners and hardware capabilities are not exercised' if d.get('group')=='thor' else None)
  render_body(s,d);metadata.append(s.finish(out));print('scene',d['id'],flush=True)
 (out/'screens/layout-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n');(out/'flow-definitions.json').write_text(json.dumps(defs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 labels=sorted({t['text'] for scene in metadata for t in scene['textBoxes']}|{a[1] for d in defs for a in d['actions']});assert all(not c.isalpha() or c.isascii() for label in labels for c in label)
 catalog={'authoredLocale':'en-US','textDirection':'ltr','labels':[{'id':'forge_text_'+hashlib.sha256(s.encode()).hexdigest()[:12],'text':s} for s in labels]};(out/'english-text-catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
 resource_dir=out/'native-text/res/values';resource_dir.mkdir(parents=True,exist_ok=True);resources=ET.Element('resources')
 for row in catalog['labels']:
  value=row['text'].replace('\\','\\\\').replace('"','\\"').replace("'","\\'");ET.SubElement(resources,'string',name=row['id'],translatable='false',formatted='false').text='"'+value+'"'
 (resource_dir/'strings.xml').write_text('<?xml version="1.0" encoding="utf-8"?>\n'+ET.tostring(resources,encoding='unicode')+'\n',encoding='utf8')
 provenance={'date':'2026-10-22','baseline':'iterations/13-forge-android-and-thor-flows','newComponentMasters':0,'reusedMasters':[{'id':f.stem,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted((out/'masters').glob('*.svg'))],'inputs':[{'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted((out/'source').glob('*.png'))]};(out/'source/provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 families={family:[s['id'] for s in metadata if s['family']==family] for family in sorted({s['family'] for s in metadata})};(out/'journey-index.json').write_text(json.dumps(families,indent=2)+'\n')
 for group in ['android','thor']:
  rows=[r for r in metadata if r['group']==group]
  for offset in range(0,len(rows),9):
   part=rows[offset:offset+9];tw=340 if group=='android' else 440;th=650 if group=='android' else 520;board=Image.new('RGB',(tw*3+40,math.ceil(len(part)/3)*th+125),'#080c11');draw=ImageDraw.Draw(board);draw.text((24,18),'REFERENCE FORGE 15 / '+group.upper()+f' / {offset//9+1:02}',font=font(27,True),fill='#eee7d9');draw.text((24,63),'Journey states / live labels / hardware and authentication fixtures only',font=font(17),fill='#b5bdc6')
   for i,m in enumerate(part):
    im=Image.open(out/'screens'/f"{m['id']}.png").convert('RGBA');im.thumbnail((tw-22,th-95),Image.Resampling.LANCZOS);x=20+i%3*tw;y=112+i//3*th;board.paste(im,(x+(tw-22-im.width)//2,y),im);draw.text((x+5,y+th-70),m['id'],font=font(16,True),fill='#eee7d9')
   board.save(out/'previews'/f'{group}-states-{offset//9+1:02}.png')
 write_viewer(out,defs,families)
 (out/'coverage-map.json').write_text(json.dumps({'iteration':15,'newScenes':len(metadata),'journeyFamilies':len(families),'newComponentMasters':0,'reusedComponentMasters':len(assets),'scope':'Declared missing state/journey artwork and offline scene navigation; no actual authentication, permission, capture or hardware implementation','families':families,'remaining':['114-recipe motion reconciliation and actual atmosphere/transition playback','Historical source dispositions and explicit app icon target coverage','Final pre-integration visual review; native integration and target V3 afterward'],'nativeTarget':'AYN odin2thor / LineageOS 24.0','deviceConnectedAtInventory':False},indent=2)+'\n')
 print(json.dumps({'scenes':len(metadata),'families':len(families),'out':str(out)}))

def write_viewer(out,defs,families):
 data=json.dumps(defs,ensure_ascii=False).replace('</','<' + chr(92) + '/');options=''.join('<option value="'+f+'">'+html.escape(f.replace('-',' ').title())+'</option>' for f in families)
 page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reference Forge 15 — Journey viewer</title><style>body{margin:24px;background:#080c11;color:#eee7d9;font:18px system-ui}h1{font-size:30px}p{max-width:85ch;color:#b5bdc6}label{display:inline-block;margin:8px}select,button{background:#17212a;color:#eee7d9;border:1px solid #73818c;font:inherit;padding:12px;margin:5px}button:focus-visible,select:focus-visible{outline:3px solid #d5e7f2}main{display:grid;grid-template-columns:minmax(300px,800px) minmax(260px,1fr);gap:24px}img{width:100%;height:75vh;object-fit:contain}#actions{display:flex;flex-direction:column;align-items:stretch}a{color:#c6dce9}@media(max-width:800px){main{display:block}img{height:65vh}}</style><h1>Reference Forge 15 — Journey viewer</h1><p>Navigate sample permission, unlock, picker, keyboard and Thor outcomes. These controls change artwork scenes only. They do not grant permissions, unlock a device, send data, record media or control hardware.</p><label>Journey <select id="family">OPTIONS</select></label><label>State <select id="state"></select></label><button id="restart">Restart journey</button><p id="status" aria-live="polite"></p><main><section><img id="preview" alt=""><p><a id="svg">Editable SVG</a> · <a id="cold">Cold inspection</a></p></section><aside><h2>Sample transitions</h2><div id="actions"></div><p>Branches labelled Preview are design fixtures. Platform and hardware owners remain authoritative in a real implementation.</p></aside></main><script>const scenes=DATA;
const family=document.querySelector('#family'),state=document.querySelector('#state'),preview=document.querySelector('#preview'),actions=document.querySelector('#actions');
function show(id){const row=scenes.find(s=>s.id===id);if(!row)throw Error('Unknown scene');family.value=row.family;state.replaceChildren(...scenes.filter(s=>s.family===row.family).map(s=>{const o=document.createElement('option');o.value=s.id;o.textContent=s.id;return o}));state.value=id;preview.src='screens/'+id+'.png';preview.alt=row.title+' — '+row.subtitle;document.querySelector('#svg').href='screens/'+id+'.svg';document.querySelector('#cold').href='inspections/'+id+'.cold-material.png';document.querySelector('#status').textContent=row.title+' · '+id;actions.replaceChildren(...row.actions.map(a=>{const b=document.createElement('button');b.textContent=a[1];b.addEventListener('click',()=>show(a[2]));return b}));}
family.addEventListener('change',()=>show(scenes.find(s=>s.family===family.value).id));state.addEventListener('change',()=>show(state.value));document.querySelector('#restart').addEventListener('click',()=>show(scenes.find(s=>s.family===family.value).id));show(scenes[0].id);
</script></html>'''.replace('OPTIONS',options).replace('DATA',data)
 (out/'index.html').write_text(page,encoding='utf8')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--resume-draft',action='store_true');p.add_argument('--scene',action='append');a=p.parse_args();assert not a.scene or a.resume_draft;build(a.out.resolve(),a.resume_draft,a.scene)
