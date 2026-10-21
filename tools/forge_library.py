"""Shared original forged geometry: real cold material, separate neutral runtime masks."""
import base64,copy,io,math,xml.etree.ElementTree as ET
from PIL import Image
from build_pilot import Asset,SVG,INK,el,add,path,poly,chamfer,defs,render
from build_components import Component
from build_symbols import geometry,circle
from build_reference_forge import COLORS,LAYERS

def xml(r):return ET.tostring(r,encoding='unicode')
def setup(w,h,title,texture='../source/steel-material.png',view=None):
 r=el('svg',width=w,height=h,viewBox=view or f'0 0 {w} {h}')
 add(r,'title').text='Craftageddon Reference Forge / '+title
 add(r,'desc').text='Cold material visible; independent neutral light/focus/selection masks hidden. No live text baked into artwork.'
 d=defs(r,11)
 # Opaque cold material is sampled through editable vector shapes, never recolored with emission.
 p=add(d,'pattern',id='forged',patternUnits='userSpaceOnUse',width=76,height=76)
 add(p,'image',href=texture,width=76,height=76,preserveAspectRatio='xMidYMid slice')
 for gid,cols in [('steel',['#7e8588','#292d31','#111519','#353b40','#090d11']),('edge',['#929390','#3c4145','#111418','#596066','#111419']),('copper',['#9a7251','#4f392c','#211d1b','#674733','#161516'])]:
  g=d.find(f"{{{SVG}}}linearGradient[@id='{gid}']")
  for n in list(g):g.remove(n)
  for i,col in enumerate(cols):add(g,'stop',offset=i/(len(cols)-1),stop_color=col)
 for name,sigma in [('light-spill',1.5),('light-reflection',.65)]:
  f=add(d,'filter',id=name,x='-100%',y='-100%',width='300%',height='300%');add(f,'feGaussianBlur',stdDeviation=sigma)
 groups={}
 for name in LAYERS:
  g=add(r,'g',id=name);g.set('{'+INK+'}groupmode','layer');g.set('{'+INK+'}label',name)
  if name!='cold':g.set('style','display:none')
  groups[name]=g
 return r,groups

def joint(g,x,y,size):
 pts=[(x,y-size),(x+size*.40,y-size*.30),(x+size,y),(x+size*.30,y+size*.32),(x,y+size),(x-size*.32,y+size*.30),(x-size,y),(x-size*.30,y-size*.30)]
 path(g,poly(pts),'url(#copper)',stroke='#080b0e',width=.7)
 path(g,poly([(x,y-size*.82),(x,y),(x-size*.62,y)]),'#82715e',opacity='.60')
 path(g,poly([(x+size*.65,y),(x,y),(x,y+size*.80)]),'#171719')
 add(g,'circle',cx=x,cy=y,r=max(.45,size*.13),fill='#a28d74',stroke='#191b1b',stroke_width='.35')

def steel(g,d,width=2.7,fill=False):
 path(g,d,'url(#edge)' if fill else 'none',stroke='#020509',width=width+1.0)
 path(g,d,'url(#forged)' if fill else 'none',stroke='url(#edge)',width=width)
 path(g,d,'url(#forged)' if fill else 'none',stroke='url(#forged)',width=width*.72)
 path(g,d,stroke='#080b0e',width=max(.28,width*.22))
 path(g,d,stroke='#654831',width=max(.09,width*.05),transform='translate(.13 .17)',opacity='.85')

def lights(groups,d,width,core=True):
 path(groups['seam'],d,stroke='white',width=width)
 if core:path(groups['core'],d,stroke='white',width=width*.23)
 path(groups['spill'],d,stroke='white',width=width*2.3,filter='url(#light-spill)')
 path(groups['reflection'],d,stroke='white',width=width*3.0,filter='url(#light-reflection)',opacity='.50')

