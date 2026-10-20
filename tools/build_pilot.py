"""Build original, layered Ember Steel SVG components and reproducible review sheets.

Python 3.10+, Pillow 12.3.0, resvg_py 0.5.0. No network or private asset paths.
"""
from pathlib import Path
import argparse, copy, csv, hashlib, html, io, json, math, os, sys
import xml.etree.ElementTree as ET

if os.environ.get('CRAFTAGEDDON_RENDERLIB'):
    sys.path.insert(0, os.environ['CRAFTAGEDDON_RENDERLIB'])
import resvg_py
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',SVG); ET.register_namespace('inkscape',INK)
def tag(name): return '{'+SVG+'}'+name
def el(name, **attrs): return ET.Element(tag(name),{k.replace('_','-'):str(v) for k,v in attrs.items()})
def add(parent,name,**attrs):
    node=el(name,**attrs); parent.append(node); return node
def path(parent,d,fill='none',stroke=None,width=1,**attrs):
    if stroke: attrs.update(stroke=stroke,stroke_width=width,stroke_linejoin='round',stroke_linecap='round')
    return add(parent,'path',d=d,fill=fill,**attrs)
def poly(points):return 'M'+' L'.join(f'{x:g},{y:g}' for x,y in points)+' Z'
def chamfer(x,y,w,h,c=8):return poly([(x+c,y),(x+w-c,y),(x+w,y+c),(x+w,y+h-c),(x+w-c,y+h),(x+c,y+h),(x,y+h-c),(x,y+c)])
def ring(parent,cx,cy,r,thick,fill):
    add(parent,'circle',cx=cx,cy=cy,r=r,fill='none',stroke=fill,stroke_width=thick)
def gradient(defs,name,stops):
    g=add(defs,'linearGradient',id=name,x1='0',y1='0',x2='.25',y2='1')
    for off,col in stops:add(g,'stop',offset=off,stop_color=col)
def defs(root,rev):
    d=add(root,'defs')
    gradient(d,'steel',[(0,'#77828c'),(.12,'#363f48'),(.40,'#202830'),(.68,'#13191f'),(.87,'#454d55'),(1,'#151b22')])
    gradient(d,'face',[(0,'#252d35'),(.45,'#151b21'),(1,'#0b1016')])
    gradient(d,'copper',[(0,'#b98559'),(.24,'#614532'),(.5,'#372b23'),(.78,'#7e5639'),(1,'#211d1b')])
    gradient(d,'edge',[(0,'#a4aeb5'),(.2,'#535d66'),(.55,'#171f27'),(.9,'#606973'),(1,'#252e37')])
    f=add(d,'filter',id='bloom',x='-80%',y='-80%',width='260%',height='260%')
    add(f,'feGaussianBlur',stdDeviation='.9' if rev>1 else '1.6')
    return d

TOKENS={
 'schema':1,'theme':'Craftageddon Ember Steel','date':'2026-10-20',
 'colors':{'background':'#090e14','well':'#10171e','text':'#eee7d9','secondary':'#b5bdc6','steel':'#414b56','copper':'#795139','ember':'#ff6b24','hotCore':'#ffc078','focus':'#d5e7f2','warning':'#f3b865','error':'#ef8791','success':'#8ec4ae'},
 'states':{'cold':0,'idle':.14,'selected':.36,'focused':.36,'pressed':.70,'disabled':0,'reduced':.36},
 'motion':{'pressMs':160,'pressReleaseMs':120,'selectMs':180,'easing':'cubic-bezier(0.2,0,0,1)','breathing':False,'hidden':'stop','reduced':'static; no blur or transform'},
 'geometry':{'minimumTouchDp':48,'focusWidthDp':2,'contentSafeInsetDp':20,'compactGlyphDp':24},
 'rules':['disabled suppresses emission and selection','focus cue can coexist with selection','cold layers never contain orange pixels','status indicators never breathe','render text as live platform text','focus and selected cues do not rely on color']}

