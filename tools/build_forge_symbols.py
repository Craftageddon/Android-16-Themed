"""Iteration 11: full named symbol catalog and remaining sculpted reference motifs."""
from pathlib import Path
import argparse,base64,copy,hashlib,io,json,math,random,shutil,subprocess,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import el,add,path,render,font,SVG
from build_symbols import NAMES,vector
from build_reference_forge import COLORS,LAYERS,FLAGS
from forge_library import symbol,layer,state,raster,xml,compose_layers,lighting_descriptor

ROOT=Path(__file__).resolve().parents[1]
CHANNELS={
 'signal':'M229 878 V1005 M504 699 V1005 M780 507 V1005 M1055 305 V1005',
 'hotspot':'M270 185 C133 339 133 581 270 716 M983 185 C1119 339 1119 581 983 716 M383 286 C316 397 316 523 383 625 M869 286 C936 397 936 523 869 625 M627 632 V924',
 'shield':'M278 416 C365 358 488 356 578 267 M676 267 C763 356 886 358 975 416 M343 670 C372 814 482 899 580 908 M671 908 C784 899 895 814 923 670 M343 584 C366 453 464 366 581 362 M671 362 C786 366 896 453 919 584',
 'cast':'M210 237 H1049 M141 298 V912 M1115 298 V912 M220 986 H1043 M300 416 C450 427 581 489 665 580 M742 640 C772 706 793 780 800 858 M305 586 C410 600 481 648 539 725 M606 802 Q616 825 620 858',
 'play':'M536 508 L719 626 L537 748 Z',
 'power_core':'',
}

def arc(cx,cy,r,a,b):
 p=lambda t:(cx+r*math.cos(math.radians(t)),cy+r*math.sin(math.radians(t)))
 x,y=p(a);xx,yy=p(b);return f'M{x:.2f} {y:.2f} A{r} {r} 0 0 1 {xx:.2f} {yy:.2f} '
CHANNELS['play']+=' '+''.join(arc(625,626,365,a,a+64) for a in [-77,13,103,193])
CHANNELS['power_core']=''.join(arc(625,625,338,a,a+50) for a in [-70,20,110,200])+''.join(arc(625,625,199,a,a+84) for a in [-87,3,93,183])

def hero(name,source):
 with Image.open(source) as im:w,h=im.size
 r,gs=__import__('forge_library').setup(w,h,name+' / sculpted master')
 # No texture pattern is used by the preserved cold raster. Remove unused texture references.
 for defs in r.findall('{'+SVG+'}defs'):
  for p in list(defs):
   if p.get('id')=='forged':defs.remove(p)
 add(gs['cold'],'image',href=f'../source/{name}-cold.png',width=w,height=h)
 for key,width,extra in [('reflection',22,{'filter':'url(#light-reflection)','opacity':'.5'}),('spill',18,{'filter':'url(#light-spill)'}),('seam',8,{}),('core',2,{})]:
  # Large optical artwork uses appropriately scaled blur rather than unit-sized control blur.
  for f in r.findall('.//{'+SVG+'}feGaussianBlur'):f.set('stdDeviation','5')
  path(gs[key],CHANNELS[name],stroke='white',width=width,**extra)
 cores={'hotspot':(627,477,49),'cast':(294,822,62),'power_core':(625,625,155)}
 if name in cores:
  x,y,rad=cores[name];defs=r.find('{'+SVG+'}defs');g=add(defs,'radialGradient',id='hot-spot',cx='.45',cy='.42',r='.58')
  for off,alpha in [(0,1),(.25,.9),(.65,.65),(1,0)]:add(g,'stop',offset=off,stop_color='white',stop_opacity=alpha)
  for key,scale,alpha in [('seam',1,1),('core',.84,.45),('spill',1.1,.7)]:
   add(gs[key],'circle',cx=x,cy=y,r=rad*scale,fill='url(#hot-spot)',opacity=alpha,**({'filter':'url(#light-spill)'} if key=='spill' else {}))
  rng=random.Random(11)
  for _ in range(65):
   a=rng.random()*math.tau;rr=math.sqrt(rng.random())*rad*.83;xx=x+math.cos(a)*rr;yy=y+math.sin(a)*rr
   path(gs['core'],f'M{xx:.2f} {yy:.2f} l{rad*.06:.2f} {-rad*.04:.2f}',stroke='white',width=max(.6,rad*.012),opacity=rng.uniform(.2,.7))
 path(gs['focus'],'M80 170 V80 H170 M1084 80 H1174 V170 M80 1084 V1174 H170 M1084 1174 H1174 V1084',stroke='white',width=4)
 path(gs['symbol'],'M1130 1100 l13 13 l-13 13 l-13 -13 Z','white')
 return r