def cues(groups,w,h,compact=False):
 if compact:return
 z=min(4,w/18,h/14);pad=max(1,z*.5)
 path(groups['focus'],f'M{pad} {pad+z*2} V{pad} H{pad+z*2} M{w-pad-z*2} {pad} H{w-pad} V{pad+z*2} M{pad} {h-pad-z*2} V{h-pad} H{pad+z*2} M{w-pad-z*2} {h-pad} H{w-pad} V{h-pad-z*2}',stroke='white',width=max(.7,z*.3))
 x=w-8;y=h-8;s=min(2.2,w/24,h/24);path(groups['symbol'],poly([(x,y-s),(x+s,y),(x,y+s),(x-s,y)]),'white')

def symbol(name,optical):
 compact=optical=='compact';size=24 if compact else 96
 r,groups=setup(size,size,name+' / '+optical,view='-3 -3 30 30' if not compact else '0 0 24 24')
 for i,(d,fill) in enumerate(geometry(name)):
  if compact:
   path(groups['cold'],d,'#c0c7c9' if fill else 'none',stroke='#c0c7c9',width=1.7 if fill else 1.85)
   if i==0:path(groups['seam'],d,stroke='white',width=.35,stroke_dasharray='1.5 120')
  else:
   steel(groups['cold'],d,2.65,fill)
   # Routed within the dark carved center. Core and spill remain separate and neutral.
   lights(groups,d,.31)
 # Small-symbol focus/selection belongs to the interactive owner. Detailed specimens show both.
 if not compact:
  path(groups['focus'],'M-2 2 V-2 H2 M22 -2 H26 V2 M-2 22 V26 H2 M22 26 H26 V22',stroke='white',width='.35')
  path(groups['symbol'],'M24 23 l.7 .7 l-.7 .7 l-.7 -.7 Z','white')
 return r

class ForgedMixin:
 def forge_setup(self):
  self.root,self.layers=setup(self.w,self.h,self.label)
  self.b=self.layers['cold'];self.s=self.layers['seam'];self.c=self.layers['core']
  # Legacy builders write semantic details to g. Fold those details into the persistent cold layer.
  self.g=el('g',id='persistent-details');self.b.append(self.g)
 def frame(self,x,y,w,h,detail=True):
  rim=min(9,max(2.5,h*.12));c=min(12,max(2.5,h*.20),w/6)
  outer=chamfer(x,y,w,h,c);inside=chamfer(x+rim,y+rim,max(1,w-2*rim),max(1,h-2*rim),max(1,c-rim*.5))
  path(self.b,outer,'url(#edge)',stroke='#020508',width=1.5)
  middle=chamfer(x+1.3,y+1.3,max(1,w-2.6),max(1,h-2.6),max(1,c-1))
  path(self.b,middle+' '+inside,'url(#forged)',fill_rule='evenodd')
  path(self.b,inside,'#10151b',stroke='#03060a',width=1.3)
  path(self.b,inside,stroke='#684a34',width='.55')
  path(self.b,f'M{x+c} {y+1.3} H{x+w-c}',stroke='#7e8587',width='.65',opacity='.6')
  off=rim*.61;end=c+rim*.5
  rails=f'M{x+end} {y+off} H{x+w-end} M{x+end} {y+h-off} H{x+w-end}'
  if h>70:rails+=f' M{x+off} {y+end} V{y+h-end} M{x+w-off} {y+end} V{y+h-end}'
  path(self.b,rails,stroke='#010407',width=max(1.2,rim*.28))
  lights(self.layers,rails,max(.55,rim*.16))
  if detail and min(w,h)>33:
   j=min(7,rim*.85)
   for xx,yy in [(x+rim*.55,y+rim*.55),(x+w-rim*.55,y+rim*.55),(x+rim*.55,y+h-rim*.55),(x+w-rim*.55,y+h-rim*.55)]:joint(self.b,xx,yy,j)
 def circle(self,x,y,r):
  rim=min(8,max(2,r*.25))
  path(self.b,circle(x,y,r),fill='url(#edge)',stroke='#030609',width=1.5)
  path(self.b,circle(x,y,r-1.2),fill='url(#forged)')
  add(self.b,'circle',cx=x,cy=y,r=max(.5,r-rim),fill='#10151b',stroke='#684831',stroke_width='.6')
  radius=r-rim*.55;d=''
  for start,end in [(-79,-11),(11,79),(101,169),(191,259)]:
   point=lambda a:(x+radius*math.cos(math.radians(a)),y+radius*math.sin(math.radians(a)))
   a,b=point(start),point(end);d+=f'M{a[0]:.3f} {a[1]:.3f} A{radius} {radius} 0 0 1 {b[0]:.3f} {b[1]:.3f} '
  path(self.b,d,stroke='#020407',width=max(1.4,rim*.35));lights(self.layers,d,max(.65,rim*.17))
  if r>12:
   for angle in [-90,0,90,180]:
    a=math.radians(angle);joint(self.b,x+(r-1)*math.cos(a),y+(r-1)*math.sin(a),min(7,r*.20))
 def symbol(self,d,width=2):
  steel(self.b,d,max(1.5,width),False)
  path(self.b,d,stroke='#bdc4c8',width=max(.6,width*.40))
  lights(self.layers,d,max(.4,width*.23))
 def finish(self):
  # Persistent neutral labels/glyph details remain visible when all emission is off.
  self.b.remove(self.g);self.b.append(self.g)
  for n in self.b.iter():
   if n.get('fill')=='url(#steel)':n.set('fill','url(#forged)')
   if n.get('stroke')=='url(#steel)':n.set('stroke','url(#forged)')
  cues(self.layers,self.w,self.h,self.w<40)
  return self.root