SPECS=[
 ('primary_button','Primary action',256,72,'Launch game'),('icon_socket','Icon socket',88,88,''),
 ('toggle','Toggle',104,56,''),('slider','Slider',280,56,''),
 ('notification','Notification frame',344,112,'Download ready'),('dialog','Dialog frame',344,212,'Choose a display'),
 ('quick_tile','Quick settings tile',152,100,'Wi-Fi'),('settings','Settings symbol',64,64,''),
 ('wifi','Compact Wi-Fi',24,24,''),('battery','Compact battery',28,24,''),
 ('navigation','Back / home navigation',112,48,''),('charging_ring','Charging ring',160,160,'72%'),
 ('controller_prompts','Controller prompts',272,64,''),('calibration','Stick / trigger calibration',280,160,'Left stick'),
 ('gaming_menu','Gaming menu',312,160,'Game controls'),('display_route','Display routing',312,128,'Display target'),
 ('game_profile','Per-game profile',312,136,'Balanced profile'),('performance','Fan / power / lights',312,168,'Device controls')]

class Asset:
 def __init__(self,spec,rev):
    self.key,self.label,self.w,self.h,self.caption=spec; self.rev=rev
    self.root=el('svg',width=self.w,height=self.h,viewBox=f'0 0 {self.w} {self.h}')
    add(self.root,'title').text=f'Craftageddon {self.label} — iteration {rev}'
    add(self.root,'desc').text='Original editable steel geometry. Neutral emission masks are hidden. No live text baked into master.'
    defs(self.root,rev)
    self.layers={}
    for name in ['cold','seam','core','symbol']:
      g=add(self.root,'g',id=name);g.set('{'+INK+'}groupmode','layer');g.set('{'+INK+'}label',name)
      if name in ('seam','core'):g.set('style','display:none')
      self.layers[name]=g
    self.b=self.layers['cold'];self.s=self.layers['seam'];self.c=self.layers['core'];self.g=self.layers['symbol']
 def frame(self,x,y,w,h,detail=True):
    c=min(12,h/5,w/7); outer=chamfer(x,y,w,h,c); inner=chamfer(x+7,y+7,w-14,h-14,max(3,c-4))
    path(self.b,outer,'#05090e',stroke='#020508',width=2)
    path(self.b,outer+' '+inner,'url(#steel)',fill_rule='evenodd')
    path(self.b,inner,'url(#face)',stroke='#060a0f',width=2)
    path(self.b,f'M{x+c} {y+1} H{x+w-c} L{x+w-2} {y+c}',stroke='#84909b',width=.8,opacity='.65')
    path(self.b,f'M{x+1} {y+h-c} L{x+c} {y+h-1} H{x+w-c}',stroke='#53606b',width=.8,opacity='.65')
    # Recessed neutral seams, discontinuous to avoid a neon border.
    seg=f'M{x+c+8} {y+5} H{x+w*.43} M{x+w*.58} {y+h-5} H{x+w-c-8}'
    path(self.b,seg,stroke='#03070b',width=2.6)
    path(self.s,seg,stroke='white',width=1.6)
    path(self.c,f'M{x+w*.33} {y+5} h9 M{x+w*.70} {y+h-5} h7',stroke='white',width=.6)
    if self.rev>1 and detail:
      # Broken secondary facets give the rails physical depth without invading text.
      for start,end in [(x+c+9,x+w*.42),(x+w*.56,x+w-c-10)]:
        path(self.b,poly([(start,y+1.5),(end-7,y+1.5),(end,y+3),(start+4,y+4.2)]),'#63707c',opacity='.55')
        path(self.b,poly([(start,y+h-1.5),(end,y+h-1.5),(end-6,y+h-4.3),(start+4,y+h-3)]),'#0a1017')
      crack=f'M{x+w*.47} {y+1} l-4 2 l3 3 l-2 1 M{x+w*.62} {y+h-1} l4 -2 l-2 -3'
      path(self.b,crack,stroke='#080c12',width=1.3)
      path(self.s,crack,stroke='white',width=.6)
    if detail:
      for px,py,sx,sy in [(x,y,1,1),(x+w,y,-1,1),(x,y+h,1,-1),(x+w,y+h,-1,-1)]:
        q=lambda a,b:(px+a*sx,py+b*sy)
        path(self.b,poly([q(0,c),q(c,0),q(c+9,3),q(8,8),q(3,c+9)]),'url(#copper)',stroke='#1b2025',width=.8)
        path(self.b,poly([q(3,c),q(c,3),q(c+2,6),q(6,c+2)]),'url(#edge)')
        path(self.s,poly([q(5,c-1),q(c-1,5),q(c+1,6),q(6,c+1)]),'white')
      # Designed scratches follow rim direction; not stochastic texture.
      for xx,yy in [(x+w*.22,y+2),(x+w*.78,y+h-3)]:path(self.b,f'M{xx:g} {yy:g} l7 1 l4 -1',stroke='#89939b',width=.45,opacity='.45')
 def circle(self,x,y,r):
    ring(self.b,x,y,r,9,'#05090d');ring(self.b,x,y,r-1,7,'url(#steel)');ring(self.b,x,y,r-6,2,'url(#copper)')
    add(self.b,'circle',cx=x,cy=y,r=r-8,fill='url(#face)',stroke='#05090d',stroke_width=2)
    for a in [-90,30,150]:
      rad=math.radians(a);px=x+(r-1)*math.cos(rad);py=y+(r-1)*math.sin(rad)
      path(self.b,poly([(px,py-6),(px+5,py),(px,py+6),(px-5,py)]),'url(#copper)',stroke='#0a0e14',width=1)
    path(self.s,f'M{x-r+5} {y} A{r-5} {r-5} 0 0 1 {x} {y-r+5}',stroke='white',width=1.7)
    path(self.s,f'M{x+r-5} {y} A{r-5} {r-5} 0 0 1 {x} {y+r-5}',stroke='white',width=1.7)
    add(self.c,'circle',cx=x,cy=y-r+5,r=1.6,fill='white')
    if self.rev>1:
      for a in range(-140,200,45):
        rad=math.radians(a);px=x+(r-1)*math.cos(rad);py=y+(r-1)*math.sin(rad)
        path(self.b,f'M{px:g} {py:g} l2 -2 l-1 -2',stroke='#7a8791',width=.55,opacity='.6')
 def symbol(self,d,width=2):path(self.g,d,stroke='#d0d8df',width=width)
 def build(self):
    k=self.key; w=self.w;h=self.h
    if k=='icon_socket':
      self.circle(44,44,34); self.symbol('M35 33 L55 44 L35 55 Z',2.5)
    elif k=='toggle':
      self.frame(8,10,88,36,False);self.circle(73,28,16)
      path(self.g,'M20 28 h13',stroke='#aebbc5',width=2)
    elif k=='slider':
      self.frame(8,21,264,14,False);path(self.g,'M23 28 H172',stroke='#6d7c89',width=3);self.circle(178,28,17)
      self.symbol('M174 23 v10 M181 23 v10',1)
    elif k=='settings':
      pts=[]
      for i in range(32):
        a=math.radians(i*11.25-95.625);r=24 if i%4<2 else 19
        pts.append((32+r*math.cos(a),32+r*math.sin(a)))
      path(self.b,poly(pts),'url(#steel)',stroke='#5c6874',width=1);ring(self.b,32,32,9,5,'url(#copper)');ring(self.b,32,32,6,2,'#03070c')
      ring(self.s,32,32,8,1.5,'white');add(self.c,'circle',cx=32,cy=24,r=1,fill='white')
    elif k=='wifi':
      self.symbol('M2 7 Q12 -1 22 7 M5 11 Q12 5 19 11 M8.5 15 Q12 12 15.5 15',2.4 if self.rev>1 else 1.7)
      add(self.g,'circle',cx=12,cy=19,r=2,fill='#d0d8df')
      # No texture/bloom at status size. One tiny optional seam.
      path(self.s,'M9 15 Q12 12.5 15 15',stroke='white',width=1)
    elif k=='battery':
      path(self.g,chamfer(2,5,22,15,2),stroke='#d0d8df',width=1.7)
      path(self.g,'M26 10 v5',stroke='#d0d8df',width=2)
      for i in range(3):path(self.g,chamfer(5+i*5,8,3,9,.5),'#d0d8df')
    elif k=='navigation':
      self.frame(4,4,48,40,False);self.frame(60,4,48,40,False)
      self.symbol('M32 14 L21 24 L32 34 M73 23 L84 14 L95 23 V34 H78 V23',2)
    elif k=='charging_ring':
      self.circle(80,80,64);ring(self.b,80,80,47,1,'#384550')
      path(self.g,'M80 40 L69 57 H80 L75 69 L91 51 H79 Z','#aebdc8')
    elif k=='controller_prompts':
      for i in range(4):self.circle(36+i*66,32,22)
      # Label order is an example convention, not an asserted physical map.
    elif k=='calibration':
      self.frame(6,6,w-12,h-12);self.circle(70,84,42)
      path(self.b,'M34 84 H106 M70 48 V120',stroke='#43515d',width=1)
      ring(self.g,70,84,10,1.5,'#becbd5');add(self.g,'circle',cx=70,cy=84,r=3,fill='#becbd5')
      self.frame(137,55,120,22,False);self.frame(137,94,120,22,False)
      path(self.g,'M147 66 H212 M147 105 H229',stroke='#a8b6c1',width=3)
    elif k=='display_route':
      self.frame(6,6,w-12,h-12)
      for x in [27,170]:
        path(self.b,chamfer(x,46,112,57,6),'url(#steel)',stroke='#56636f',width=1)
        path(self.b,chamfer(x+5,51,102,47,3),'#0b1118')
      self.symbol('M144 65 H163 M157 60 L163 65 L157 70 M163 84 H144 M150 79 L144 84 L150 89',1.8)
      path(self.s,'M34 101 H131',stroke='white',width=1.7)
    elif k=='gaming_menu':
      self.frame(6,6,w-12,h-12)
      for i in range(3):self.frame(22+i*94,58,80,78,False)
      self.symbol('M45 94 h32 M61 78 v32 M140 84 h26 v21 h-26 Z M234 84 l12 10 l-12 10',2)
    elif k=='game_profile':
      self.frame(6,6,w-12,h-12);self.circle(46,68,24)
      self.symbol('M39 58 L56 68 L39 78 Z',1.8)
      path(self.b,'M85 83 H280',stroke='#34424e',width=1)
      for x in [90,152,214]:self.frame(x,97,53,19,False)
    elif k=='performance':
      self.frame(6,6,w-12,h-12)
      for y in [62,99,136]:
        path(self.b,f'M27 {y+15} H284',stroke='#34424e',width=.8)
        self.frame(208,y-9,72,21,False)
      self.symbol('M28 60 l8 -8 l8 8 l-8 8 Z M28 92 H45 L36 106 Z M28 132 h17 v10 H28 Z',1.5)
    else:
      self.frame(6,6,w-12,h-12)
      if k=='notification':
        self.circle(45,56,26);self.symbol('M36 56 l7 7 l13 -17',2)
      elif k=='dialog':
        path(self.b,'M27 62 H317',stroke='#37434f',width=1)
        self.frame(23,148,143,44,False);self.frame(177,148,143,44,False)
      elif k=='quick_tile':
        self.symbol('M25 31 Q44 16 63 31 M31 39 Q44 29 57 39 M38 47 Q44 42 50 47',2.2)
        add(self.g,'circle',cx=44,cy=53,r=2.3,fill='#d0d8df')
    return self
 def preview_text(self,root):
    def text(s,x,y,size=14,color='#eee7d9',anchor='start'):
      add(root,'text',x=x,y=y,fill=color,font_family='sans-serif',font_size=size,text_anchor=anchor).text=s
    k=self.key
    if k=='primary_button':text(self.caption,128,42,17,anchor='middle')
    elif k=='notification':text(self.caption,87,44,16);text('Ready to install',87,69,13,'#b5bdc6');text('Preview content',87,90,10,'#a0aeb9')
    elif k=='dialog':
      text(self.caption,27,42,18);text('Open the game on the top screen?',27,91,14);text('Display behavior is a mockup.',27,116,12,'#b5bdc6');text('Cancel',94,175,14,anchor='middle');text('Open',248,175,14,anchor='middle')
    elif k=='quick_tile':text('Wi-Fi',24,78,15);text('On',126,32,11,anchor='end')
    elif k=='charging_ring':text('72%',80,101,25,anchor='middle');text('Charging',80,120,10,'#b5bdc6','middle')
    elif k=='controller_prompts':
      for i,l in enumerate('ABXY'):text(l,36+i*66,38,17,anchor='middle')
    elif k=='calibration':
      text('Stick & triggers',24,31,14);text('L2',140,48,10);text('R2',140,88,10);text('ILLUSTRATIVE',197,138,9,'#b5bdc6','middle')
    elif k=='gaming_menu':
      text('Game controls',24,35,17)
      for i,l in enumerate(['Input','Screen','Profile']):text(l,62+i*94,123,10,anchor='middle')
    elif k=='display_route':text('Display target',24,34,16);text('TOP',83,81,12,anchor='middle');text('BOTTOM',226,81,12,anchor='middle')
    elif k=='game_profile':
      text('Balanced profile',85,47,17);text('Per-app settings',85,70,12,'#b5bdc6')
      for i,l in enumerate(['Power','Input','Display']):text(l,116+i*62,110,9,anchor='middle')
    elif k=='performance':
      text('Device controls',24,33,17)
      for i,(a,b) in enumerate([('Fan','Auto'),('Power','Balanced'),('Lights','Ember')]):text(a,58,66+i*37,13);text(b,244,66+i*37,10,anchor='middle')
 def doc(self,state='master',layer=None,labels=False):
    root=copy.deepcopy(self.root)
    for name in ['cold','seam','core','symbol']:
      g=root.find(f"{{{SVG}}}g[@id='{name}']")
      if layer:
        if name!=layer:root.remove(g)
        else:g.attrib.pop('style',None)
      elif state!='master':
        g.attrib.pop('style',None)
        if name in ['seam','core']:
          opacity=TOKENS['states'][state]
          if self.rev>1:opacity=min(1,opacity*2.8)
          if self.key in ['wifi','battery','navigation'] and state not in ['cold','disabled']:opacity=.26
          # Masks remain white sources; tint happens only in state preview.
          for n in g.iter():
            for attr in ['fill','stroke']:
              if n.get(attr)=='white':n.set(attr,TOKENS['colors']['ember' if name=='seam' else 'hotCore'])
          g.set('opacity',str(opacity*(.85 if name=='core' else 1)))
          if self.rev>1 and state not in ['cold','disabled','reduced'] and self.w>40:
            halo=copy.deepcopy(g);halo.set('id',name+'-bloom');halo.set('filter','url(#bloom)');halo.set('opacity',str(opacity*.6));root.insert(list(root).index(g),halo)
        elif state=='disabled':g.set('opacity','.42')
    if layer is None and state!='master':
      if state in ['selected','focused','pressed','reduced'] and self.w>40:
        path(root,f'M{self.w*.4:g} {self.h-2:g} h{self.w*.2:g}',stroke='#c8d4df',width=2)
      if state in ['focused','pressed'] and self.w>40:
        add(root,'rect',x=1,y=1,width=self.w-2,height=self.h-2,rx=4,fill='none',stroke='#d5e7f2',stroke_width=2)
      if labels:self.preview_text(root)
    return ET.tostring(root,encoding='unicode')