def embedded_hero(r,data):
 q=copy.deepcopy(r)
 for n in q.findall('.//{'+SVG+'}image'):n.set('href','data:image/png;base64,'+data)
 return q

def write_asset(out,key,r,states,widths,texture,hero_data=None,metadata=None):
 logical=(metadata or {}).get('symbol',(metadata or {}).get('canonicalId',key))
 locked=logical.endswith('_off') or logical=='check_empty'
 (out/'masters'/f'{key}.svg').write_text(xml(r),encoding='utf8')
 def rast(q,width):
  if hero_data is not None:return Image.open(io.BytesIO(render(xml(embedded_hero(q,hero_data)),width))).convert('RGBA')
  return raster(q,width,texture)
 cached={}
 for name in LAYERS:
  for width in widths:
   im=rast(layer(r,name),width);im.save(out/'exports'/f'{key}.{name}.{width}.png')
   if width==widths[-1]:cached[name]=im
 for st,descriptor in states.items():compose_layers(cached,lighting_descriptor(descriptor,locked)).save(out/'exports'/f'{key}.{st}.preview.png')
 return {'id':key,'layers':LAYERS,'exportWidths':widths,'states':list(states),'emissionLockedOff':locked,'nativeIntegrated':False,'deviceVerified':False,**(metadata or {})}

def states_from(node):
 code="const {sample}=require('./tools/state_driver_v2.cjs');const flags="+json.dumps(FLAGS)+";process.stdout.write(JSON.stringify(Object.fromEntries(Object.entries(flags).map(([k,v])=>[k,sample(v)]))));"
 return json.loads(subprocess.check_output([node,'-e',code],cwd=ROOT,text=True))

