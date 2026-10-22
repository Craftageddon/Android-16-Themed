"""Original Reference Forge atmosphere: cold vector structures, neutral masks, live content.

Creates wallpaper surfaces, boot/recovery/loading and charging specimens. Never
rewrites a packaged iteration and never bakes emission into a production base.
"""
from pathlib import Path
import argparse,base64,copy,hashlib,html,json,math,shutil,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import add,path,poly,chamfer,font,SVG
from forge_library import ForgedPilot,lights,state,unique,xml,raster,layer,compose_layers
from build_forge_symbols import write_asset

ROOT=Path(__file__).resolve().parents[1]
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']

def crest():
 o=ForgedPilot(('forge_crest','Forge crest',512,512,''))
 for rad in [220,178,123]:o.circle(256,256,rad)
 # Original anvil/hammer crest: cold structural plates, routed channels and joints.
 shape='M149 225 H363 L335 257 H290 V300 H337 L356 328 H156 L176 300 H222 V257 H174 Z'
 path(o.b,shape,'url(#edge)',stroke='#020509',width=5)
 path(o.b,'M159 229 H352 L329 251 H283 V306 H329 L339 320 H173 L183 306 H229 V251 H179 Z','url(#forged)')
 path(o.b,'M172 235 H340 M239 262 V297 M275 262 V297 M191 314 H321',stroke='#03060a',width=5)
 lights(o.layers,'M172 235 H340 M239 262 V297 M275 262 V297 M191 314 H321',2.4)
 # Riveted diagonal ribs stay cold; they do not introduce warm ambient material.
 for angle in [45,135,225,315]:
  a=math.radians(angle);xx=256+math.cos(a)*153;yy=256+math.sin(a)*153
  path(o.b,poly([(xx-7,yy-4),(xx+13,yy-12),(xx+7,yy+6),(xx-10,yy+12)]),'url(#copper)',stroke='#070b10',width=2)
 return o.finish(),512,512

def chamber():
 o=ForgedPilot(('charge_chamber','Charge chamber',512,512,''));o.frame(18,18,476,476)
 # Reuse the accepted sculpted core unchanged, including its independently authored masks.
 hero=unique(ET.parse(ROOT/'iterations/11-forge-symbol-library/masters/hero-power_core.svg').getroot(),'sculpted-')
 for image in hero.findall('.//{'+SVG+'}image'):
  name=Path(image.get('href')).name
  image.set('href','data:image/png;base64,'+base64.b64encode((ROOT/'iterations/11-forge-symbol-library/source'/name).read_bytes()).decode())
 for d in hero.findall('{'+SVG+'}defs'):
  for node in d:o.root.find('{'+SVG+'}defs').append(copy.deepcopy(node))
 for k in LAYERS:
  if k in ['focus','symbol']:continue
  g=hero.find('{'+SVG+'}g[@id="sculpted-'+k+'"]');g.attrib.pop('style',None);g.attrib.pop('id',None)
  wrap=add(o.layers[k],'g',transform='translate(38 38) scale(.348)');wrap.append(copy.deepcopy(g))
 return o.finish(),512,512

def aperture():
 o=ForgedPilot(('loading_aperture','Loading aperture',256,256,''));o.circle(128,128,106);o.circle(128,128,73)
 for i in range(8):
  a=math.radians(i*45);xx=128+math.cos(a)*49;yy=128+math.sin(a)*49
  o.symbol(f'M{xx-6:.2f} {yy-6:.2f} l12 12 M{xx+6:.2f} {yy-6:.2f} l-12 12',2)
 return o.finish(),256,256

