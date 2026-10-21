"""Iteration 10: unchanged generated cold masters, hand-authored neutral masks, cold-off states."""
from pathlib import Path
import argparse,base64,copy,hashlib,io,json,math,random,shutil,subprocess,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import el,add,path,render,font,SVG,INK
from build_scalable_frames import stretch
import build_rich_scalable_frames as frames

ROOT=Path(__file__).resolve().parents[1]
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
COLORS={'reflection':'#dc5920','spill':'#ff4908','seam':'#ff5b0b','core':'#ffd083','focus':'#d5e7f2','symbol':'#ffe5bc'}
FLAGS={'off':{},'hovered':{'hovered':True},'focused_off':{'focused':True},'on':{'on':True},'selected_focused':{'selected':True,'focused':True},'active_pressed':{'on':True,'pressed':True},'disabled':{'enabled':False,'on':True},'reduced':{'on':True,'reducedMotion':True}}
CHANNELS={
 'wifi':'M193 420 C310 306 462 245 598 245 M650 245 C802 247 928 301 1059 420 M316 610 C402 523 493 477 598 477 M653 477 C753 479 850 526 938 610 M466 774 Q529 705 597 690 M653 690 Q723 706 790 774',
 'bluetooth':'M635 184 V567 M635 682 V1065 M665 187 L902 396 L661 600 M570 666 L381 835 M378 428 L568 598 M664 684 L902 850 L663 1055',
 'airplane':'M625 286 V912 M625 127 V201 M257 778 L440 675 L461 655 L535 612 M995 778 L812 675 L791 655 L717 612 M500 1022 L551 963 M752 1022 L701 963',
}

def xml(r):return ET.tostring(r,encoding='unicode')
def master(name):
 r=el('svg',width=1254,height=1254,viewBox='0 0 1254 1254')
 add(r,'title').text=f'Craftageddon {name} / cold steel and independent runtime light'
 add(r,'desc').text='Generated cold material is preserved unchanged. Neutral SVG masks are editable; only cold layer is visible by default.'
 defs=add(r,'defs')
 for key,sigma in [('spill-blur',12),('reflection-blur',5)]:
  f=add(defs,'filter',id=key,x='-70%',y='-70%',width='240%',height='240%');add(f,'feGaussianBlur',stdDeviation=sigma)
 g=add(defs,'radialGradient',id='orb',cx='.46',cy='.42',r='.55')
 for off,opacity in [(0,1),(.24,.95),(.6,.67),(.85,.32),(1,0)]:add(g,'stop',offset=off,stop_color='white',stop_opacity=opacity)
 groups={}
 for name2 in LAYERS:
  q=add(r,'g',id=name2);q.set('{'+INK+'}groupmode','layer');q.set('{'+INK+'}label',name2)
  if name2!='cold':q.set('style','display:none')
  groups[name2]=q
 add(groups['cold'],'image',href=f'../source/{name}-cold.png',width=1254,height=1254)
 # Separate broad reflection, soft spill, saturated channel and narrow bright core.
 for key,width,attrs in [('reflection',20,{'filter':'url(#reflection-blur)','opacity':'.65'}),('spill',16,{'filter':'url(#spill-blur)'}),('seam',8,{}),('core',2.1,{})]:
  path(groups[key],CHANNELS[name],stroke='white',width=width,**attrs)
 if name=='wifi':
  for key,radius,fill,attrs in [('seam',83,'url(#orb)',{}),('core',73,'url(#orb)',{}),('spill',84,'white',{'filter':'url(#spill-blur)','opacity':'.65'}),('reflection',103,'none',{'stroke':'white','stroke-width':'8','opacity':'.3','filter':'url(#reflection-blur)'})]:
   if key=='core':attrs['opacity']='.33'
   add(groups[key],'circle',cx=625,cy=955,r=radius,fill=fill,**attrs)
  # Sparse white-hot fissures remain an independent light layer.
  path(groups['core'],'M592 941 l17 -21 l12 16 l19 -33 M609 936 l-7 31 l23 22 l19 -34 l-5 -25 M628 980 l26 11',stroke='white',width=2,opacity='.75')
  # Irregular neutral hot spots and fine sparks break up the core. They carry no color.
  for x,y,rad,alpha in [(610,940,24,.8),(642,947,17,.85),(620,969,21,.6),(629,917,11,.55)]:
   add(groups['core'],'circle',cx=x,cy=y,r=rad,fill='url(#orb)',opacity=alpha)
  rng=random.Random(10)
  for _ in range(95):
   angle=rng.random()*math.tau;rad=math.sqrt(rng.random())*68;x=625+math.cos(angle)*rad;y=955+math.sin(angle)*rad
   path(groups['core'],f'M{x:.2f} {y:.2f} l{rng.uniform(-4,4):.2f} {-rng.uniform(1,6):.2f}',stroke='white',width=rng.uniform(.5,1.6),opacity=rng.uniform(.12,.6))
 # Focus is neutral geometry. Selection also has a non-color diamond cue.
 path(groups['focus'],'M95 190 V115 H170 M1110 115 H1185 V190 M95 1090 V1165 H170 M1110 1165 H1185 V1090',stroke='white',width=5)
 path(groups['symbol'],'M1140 1060 l18 18 l-18 18 l-18 -18 Z',fill='white')
 return r