def build(a):
 out=a.out.resolve();assert not out.exists()
 for sub in ['source','masters','exports','previews','android/res/drawable','verification/evidence']:(out/sub).mkdir(parents=True)
 provenance=json.loads(a.provenance.read_text());sources={x['name']:Path(x['path']) for x in provenance.pop('sources')};provenance['coldSources']=[]
 for name,source in sources.items():
  target=out/'source'/('steel-material-original.png' if name=='steel_material' else name+'-cold.png');shutil.copy2(source,target)
  provenance['coldSources'].append({'name':name,'file':target.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'modified':False})
 previous=ROOT/'iterations/10-reference-forge'
 for name in ['wifi','bluetooth','airplane']:
  source=previous/'source'/f'{name}-cold.png';shutil.copy2(source,out/'source'/source.name)
  provenance['coldSources'].append({'name':name,'file':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'modified':False,'fromIteration':10})
 original=out/'source/steel-material-original.png';encoded=base64.b64encode(original.read_bytes()).decode()
 proxy=el('svg',width=256,height=256,viewBox='0 0 256 256');add(proxy,'image',href='data:image/png;base64,'+encoded,width=256,height=256)
 (out/'source/steel-material.png').write_bytes(render(xml(proxy),256))
 provenance['textureProxy']={'file':'steel-material.png','size':[256,256],'method':'SVG image scaling with resvg; no painting, no emission; original preserved','sha256':hashlib.sha256((out/'source/steel-material.png').read_bytes()).hexdigest()}
 texture=base64.b64encode((out/'source/steel-material.png').read_bytes()).decode();states=states_from(a.node);rows=[]
 (out/'runtime-style.json').write_text(json.dumps({'schema':2,'colors':COLORS,'layerOrder':LAYERS,'sampleStates':states,'activationRule':'enabled && !cold && !emissionLockedOff && (selected || checked || on)','assetOverride':'Pass components.json emissionLockedOff to the state owner; explicit off geometry stays cold even if selected. Neutral selection/focus cues remain independent.','compactTreatment':'Flat neutral semantic geometry, tiny optional steady emission; focus and selection owned by container','motion':'Static, no timers or breathing','nativeIntegrated':False},indent=2)+'\n')
 for index,name in enumerate(NAMES):
  for optical in ['compact','detailed']:
   r=symbol(name,optical);key=name+'__'+optical;widths=[24,48] if optical=='compact' else [96,192]
   rows.append(write_asset(out,key,r,states,widths,texture,metadata={'type':'symbol','symbol':name,'optical':optical,'semanticGeometry':'original iteration 05 geometry; reworked optical material'}))
  (out/'android/res/drawable'/f'cg_rf_{name}.xml').write_text(vector(name).replace('#C9D4DE','#C0C7C9'),encoding='utf8')
  if (index+1)%24==0:print('Symbols',index+1,flush=True)
 order=['wifi','bluetooth','signal','hotspot','airplane','shield','cast','play','power_core']
 for name in order:
  r=ET.parse(previous/'masters'/f'{name}.svg').getroot() if name in ['wifi','bluetooth','airplane'] else hero(name,out/'source'/f'{name}-cold.png')
  data=base64.b64encode((out/'source'/f'{name}-cold.png').read_bytes()).decode()
  rows.append(write_asset(out,'hero-'+name,r,states,[256,512],texture,data,{'type':'hero','motif':name,'optical':'sculpted','sourceColdUnmodified':True}))
 # Full catalog: off + on side by side for every named symbol, compact companions underneath.
 for start in range(0,len(NAMES),32):
  board=Image.new('RGB',(1800,1440),'#090d12');d=ImageDraw.Draw(board)
  d.text((40,25),f'REFERENCE FORGE / SYMBOL CATALOG / {start//32+1:02}',font=font(34,True),fill='#eee7d9')
  d.text((42,80),'Cold + active sample / Explicit off symbols remain cold / Compact companion below',font=font(21),fill='#b5bdc6')
  for i,name in enumerate(NAMES[start:start+32]):
   x=35+i%8*222;y=145+i//8*308
   for st,xx in [('off',x+5),('on',x+108)]:
    im=Image.open(out/'exports'/f'{name}__detailed.{st}.preview.png').convert('RGBA');im.thumbnail((100,142),Image.Resampling.LANCZOS);board.paste(im,(xx,y),im)
   small=Image.open(out/'exports'/f'{name}__compact.off.preview.png').convert('RGBA');board.paste(small,(x+75,y+111),small)
   label=name.replace('_',' ');d.text((x+4,y+179),label,font=font(14),fill='#d5dce0')
  board.save(out/'previews'/f'symbol-catalog-{start//32+1:02}.png')
 board=Image.new('RGB',(1800,2460),'#090d12');d=ImageDraw.Draw(board)
 d.text((50,26),'CRAFTAGEDDON / NINE SCULPTED MOTIFS',font=font(37,True),fill='#eee7d9')
 d.text((52,80),'Cold masters + independent on-state light / Matching the original reference direction',font=font(22),fill='#b5bdc6')
 for i,name in enumerate(order):
  x=35+i%3*590;y=140+i//3*750;d.text((x+15,y),name.upper().replace('_',' '),font=font(23,True),fill='#eee7d9')
  for st,yy,labeltext in [('off',y+45,'OFF'),('on',y+390,'ON')]:
   im=Image.open(out/'exports'/f'hero-{name}.{st}.preview.png').convert('RGBA');im.thumbnail((315,315),Image.Resampling.LANCZOS);board.paste(im,(x+135,yy),im);d.text((x+18,yy+145),labeltext,font=font(21),fill='#b5bdc6')
 d.text((52,2410),'Actual layer renders. All source PNGs unchanged. Native and target validation pending.',font=font(22),fill='#b5bdc6')
 board.save(out/'previews/nine-motifs-off-on.png')
 (out/'components.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'source/GENERATION.json').write_text(json.dumps(provenance,indent=2)+'\n')
 shutil.copy2(ROOT/'tools/state_driver_v2.cjs',out/'source/state_driver_v2.cjs')
 print(json.dumps({'namedSymbols':len(NAMES),'opticalMasters':len(NAMES)*2,'sculptedMotifs':9,'totalMasters':len(rows),'pngs':len(list(out.rglob('*.png')))}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--provenance',type=Path,required=True);p.add_argument('--node',required=True);build(p.parse_args())