class ForgedComponent(ForgedMixin,Component):
 def __init__(self,s):super().__init__(s);self.forge_setup()
class ForgedPilot(ForgedMixin,Asset):
 def __init__(self,s):super().__init__(s,11);self.forge_setup()

def layer(root,name):
 q=copy.deepcopy(root)
 for g in list(q.findall('{'+SVG+'}g')):
  if g.get('id')!=name:q.remove(g)
  else:g.attrib.pop('style',None)
 if name!='cold':
  for d in q.findall('{'+SVG+'}defs'):
   for n in list(d):
    if n.get('id')=='forged':d.remove(n)
 return q

def embed(root,texture_data):
 q=copy.deepcopy(root)
 for n in q.findall('.//{'+SVG+'}image'):
  if 'steel-material.png' in n.get('href',''):n.set('href','data:image/png;base64,'+texture_data)
 return q

def raster(root,width,texture_data):return Image.open(io.BytesIO(render(xml(embed(root,texture_data)),width))).convert('RGBA')

def compose_layers(layers,descriptor):
 out=layers['cold'].copy();gain=descriptor['baseOpacity']
 if gain!=1:out.putalpha(out.getchannel('A').point(lambda v:round(v*gain)))
 for key in LAYERS[1:]:
  gain=descriptor['gains'][key]
  if gain:
   im=Image.new('RGBA',out.size,COLORS[key]);im.putalpha(layers[key].getchannel('A').point(lambda v:round(v*gain)));out.alpha_composite(im)
 return out

def lighting_descriptor(descriptor,locked=False):
 q=copy.deepcopy(descriptor)
 if locked:
  for key in ['reflection','spill','seam','core']:q['gains'][key]=0
 return q

def state(root,descriptor,labels=None):
 q=copy.deepcopy(root)
 d=q.find('{'+SVG+'}defs')
 for g in q.findall('{'+SVG+'}g'):
  key=g.get('id');g.attrib.pop('style',None)
  gain=descriptor['baseOpacity'] if key=='cold' else descriptor['gains'].get(key,0)
  g.set('opacity',str(gain))
  if key!='cold':
   f=add(d,'filter',id='tint-'+key,x='-100%',y='-100%',width='300%',height='300%',color_interpolation_filters='sRGB')
   add(f,'feFlood',flood_color=COLORS[key]);add(f,'feComposite',in2='SourceGraphic',operator='in')
   g.set('filter','url(#tint-'+key+')')
 if labels:labels(q)
 return q

def unique(root,prefix):
 q=copy.deepcopy(root);ids={n.get('id'):prefix+n.get('id') for n in q.iter() if n.get('id')}
 for n in q.iter():
  for key,value in list(n.attrib.items()):
   if key=='id':n.set(key,ids[value]);continue
   for old,new in ids.items():
    value=value.replace('url(#'+old+')','url(#'+new+')')
    if value=='#'+old:value='#'+new
   n.set(key,value)
 return q