def plate(w,h,quiet=False):
 o=ForgedPilot(('wallpaper','Quiet forged plates' if quiet else 'Forged plates',w,h,''))
 add(o.b,'rect',width=w,height=h,fill='#070b10')
 # Separate edge ribs leave the reading region uninterrupted.
 margin=min(w,h)*.035;bw=min(w,h)*.095
 for side in [0,1]:
  x=margin if side==0 else w-margin-bw
  for i in range(4):
   y=margin+i*(h-2*margin)/4;hh=(h-2*margin)/4-12
   o.frame(x,y,bw,hh,not quiet)
   if not quiet:
    path(o.b,f'M{x+bw*.3} {y+hh*.25} L{x+bw*.7} {y+hh*.72}',stroke='#02060a',width=4)
    lights(o.layers,f'M{x+bw*.3} {y+hh*.25} L{x+bw*.7} {y+hh*.72}',max(1,w/900))
 # Paired header/foot plates, sized directly rather than texture stretching.
 for y in [margin,h-margin-bw*.52]:o.frame(margin+bw+18,y,w-2*(margin+bw+18),bw*.52,not quiet)
 return o.finish()

def put(root,r,x,y,w,h,desc,prefix):
 q=unique(state(r,desc),prefix);q.set('x',str(x));q.set('y',str(y));q.set('width',str(w));q.set('height',str(h));root.append(q)

def live(root,s,x,y,size=24,center=True,color='#eee7d9',bold=False):
 n=add(root,'text',x=x,y=y,font_family='Segoe UI, sans-serif',font_size=size,font_weight=700 if bold else 400,text_anchor='middle' if center else 'start',fill=color);n.text=s

