"""Expand ES-011..024 into usable component variants with independent material/masks."""
from pathlib import Path
import argparse,copy,io,json,math,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import Asset,SVG,INK,TOKENS,el,add,path,chamfer,poly,ring,render,font,fitpaste

# Fixed-size art specimens, not final native text metrics or stretch-safe layouts.
SPECS=[('button_primary','Primary button',256,72,'Launch game','ES-011'),('button_secondary','Secondary button',256,72,'Cancel','ES-011'),('button_destructive','Destructive button',256,72,'Delete profile','ES-011'),('icon_button','Icon button',72,72,'','ES-012'),('switch_off','Switch off',112,56,'','ES-013'),('switch_on','Switch on',112,56,'','ES-013'),('check_empty','Checkbox empty',48,48,'','ES-014'),('check_checked','Checkbox checked',48,48,'','ES-014'),('check_mixed','Checkbox mixed',48,48,'','ES-014'),('radio_off','Radio off',48,48,'','ES-014'),('radio_on','Radio on',48,48,'','ES-014'),('slider_min','Slider minimum',320,56,'','ES-015'),('slider_half','Slider midpoint',320,56,'','ES-015'),('slider_max','Slider maximum',320,56,'','ES-015'),('progress_empty','Progress empty',320,40,'','ES-016'),('progress_half','Progress half',320,40,'','ES-016'),('progress_full','Progress full',320,40,'','ES-016'),('progress_indeterminate','Indeterminate window',320,40,'','ES-016'),('progress_ring','Circular progress',160,160,'72%','ES-016'),('tabs','Three tabs',344,64,'','ES-017'),('section_header','Section heading',344,56,'Connections','ES-017'),('text_field','Text field',344,80,'Profile name','ES-018'),('search_field','Search field',344,80,'Search library','ES-018'),('error_field','Validation error',344,104,'Enter a profile name','ES-018'),('settings_row','Settings row',344,80,'Display target','ES-019'),('menu_panel','Context menu',256,240,'','ES-020'),('menu_item','Context item',256,56,'Game options','ES-020'),('tooltip','Tooltip',240,64,'Open on lower screen','ES-020'),('card','Card / widget',344,192,'Recent games','ES-021'),('notification_compact','Compact notification',344,112,'Download ready','ES-022'),('notification_expanded','Expanded notification',344,224,'Download complete','ES-022'),('notification_group','Grouped notifications',344,288,'Downloads','ES-022'),('notification_persistent','Persistent notification',344,112,'Game controller connected','ES-022'),('dialog','Dialog',344,224,'Choose a display','ES-023'),('confirmation','Confirmation',344,200,'Delete this profile?','ES-023'),('bottom_sheet','Bottom sheet',360,320,'Game options','ES-023'),('toast','Toast',280,64,'Profile saved','ES-023'),('scrollbar','Scrollbar',32,192,'','ES-024'),('focus_boundary','Focus boundary',280,72,'','ES-024'),('controller_cap','Controller button cap',56,56,'A','TH-001'),('shoulder_cap','Shoulder button cap',88,48,'L1','TH-001'),('trigger_cap','Trigger button cap',88,64,'L2','TH-004'),('keyboard_letter','Letter key',56,56,'A','ES-048'),('keyboard_space','Space key',256,56,'Space','ES-048'),('keyboard_enter','Enter key',104,56,'Enter','ES-048'),('keyboard_modifier','Modifier key',88,56,'Shift','ES-048')]
STATES=['cold','idle','hovered','selected','focused','pressed','disabled','reduced']
class Component(Asset):
 def __init__(self,s):super().__init__(s[:5],4);self.package=s[5]
 def frame(self,x,y,w,h,detail=True):
  super().frame(x,y,w,h,detail)
  if detail and h>45:
   # Original sculpted seam cuts live on trim, never in the reading well.
   for xx,yy,sign in [(x+w*.27,y+3,1),(x+w*.71,y+h-3,-1)]:
    path(self.b,poly([(xx,yy),(xx+8,yy+sign*2),(xx+14,yy),(xx+11,yy+sign*4),(xx+5,yy+sign*3)]),'#252f39')
    path(self.b,f'M{xx} {yy} l8 {sign*2} l6 {-sign*2}',stroke='#a0a9ae',width=.5,opacity='.48')
    path(self.s,f'M{xx+8} {yy+sign*2} l3 {sign*2}',stroke='white',width=.55)
 def build(self):
  k=self.key;w=self.w;h=self.h
  if k.startswith('switch_'):
   self.frame(6,10,100,36,False);self.circle(84 if k.endswith('on') else 28,28,17)
   if k.endswith('on'):path(self.g,'M22 28 h12',stroke='#d0d8df',width=2)
  elif k.startswith('check_'):
   self.frame(7,7,34,34,False)
   if k.endswith('checked'):self.symbol('M15 24 l7 7 l12 -15',2.6)
   if k.endswith('mixed'):self.symbol('M15 24 H33',2.6)
  elif k.startswith('radio_'):
   self.circle(24,24,16)
   if k.endswith('on'):add(self.g,'circle',cx=24,cy=24,r=6,fill='#cbd5df')
  elif k.startswith('slider_'):
   self.frame(9,22,w-18,12,False);p={'slider_min':29,'slider_half':160,'slider_max':291}[k]
   path(self.g,f'M24 28 H{p}',stroke='#a3b1bf',width=2.5);self.circle(p,28,17)
  elif k.startswith('progress_'):
   if k=='progress_ring':
    self.circle(80,80,64);add(self.g,'circle',cx=80,cy=80,r=47,fill='none',stroke='#c6d2db',stroke_width=3,stroke_dasharray='212 84',transform='rotate(-90 80 80)')
   else:
    self.frame(7,12,w-14,16,False);a,b=(20,20) if k.endswith('empty') else (20,160) if k.endswith('half') else (20,300) if k.endswith('full') else (100,186)
    if b>a:path(self.g,f'M{a} 20 H{b}',stroke='#b7c7d3',width=3)
  elif k in ['icon_button','controller_cap']:
   self.circle(w/2,h/2,min(w,h)/2-9)
   if k=='icon_button':self.symbol('M28 25 L48 36 L28 47 Z',2)
  elif k=='scrollbar':
   self.frame(11,5,10,182,False);path(self.g,chamfer(8,48,16,64,4),'url(#edge)')
  elif k=='focus_boundary':
   path(self.g,chamfer(3,3,w-6,h-6,8),stroke='#d5e7f2',width=2)
  else:
   self.frame(6,6,w-12,h-12)
   if k=='button_destructive':self.symbol('M30 26 V44 M23 26 H37 M26 22 H34 M26 29 V41 H34 V29',1.5)
   if k=='tabs':
    for x in [116,228]:path(self.b,f'M{x} 20 V45',stroke='#4b5864',width=1)
    path(self.g,'M26 54 H98',stroke='#c8d5df',width=2)
   if k in ['text_field','search_field','error_field']:
    path(self.b,f'M25 {60 if k=="error_field" else h-20} H{w-25}',stroke='#576572' if k!='error_field' else '#d68791',width=1)
    if k=='search_field':ring(self.g,33,38,8,1.8,'#c8d4df');self.symbol('M39 44 L46 51',1.8)
    if k=='error_field':self.symbol('M315 28 v10 M315 43 v1',2)
   if k in ['settings_row','menu_item']:self.symbol(f'M{w-34} {h/2-8} l8 8 l-8 8',2)
   if k=='menu_panel':
    for y in [66,118,170]:path(self.b,f'M23 {y} H{w-23}',stroke='#3d4b58',width=.8)
   if k.startswith('notification_'):
    self.circle(44,48,23);self.symbol('M36 48 l6 6 l12 -14',2)
    if k=='notification_expanded':self.frame(22,145,w-44,54,False)
    if k=='notification_group':
     for y in [96,178]:self.frame(20,y,w-40,72,False)
    if k=='notification_persistent':path(self.g,'M82 91 H308',stroke='#a5b7c5',width=2)
   if k in ['dialog','confirmation']:
    for x in [22,178]:self.frame(x,h-70,144,48,False)
    path(self.b,'M24 63 H320',stroke='#43515f',width=.8)
   if k=='bottom_sheet':
    path(self.g,'M150 22 H210',stroke='#aab7c1',width=2)
    for y in [90,154,218]:self.frame(20,y,w-40,54,False)
  return self
 def preview_text(self,root):
  k=self.key;w=self.w;h=self.h
  def t(s,x,y,size=14,col='#eee7d9',anchor='start'):add(root,'text',x=x,y=y,font_family='sans-serif',font_size=size,fill=col,text_anchor=anchor).text=s
  if k.startswith('button_') or k in ['toast','tooltip','keyboard_letter','keyboard_space','keyboard_enter','keyboard_modifier','shoulder_cap','trigger_cap','controller_cap']:t(self.caption,w/2,h/2+5,15,anchor='middle')
  elif k=='progress_ring':t('72%',80,90,23,anchor='middle')
  elif k=='tabs':
   for i,s in enumerate(['Games','Apps','Tools']):t(s,59+i*114,39,14,anchor='middle')
  elif k=='section_header':t(self.caption,24,35,17)
  elif k in ['text_field','search_field','error_field']:
   t(self.caption,58 if k=='search_field' else 26,45,15)
   if k=='error_field':t('Name is required',26,85,12,'#ef8791')
  elif k in ['settings_row','menu_item']:t(self.caption,25,h/2+5,15)
  elif k=='menu_panel':
   for i,s in enumerate(['Open game','Launch display','Edit profile','Game details']):t(s,25,46+i*52,15)
  elif k=='card':t(self.caption,25,42,18);t('Your latest library entries',25,70,13,'#b5bdc6');t('Live content area',25,143,14,'#b5bdc6')
  elif k.startswith('notification_'):
   t(self.caption,80,39,15);t('Sample notification content',80,64,12,'#b5bdc6')
   if k=='notification_expanded':t('A longer message can wrap in this area.',25,112,13,'#b5bdc6');t('Open',w/2,177,14,anchor='middle')
   if k=='notification_group':
    for i,s in enumerate(['Game package ready','Media copied']):t(s,38,138+i*82,14)
  elif k in ['dialog','confirmation']:
   t(self.caption,25,43,18);t('This is live platform content.',25,99,14,'#b5bdc6');t('Cancel',94,h-40,14,anchor='middle');t('Continue',250,h-40,14,anchor='middle')
  elif k=='bottom_sheet':
   t(self.caption,25,65,20)
   for i,s in enumerate(['Open on top display','Edit game profile','Close']):t(s,38,124+i*64,15)
 def doc(self,state='master',layer=None,labels=False):
  mapped='idle' if state=='hovered' else state
  s=super().doc(mapped,layer,labels)
  if layer is None and state!='master':
   r=ET.fromstring(s)
   if state=='hovered':
    for g in r.findall('{'+SVG+'}g'):
     if g.get('id') in ['seam','core']:g.set('opacity','.60')
   if self.key.startswith('progress_') or self.key in ['section_header','toast','tooltip']:
    for child in list(r):
     if child.tag=='{'+SVG+'}rect' and child.get('stroke')=='#d5e7f2' or child.tag=='{'+SVG+'}path' and child.get('stroke')=='#c8d4df':r.remove(child)
   if state=='disabled':
    for child in r.findall('{'+SVG+'}text'):child.set('opacity','.42')
   s=ET.tostring(r,encoding='unicode')
  return s