def render(svg,w=None):
    opts={'svg_string':svg}
    if w:opts['width']=w
    return resvg_py.svg_to_bytes(**opts)
def font(size,bold=False):
    candidates=[Path('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf')),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    for p in candidates:
      if p.exists():return ImageFont.truetype(str(p),size)
    return ImageFont.load_default(size=size)
def fitpaste(board,svg,box):
    x,y,w,h=box
    tree=ET.fromstring(svg);vw,vh=[float(v) for v in tree.attrib['viewBox'].split()[2:]]
    display_width=max(1,round(min(w,h*vw/vh)))
    src=Image.open(io.BytesIO(render(svg,display_width))).convert('RGBA')
    scale=min(w/src.width,h/src.height);src=src.resize((round(src.width*scale),round(src.height*scale)),Image.Resampling.LANCZOS)
    board.alpha_composite(src,(x+(w-src.width)//2,y+(h-src.height)//2))
def sheet(out,assets,rev):
    board=Image.new('RGBA',(1800,1530),'#090e14');d=ImageDraw.Draw(board)
    d.text((55,32),'CRAFTAGEDDON / EMBER STEEL',font=font(36,True),fill='#eee7d9')
    d.text((57,84),f'ITERATION {rev:02d}  /  18 COMPONENT PILOT  /  PREVIEW CONTENT',font=font(17),fill='#b5bdc6')
    for i,a in enumerate(assets):
      x=45+(i%4)*435;y=135+(i//4)*266
      d.rounded_rectangle((x,y,x+414,y+246),radius=8,fill='#10171e',outline='#29343e')
      d.text((x+18,y+15),f'{i+1:02d}  {a.label}',font=font(17,True),fill='#d1d9de')
      fitpaste(board,a.doc('selected' if i in [1,6,11,14,15] else 'idle',labels=True),(x+20,y+52,374,170))
      if i>=12:d.text((x+18,y+222),'THOR / DESIGN SPECIMEN',font=font(10),fill='#8c9da9')
    d.text((930,1360),'STEEL FIRST. EMBER WITHIN.',font=font(28,True),fill='#eee7d9')
    d.text((930,1409),'Cold bases + neutral seam/core masks + live symbols.',font=font(17),fill='#b5bdc6')
    d.text((930,1440),'No ROM integration or device validation claimed.',font=font(17),fill='#b5bdc6')
    board.convert('RGB').save(out/'previews/pilot-sheet.png')

def statesheet(out,assets,rev):
    board=Image.new('RGBA',(1800,920),'#090e14');d=ImageDraw.Draw(board)
    d.text((40,28),'MATERIAL / INPUT STATES',font=font(32,True),fill='#eee7d9')
    states=['cold','idle','selected','focused','pressed','disabled','reduced']
    chosen=[assets[i] for i in [0,1,6,8]]
    for j,state in enumerate(states):d.text((38+j*252,94),state.upper(),font=font(18,True),fill='#b5bdc6')
    for i,a in enumerate(chosen):
      y=144+i*182;d.text((40,y),a.label,font=font(16),fill='#b5bdc6')
      for j,state in enumerate(states):fitpaste(board,a.doc(state,labels=True),(35+j*252,y+34,224,120))
    d.text((40,877),'Focus and selection coexist. Status glyphs are steady. Reduced motion uses static light.',font=font(17),fill='#b5bdc6')
    board.convert('RGB').save(out/'previews/state-sheet.png')

def write_contract(out,rev,assets):
    TOKENS['previewEmissionGain']=1 if rev==1 else 2.8
    (out/'tokens.json').write_text(json.dumps(TOKENS,indent=2)+'\n')
    meta=[]
    for a in assets:
      meta.append({'id':a.key,'label':a.label,'viewBox':[0,0,a.w,a.h],'layers':['cold','seam','core','symbol'],'safeInsetDp':20 if a.w>140 else 8,'smallSymbol':a.w<=32,'touchTargetDp':48,'liveTextBaked':False,'status':'Designed; desktop rendered','deviceVerified':False})
    (out/'components.json').write_text(json.dumps(meta,indent=2)+'\n')
    (out/'README.md').write_text(f'''# Iteration {rev:02d} — Ember Steel pilot\n\n18 original editable component specimens. The everyday material uses faceted dark steel, recessed wells, structural copper and discontinuous ember channels. Detailed and compact symbols intentionally differ.\n\n- `masters/`: Inkscape-compatible layered SVGs; emission layers hidden by default.\n- `layers/`: individual cold, seam, core and symbol layers. White masks contain alpha, never baked orange. Empty mask layers are intentional for compact battery.\n- `exports/`: transparent 1x and 2x PNG cold/symbol layers and neutral masks. State PNGs are review-only.\n- `previews/`: contact/state sheets; labels and values are illustrative live-content examples.\n- `components.json`, `tokens.json`: geometry and state contract.\n\nThe exported frame sizes are fixed pilot specimens. Do not stretch textured bevels; use native procedural corners or explicitly authored nine-patches in a later integration pass. `symbol` is a separate semantic layer. Keyboard, gamepad focus, state handling, hardware and screen routing are design handoffs until integrated and tested.\n\nAll 103 roadmap packages remain tracked separately. This checkpoint does not complete the ROM or whole-library rework. No device was modified or flashed.\n''',encoding='utf-8')

def build(rev,out):
    if out.exists():raise SystemExit('Refusing to overwrite preserved iteration: '+str(out))
    for sub in ['masters','layers','exports','previews','verification/evidence']:(out/sub).mkdir(parents=True,exist_ok=True)
    assets=[Asset(s,rev).build() for s in SPECS]
    for a in assets:
      (out/'masters'/f'{a.key}.svg').write_text(a.doc(),encoding='utf-8')
      for layer in ['cold','seam','core','symbol']:
        src=a.doc(layer=layer);(out/'layers'/f'{a.key}.{layer}.svg').write_text(src,encoding='utf-8')
        for density in [1,2]:(out/'exports'/f'{a.key}.{layer}@{density}x.png').write_bytes(render(src,a.w*density))
      for state in TOKENS['states']:(out/'exports'/f'{a.key}.{state}.preview.png').write_bytes(render(a.doc(state,labels=True),a.w*2))
    write_contract(out,rev,assets);sheet(out,assets,rev);statesheet(out,assets,rev)
    print(json.dumps({'iteration':rev,'components':len(assets),'svg':len(list(out.rglob('*.svg'))),'png':len(list(out.rglob('*.png')))}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--iteration',type=int,choices=[1,2,3],required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();build(a.iteration,a.out.resolve())