def build(out,resume=False):
 assert not out.exists() or (resume and not (out/'complete-assets.zip').exists()),'Packaged iterations are immutable'
 for folder in ['masters','source','exports','scenes','previews','verification/evidence']:(out/folder).mkdir(parents=True,exist_ok=True)
 origin=ROOT/'iterations/11-forge-symbol-library/source'
 for f in ['steel-material.png','steel-material-original.png','power_core-cold.png']:shutil.copy2(origin/f,out/'source'/f)
 texture=base64.b64encode((out/'source/steel-material.png').read_bytes()).decode()
 shutil.copy2(ROOT/'iterations/13-forge-android-and-thor-flows/runtime-style.json',out/'runtime-style.json')
 states=json.loads((out/'runtime-style.json').read_text())['sampleStates'];assets={};rows=[]
 for key,builder in [('forge_crest',crest),('charge_chamber',chamber),('loading_aperture',aperture)]:
  r,w,h=builder();assets[key]=(r,w,h);rows.append(write_asset(out,key,r,states,[w,w*2],texture,metadata={'type':'atmosphere-component','canonicalId':key,'size':[w,h],'labelsBaked':False,'fixedAspect':True}));print('master',key,flush=True)
 wallpapers=[]
 for key,w,h,anchor,region in [('thor-upper',1920,1080,(.76,.53),[.16,.18,.40,.64]),('thor-lower',1240,1080,(.50,.65),[.16,.18,.68,.24]),('phone',1080,2400,(.50,.66),[.16,.15,.68,.29])]:
  for quiet in [False,True]:
   name='wallpaper-'+key+('-quiet' if quiet else '')
   r=plate(w,h,quiet);size=min(w,h)*(.32 if quiet else .49);x=w*anchor[0]-size/2;y=h*anchor[1]-size/2
   # Fold nested crest layers into matching root layers, preserving independent masks.
   c,cw,ch=assets['forge_crest'];cq=unique(c,'crest-');defs=r.find('{'+SVG+'}defs')
   for d in cq.findall('{'+SVG+'}defs'):
    for node in d:defs.append(copy.deepcopy(node))
   for k in LAYERS:
    cg=cq.find('{'+SVG+'}g[@id="crest-'+k+'"]');cg.attrib.pop('style',None);cg.attrib.pop('id',None)
    host=r.find('{'+SVG+'}g[@id="'+k+'"]');wrap=add(host,'g',transform=f'translate({x} {y}) scale({size/cw})',opacity='.30' if quiet else '.74');wrap.append(copy.deepcopy(cg))
   # Wallpaper selection/focus belongs to the launcher owner, not decorative background art.
   for k in ['focus','symbol']:
    host=r.find('{'+SVG+'}g[@id="'+k+'"]')
    for child in list(host):host.remove(child)
   (out/'masters'/f'{name}.svg').write_text(xml(r),encoding='utf8');cached={}
   for k in LAYERS:
    im=raster(layer(r,k),w,texture);im.save(out/'exports'/f'{name}.{k}.{w}.png');cached[k]=im
   for st in ['off','on','reduced']:compose_layers(cached,states[st]).save(out/'previews'/f'{name}.{st}.preview.png')
   wallpapers.append({'id':name,'size':[w,h],'readingRegionNormalized':region,'quiet':quiet,'production':'Cold plus separate neutral masks; lit PNGs are previews only','nativeIntegrated':False});print('wallpaper',name,flush=True)
 scenes=[]
 def scene(key,title,subtitle,kind='forge_crest',active=False,progress=None,warning=False):
  w,h=1080,1920;r=plate(w,h,True)
  # A scene is an explicit composition preview. Its labels are editable SVG text.
  r=state(r,states['off']);r.set('data-kind','scene-preview');r.set('data-state','on' if active else 'off')
  master,aw,ah=assets[kind];size=600 if kind!='loading_aperture' else 320
  put(r,master,(w-size)/2,500,size,size,states['on' if active else 'off'],'hero-')
  live(r,'CRAFTAGEDDON',w/2,330,64,bold=True);live(r,title,w/2,1250,46,bold=True);live(r,subtitle,w/2,1320,27,color='#b5bdc6')
  if progress is not None:
   # Real progress geometry is distinct from emission; full/paused/off remain meaningful.
   o=ForgedPilot(('progress','Progress',640,72,''));o.frame(4,4,632,64);track='M32 36 H608';path(o.b,track,stroke='#03070b',width=10)
   if progress>0:
    line=f'M32 36 H{32+576*min(100,progress)/100}'
    path(o.b,line,stroke='#bbc4ca',width=5);lights(o.layers,line,2)
   put(r,o.finish(),220,1400,640,72,states['on' if active else 'off'],'progress-');live(r,str(progress)+'%',w/2,1540,42,bold=True)
  if warning:live(r,'Automatic protection is active',w/2,1645,28,color='#d5dde2')
  if key=='recovery-menu':
   for j,label in enumerate(['Reboot system','Apply update','Factory reset','Advanced']):
    ob=ForgedPilot(('action','Recovery action',760,76,''));ob.frame(5,5,750,66);put(r,ob.finish(),160,1390+j*92,760,76,states['focused_off' if j==0 else 'off'],f'action{j}-');live(r,label,w/2,1438+j*92,29)
  (out/'scenes'/f'{key}.svg').write_text(xml(r),encoding='utf8');raster(r,w,texture).save(out/'scenes'/f'{key}.png')
  scenes.append({'id':key,'title':title,'size':[w,h],'hero':kind,'on':active,'progress':progress,'warning':warning,'liveText':True,'fixtureOnly':True,'nativeIntegrated':False});print('scene',key,flush=True)
 for key,title,sub,on,p in [('boot-cold','Preparing to start','',False,None),('boot-assembly','Starting','Loading the system',True,20),('boot-ready','Ready','Your session is starting',True,100),('boot-error','Could not start','Open recovery for available options',False,None)]:scene(key,title,sub,active=on,progress=p)
 for key,title,sub,on,p,warn in [('charge-disconnected','Power disconnected','Connect a charger to continue',False,25,False),('charge-connected','Power connected','Checking charging conditions',True,25,False),('charge-25','Charging','Connected to power',True,25,False),('charge-50','Charging','Connected to power',True,50,False),('charge-80','Charge limit reached','Charging paused at your selected limit',False,80,False),('charge-full','Fully charged','100% · connected to power',True,100,False),('charge-thermal','Charging paused','Wait for the device to cool',False,68,True),('charge-unsupported','Charging status unavailable','No charging values were reported',False,None,False)]:scene(key,title,sub,'charge_chamber',on,p,warn)
 for key,title,sub,on,p in [('recovery-menu','Recovery','Select an action with your device controls',False,None),('recovery-update','Installing update','Keep the device connected to power',True,45),('recovery-error','Update not installed','Signature or package checks did not pass',False,None),('loading-active','Loading','Preparing your content',True,None),('loading-error','Could not load','Try again when the source is available',False,None)]:scene(key,title,sub,'loading_aperture',on,p)
 (out/'components.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'wallpapers.json').write_text(json.dumps(wallpapers,indent=2)+'\n');(out/'scenes.json').write_text(json.dumps(scenes,indent=2)+'\n')
 provenance={'date':'2026-10-22','originalGeometry':True,'newRasterGeneration':False,'baselineCommit':'d4883a99cdeecfd0284b1e3051139c3dcc85feec','inputs':[{'file':f,'sha256':hashlib.sha256((out/'source'/f).read_bytes()).hexdigest(),'unchanged':True} for f in ['steel-material.png','steel-material-original.png','power_core-cold.png']]};(out/'source/provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 for group,items,folder in [('wallpapers',wallpapers,'previews'),('atmosphere',scenes,'scenes')]:
  per=6
  for offset in range(0,len(items),per):
   part=items[offset:offset+per];bw,bh=1440,1180;board=Image.new('RGB',(bw,bh),'#080c11');d=ImageDraw.Draw(board);d.text((28,20),'REFERENCE FORGE 14 / '+group.upper(),font=font(31,True),fill='#eee7d9');d.text((28,72),'Cold production material / separate masks / editable scene labels',font=font(20),fill='#b5bdc6')
   for i,row in enumerate(part):
    file=row['id']+('.on.preview.png' if group=='wallpapers' else '.png');im=Image.open(out/folder/file).convert('RGBA');im.thumbnail((430,430),Image.Resampling.LANCZOS);x=25+i%3*475;y=130+i//3*520;board.paste(im,(x+(430-im.width)//2,y),im);d.text((x,y+450),row['id'],font=font(18,True),fill='#eee7d9')
   board.save(out/'previews'/f'{group}-sheet-{offset//per+1:02}.png')
 cards=''.join('<article><h2>'+html.escape(s['title'])+'</h2><img src="scenes/'+s['id']+'.png" alt="'+html.escape(s['title'])+'"><p>'+s['id']+'</p><a href="scenes/'+s['id']+'.svg">Editable SVG</a></article>' for s in scenes)
 cards+=''.join('<article><h2>'+s['id']+'</h2><img src="previews/'+s['id']+'.on.preview.png" alt="Wallpaper lighting preview"><p>Lighting preview</p><a href="masters/'+s['id']+'.svg">Layered SVG</a> · <a href="exports/'+s['id']+'.cold.'+str(s['size'][0])+'.png">Production cold PNG</a></article>' for s in wallpapers)
 (out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Reference Forge 14</title><style>body{background:#080c11;color:#eee7d9;font:18px system-ui;padding:25px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}img{width:100%;height:440px;object-fit:contain}article{border:1px solid #4a3b2d;padding:16px}a{color:#cadce7}</style><h1>Reference Forge 14</h1><p>Boot, recovery, loading and charging artwork. Sample states only. Lit scenes are previews; production cold bases and masks stay separate.</p><main>'+cards+'</main></html>',encoding='utf8')
 print(json.dumps({'components':len(rows),'wallpapers':len(wallpapers),'scenes':len(scenes),'out':str(out)}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--resume-draft',action='store_true');a=p.parse_args();build(a.out.resolve(),a.resume_draft)