def build(out):
 if out.exists():raise SystemExit('Preserved checkpoint already exists')
 for name in ['masters','layers','exports','previews','verification/evidence']:(out/name).mkdir(parents=True,exist_ok=True)
 assets=[Component(s).build() for s in SPECS];metadata=[]
 for a in assets:
  (out/'masters'/f'{a.key}.svg').write_text(a.doc(),encoding='utf8')
  for layer in ['cold','seam','core','symbol']:
   src=a.doc(layer=layer);(out/'layers'/f'{a.key}.{layer}.svg').write_text(src,encoding='utf8')
   for d in [1,2]:(out/'exports'/f'{a.key}.{layer}@{d}x.png').write_bytes(render(src,a.w*d))
  for state in STATES:(out/'exports'/f'{a.key}.{state}.preview.png').write_bytes(render(a.doc(state,labels=True),a.w*2))
  metadata.append({'id':a.key,'label':a.label,'roadmap':a.package,'size':[a.w,a.h],'layers':['cold','seam','core','symbol'],'states':STATES,'masterHasText':False,'touchTargetDp':48,'nativeIntegrated':False,'deviceVerified':False})
 cols=4;rows=math.ceil(len(assets)/cols);board=Image.new('RGBA',(1800,160+rows*242),'#090e14');d=ImageDraw.Draw(board)
 d.text((45,30),'CRAFTAGEDDON / CORE COMPONENT SYSTEM',font=font(34,True),fill='#eee7d9');d.text((47,83),f'ITERATION 04 / {len(assets)} VARIANTS / COLD STEEL + NEUTRAL MASKS + LIVE CONTENT',font=font(16),fill='#b5bdc6')
 for i,a in enumerate(assets):
  x=35+i%cols*440;y=125+i//cols*242;d.rounded_rectangle((x,y,x+420,y+224),8,fill='#10171e',outline='#2b3946');d.text((x+16,y+12),f'{a.package}  {a.label}',font=font(15,True),fill='#d2dbe2');fitpaste(board,a.doc('selected' if a.key.endswith(('on','checked','half')) else 'idle',labels=True),(x+18,y+43,384,159))
 board.convert('RGB').save(out/'previews/component-system-sheet.png')
 # A readable index plus separate sheets for each native-size state remain usable off-line.
 for start in range(0,len(assets),12):
  im=Image.new('RGBA',(1800,855),'#090e14');dr=ImageDraw.Draw(im);dr.text((40,24),f'CORE COMPONENTS / PAGE {start//12+1}',font=font(30,True),fill='#eee7d9')
  for i,a in enumerate(assets[start:start+12]):
   x=35+i%4*440;y=90+i//4*250;dr.text((x+12,y+5),a.label,font=font(16),fill='#cbd6df');fitpaste(im,a.doc('selected',labels=True),(x+15,y+40,390,190))
  im.convert('RGB').save(out/'previews'/f'components-page-{start//12+1:02}.png')
 (out/'components.json').write_text(json.dumps(metadata,indent=2)+'\n');tokens=copy.deepcopy(TOKENS);tokens['states']['hovered']=.22;tokens['previewEmissionGain']=2.8;(out/'tokens.json').write_text(json.dumps(tokens,indent=2)+'\n')
 (out/'README.md').write_text('# Iteration 04 — scope register and core component system\n\n46 original component variants expand ES-011..024 and begin the keyboard/controller cap families. Every master is layered cold/seam/core/symbol with no text. Labels in review images are illustrative live content. Eight state previews include hover, focus, selection, press, disabled and reduced motion. PNG layers are supplied at 1x/2x in complete-assets.zip. Native hit targets require at least 48dp padding. Fixed-size decorated assets must not be stretched blindly.\n\nThe source-register folder accounts for all retained cached files and proposes family mappings; it does not claim full visual approval. Frame material and composition are still subject to target-device and user acceptance. No native SystemUI integration or hardware change is included.\n',encoding='utf8')
 print(json.dumps({'components':len(assets),'svg':len(list(out.rglob('*.svg'))),'png':len(list(out.rglob('*.png')))}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(a.out.resolve())