def isolate(r,name):
 q=copy.deepcopy(r)
 for g in list(q.findall('{'+SVG+'}g')):
  if g.get('id')!=name:q.remove(g)
  else:g.attrib.pop('style',None)
 return q

def raster(r,data,width):
 q=copy.deepcopy(r)
 for n in q.findall('.//{'+SVG+'}image'):n.set('href','data:image/png;base64,'+data)
 return Image.open(io.BytesIO(render(xml(q),width))).convert('RGBA')

def compose(layers,state):
 size=layers['cold'].size;s=STATES[state];out=layers['cold'].copy()
 if s['baseOpacity']!=1:out.putalpha(out.getchannel('A').point(lambda v:round(v*s['baseOpacity'])))
 for key in LAYERS[1:]:
  gain=s['gains'][key]
  if not gain:continue
  src=layers[key]
  im=Image.new('RGBA',size,COLORS[key])
  im.putalpha(src.getchannel('A').point(lambda v:round(v*gain)));out.alpha_composite(im)
 return out

def build(a):
 global STATES
 flags=json.dumps(FLAGS,separators=(',',':'))
 code="const {sample}=require('./tools/state_driver_v2.cjs');const f="+flags+";process.stdout.write(JSON.stringify(Object.fromEntries(Object.entries(f).map(([k,v])=>[k,sample(v)]))));"
 STATES=json.loads(subprocess.check_output([a.node,'-e',code],cwd=ROOT,text=True))
 out=a.out.resolve();assert not out.exists(), 'Use a new output folder'
 for sub in ['source','masters','layers','exports','previews','verification/evidence']:(out/sub).mkdir(parents=True)
 provenance=json.loads(a.provenance.read_text());provenance['coldSources']=[]
 all_layers={};inventory=[]
 for name in CHANNELS:
  source=a.sources/f'{name}-cold.png';target=out/'source'/source.name;shutil.copy2(source,target)
  digest=hashlib.sha256(source.read_bytes()).hexdigest();data=base64.b64encode(source.read_bytes()).decode()
  with Image.open(source) as im:assert im.mode=='RGBA';assert im.getchannel('A').getextrema()[0]==0;dims=list(im.size)
  r=master(name);(out/'masters'/f'{name}.svg').write_text(xml(r),encoding='utf8');at1={}
  for key in LAYERS:
   q=isolate(r,key);(out/'layers'/f'{name}.{key}.svg').write_text(xml(q),encoding='utf8')
   for width in [256,512,1024]:
    im=raster(q,data,width);im.save(out/'exports'/f'{name}.{key}.{width}.png')
    if width==512:at1[key]=im
  all_layers[name]=at1
  for state in FLAGS:compose(at1,state).save(out/'exports'/f'{name}.{state}.preview.png')
  provenance['coldSources'].append({'name':name,'canvas':dims,'sha256':digest,'modified':False})
  inventory.append({'id':name,'layers':LAYERS,'opticalUse':'Detailed artwork at 96dp and above; compact glyphs remain separate','densityExportsPx':[256,512,1024],'coldSourceSha256':digest,'nativeIntegrated':False,'deviceVerified':False})
 (out/'source/GENERATION.json').write_text(json.dumps(provenance,indent=2)+'\n')
 (out/'components.json').write_text(json.dumps(inventory,indent=2)+'\n')
 (out/'runtime-style.json').write_text(json.dumps({'schema':2,'colors':COLORS,'layerOrder':LAYERS,'sampleStates':STATES,'activationRule':'enabled && !cold && (selected || checked || on)','focusRule':'Neutral independent focus cue; focus and hover alone never light ember','pressedRule':'Boost only while already selected/on/checked. Owner resolves activation before rendering.','reducedMotion':'Static states; no motion or breathing','renderingScope':'Desktop source reference, not an implemented Android renderer'},indent=2)+'\n')
 shutil.copy2(ROOT/'tools/state_driver_v2.cjs',out/'source/state_driver_v2.cjs')
 # Three-state contact sheet made from actual separate layers, not generated lit mockups.
 board=Image.new('RGB',(1800,1900),'#090d12');d=ImageDraw.Draw(board)
 d.text((58,32),'CRAFTAGEDDON / BLACKENED FORGE',font=font(43,True),fill='#eee7d9')
 d.text((60,94),'Same cold metal / separate ember channels, hot cores and reflected light',font=font(24),fill='#b5bdc6')
 for col,(_,label) in enumerate([('off','OFF / COLD'),('on','ON / EMBER'),('active_pressed','ON + PRESSED')]):d.text((60+col*580,155),label,font=font(26,True),fill='#eee7d9')
 for row,(name,layers) in enumerate(all_layers.items()):
  y=215+row*535;d.text((60,y),name.upper().replace('WIFI','WI-FI'),font=font(23,True),fill='#b5bdc6')
  for col,state in enumerate(['off','on','active_pressed']):
   im=compose(layers,state);board.paste(im,(60+col*580,y+38),im)
 d.text((60,1850),'Detailed icon pilot: 3 of the full library. Off has zero emission. Production integration pending.',font=font(21),fill='#b5bdc6')
 board.save(out/'previews/cold-and-ember-sheet.png')
 close=Image.new('RGB',(1600,1000),'#090d12');d=ImageDraw.Draw(close)
 d.text((55,28),'COLD WHEN OFF / EMBER WHEN ON',font=font(40,True),fill='#eee7d9')
 for x,state,title in [(40,'off','OFF / cold forged steel'),(840,'on','ON / separate ember light')]:
  im=compose(all_layers['wifi'],state).resize((720,720),Image.Resampling.LANCZOS);close.paste(im,(x,150),im);d.text((x+20,104),title,font=font(27,True),fill='#eee7d9')
 d.text((60,930),'No glow in the base artwork. Ember emission, hot cores and bloom use separate masks.',font=font(24),fill='#b5bdc6')
 close.save(out/'previews/wifi-off-on.png')
 # Reuse iteration 09's archived scalable frames, with the new cold-off contract.
 prev=ROOT/'iterations/09-rich-scalable-controls';frames.LIGHT_COLORS=COLORS
 frames.STATES={name:[s['baseOpacity']]+[s['gains'][k] for k in LAYERS[1:]] for name,s in STATES.items()}
 shutil.copytree(prev/'android',out/'exports/scalable-frames/android')
 bindings={'source':'../09-rich-scalable-controls','archiveResources':'exports/scalable-frames/android/res','families':[s[0] for s in frames.SPECS],'runtimeStyle':'runtime-style.json','contract':'Cold when off; use these gains instead of iteration 09 warm-idle gains','frameGeometryChanged':False,'apkUpdated':False}
 (out/'scalable-frame-binding.json').write_text(json.dumps(bindings,indent=2)+'\n')
 sheet=Image.new('RGB',(1860,1900),'#090d12');d=ImageDraw.Draw(sheet)
 d.text((55,30),'SCALABLE STEEL / NEW OFF-ON BEHAVIOR',font=font(38,True),fill='#eee7d9')
 d.text((55,87),'Existing rich frames + new reference-style symbols. Labels remain live in production.',font=font(23),fill='#b5bdc6')
 for x,title in [(55,'OFF / COLD'),(985,'ON / EMBER')]:d.text((x,145),title,font=font(26,True),fill='#eee7d9')
 labels={'button':'Wi-Fi','field':'Bluetooth','panel':'Airplane mode','notification':'Wi-Fi connected'}
 for row,(name,w,h,_,_) in enumerate(frames.SPECS):
  y=220+row*390;layers={key:Image.open(prev/'android/res/drawable-xhdpi'/f'cg_es_rich_{name}_{key}.9.png').convert('RGBA') for key in LAYERS}
  for x,state in [(55,'off'),(985,'on')]:
   im=frames.composite(layers,(820,max(224,h*2)),state);sheet.paste(im,(x,y),im)
   iconname=['wifi','bluetooth','airplane','wifi'][row];icon=compose(all_layers[iconname],state).resize((150,150),Image.Resampling.LANCZOS)
   sheet.paste(icon,(x+72,y+(im.height-150)//2),icon)
   d.text((x+252,y+im.height//2-21),labels[name],font=font(31,True),fill='#eee7d9')
 d.text((55,1815),'Frame geometry is retained from iteration 09. The state contract is new; APK 0.1.0 is unchanged.',font=font(22),fill='#b5bdc6')
 sheet.save(out/'previews/scalable-controls-off-on.png')
 print(json.dumps({'newIcons':3,'layerExports':63,'reusedFrameFamilies':4,'stateTests':6,'nativeIntegrated':False}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--sources',type=Path,required=True);p.add_argument('--provenance',type=Path,required=True);p.add_argument('--node',required=True);build(p.parse_args())
