"""Iteration 12: all retained control/pilot variants, scalable frames and eight Thor compositions."""
from pathlib import Path
import argparse,base64,copy,hashlib,io,json,shutil,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import SPECS as PILOT,SVG,el,add,path,render,font
from build_components import SPECS as CONTROLS
from build_reference_forge import LAYERS,COLORS
from build_forge_symbols import write_asset
from build_scalable_frames import ninepatch,DENSITIES,stretch
from forge_library import ForgedPilot,ForgedComponent,layer,state,unique,xml,compose_layers,raster,lighting_descriptor
import build_screens as screen_builder

ROOT=Path(__file__).resolve().parents[1]

def stretch_svg(source,w,h,filename):
 # Preserve outer caps. Sample one-pixel cross-sections into constant center bands.
 sw,sh=source.size;r=el('svg',width=w,height=h,viewBox=f'0 0 {w} {h}');defs=add(r,'defs')
 add(defs,'image',id='raw',href='../source/'+filename,width=sw,height=sh,image_rendering='optimizeSpeed')
 sx=[(0,sw/2-6,0,w/2-2),(sw//2,1,w/2-2,4),(sw/2+6,sw/2-6,w/2+2,w/2-2)]
 sy=[(0,sh/2-6,0,h/2-2),(sh//2,1,h/2-2,4),(sh/2+6,sh/2-6,h/2+2,h/2-2)]
 for x,ww,xx,ow in sx:
  for y,hh,yy,oh in sy:
   q=add(r,'svg',x=xx,y=yy,width=ow,height=oh,viewBox=f'{x} {y} {ww} {hh}',preserveAspectRatio='none',overflow='hidden');add(q,'use',href='#raw')
 return r

def build(a):
 source=a.symbols.resolve();out=a.out.resolve();assert not out.exists()
 for sub in ['source','masters','exports','previews','screens','verification/evidence']:(out/sub).mkdir(parents=True)
 for den,_ in DENSITIES:(out/'android/res'/f'drawable-{den}').mkdir(parents=True)
 for f in (source/'source').glob('*.png'):shutil.copy2(f,out/'source'/f.name)
 shutil.copy2(source/'runtime-style.json',out/'runtime-style.json');shutil.copy2(source/'source/GENERATION.json',out/'source/GENERATION.json')
 style=json.loads((out/'runtime-style.json').read_text());style['contentColors']={'well':'#10151b','text':'#eee7d9','secondary':'#b5bdc6','semantic':'#bdc4c8'};(out/'runtime-style.json').write_text(json.dumps(style,indent=2)+'\n')
 shutil.copy2(ROOT/'tools/state_driver_v2.cjs',out/'source/state_driver_v2.cjs')
 states=json.loads((out/'runtime-style.json').read_text())['sampleStates'];texture=base64.b64encode((out/'source/steel-material.png').read_bytes()).decode();rows=[];assets={}
 for prefix,specs,cls in [('control',CONTROLS,ForgedComponent),('pilot',PILOT,ForgedPilot)]:
  for index,spec in enumerate(specs):
   asset=cls(spec).build();r=asset.finish();key=prefix+'-'+asset.key;assets[key]=(asset,r)
   rows.append(write_asset(out,key,r,states,[round(asset.w),round(asset.w*2)],texture,metadata={'type':prefix,'canonicalId':asset.key,'size':[asset.w,asset.h],'geometryState':'Explicit switch/check/progress variant; renderer chooses geometry before lighting','labelsBaked':False,'fixedAspect':True}))
   if (index+1)%16==0:print(prefix,index+1,flush=True)
 # Complete paired catalog, every retained component/pilot including controller and keyboard caps.
 items=list(assets.items())
 for start in range(0,len(items),12):
  board=Image.new('RGB',(2000,1740),'#090d12');d=ImageDraw.Draw(board)
  d.text((45,25),f'REFERENCE FORGE / CONTROLS / {start//12+1:02}',font=font(34,True),fill='#eee7d9')
  d.text((47,80),'Each specimen: cold base above / selected lighting below / labels are live SVG text',font=font(22),fill='#b5bdc6')
  for i,(key,(asset,r)) in enumerate(items[start:start+12]):
   x=30+i%4*495;y=145+i//4*505;d.text((x+10,y),asset.label,font=font(20,True),fill='#d8dfe2')
   for st,yy in [('off',y+45),('on',y+262)]:
    desc=lighting_descriptor(states[st],asset.key.endswith('_off') or asset.key=='check_empty')
    q=state(r,desc,asset.preview_text);im=raster(q,round(asset.w*2),texture);im.thumbnail((455,195),Image.Resampling.LANCZOS);board.paste(im,(x+(475-im.width)//2,yy+(195-im.height)//2),im)
  board.save(out/'previews'/f'controls-catalog-{start//12+1:02}.png')
 # Four newly textured scalable resource families. Raw layer sources contain no baked labels.
 frame_rows=[]
 for name,w,h in [('button',192,112),('field',224,112),('panel',224,176),('notification',288,128)]:
  obj=ForgedPilot((name,name,w,h,''));obj.frame(6,6,w-12,h-12);r=obj.finish();(out/'masters'/f'scalable-{name}.svg').write_text(xml(r),encoding='utf8')
  raw_hashes={}
  for key in LAYERS:
   raw=raster(layer(r,key),w*3,texture);rawname=f'scalable-{name}-{key}-raw.png';raw.save(out/'source'/rawname);raw_hashes[key]=hashlib.sha256((out/'source'/rawname).read_bytes()).hexdigest()
   q=stretch_svg(raw,w,h,rawname);data=base64.b64encode((out/'source'/rawname).read_bytes()).decode()
   for image in q.findall('.//{'+SVG+'}image'):image.set('href','data:image/png;base64,'+data)
   for den,scale in DENSITIES:
    im=Image.open(io.BytesIO(render(xml(q),round(w*scale)))).convert('RGBA')
    st=[round((w/2-2)*scale),round((w/2+2)*scale),round((h/2-2)*scale),round((h/2+2)*scale)]
    pad=[round(22*scale),round(22*scale),round(22*scale),round(22*scale)]
    ninepatch(im,st,pad).save(out/'android/res'/f'drawable-{den}'/f'cg_rf_{name}_{key}.9.png')
  frame_rows.append({'id':name,'size':[w,h],'layers':LAYERS,'sourceHashes':raw_hashes,'fixedCaps':True,'constantCenterBand':True,'configurations':28,'nativeIntegrated':False})
 board=Image.new('RGB',(2000,1930),'#090d12');d=ImageDraw.Draw(board);d.text((45,28),'REFERENCE FORGE / FOUR SCALABLE FRAMES',font=font(38,True),fill='#eee7d9')
 for col,st in enumerate(['off','on','active_pressed']):d.text((45+col*660,95),st.upper().replace('_',' '),font=font(24,True),fill='#b5bdc6')
 for row,spec in enumerate(frame_rows):
  name=spec['id'];w,h=spec['size'];y=175+row*420
  layers={k:stretch(Image.open(out/'android/res/drawable-xhdpi'/f'cg_rf_{name}_{k}.9.png').convert('RGBA'),(600,h*2)) for k in LAYERS}
  for col,st in enumerate(['off','on','active_pressed']):
   im=compose_layers(layers,states[st]);board.paste(im,(45+col*660,y),im)
   d.text((65+col*660,y+im.height+15),name.upper(),font=font(20),fill='#b5bdc6')
 d.text((45,1865),'Textured cold bases / fixed caps / independent neutral light masks / actual nine-patch renders',font=font(22),fill='#b5bdc6');board.save(out/'previews/scalable-frame-states.png')
 # Retain the six prior logical layouts, with every embedded asset supplied by the new factory.
 counter=[0]
 def place(root,q,x,y,w,h):
  counter[0]+=1;n=unique(q,f'f{counter[0]}-');n.set('x',str(x));n.set('y',str(y));n.set('width',str(w));n.set('height',str(h));root.append(n)
 def descriptor(st):return states['selected_focused' if st=='focused' else 'on' if st in ['selected','pressed'] else 'off']
 def frame(root,x,y,w,h,state='idle'):
  ob=ForgedPilot(('frame','Frame',w,h,''));ob.frame(5,5,w-10,h-10);q=ob.finish();place(root,__import__('forge_library').state(q,descriptor(state)),x,y,w,h)
 def asset(root,key,x,y,w=None,h=None,state='idle',labels=False):
  obj,r=assets['pilot-'+key];q=__import__('forge_library').state(r,descriptor(state),obj.preview_text if labels else None);place(root,q,x,y,w or obj.w,h or obj.h)
 def hero(root,_out,kind,x,y,w,h,state='idle'):
  if kind=='primary':
   obj,r=assets['pilot-primary_button'];q=__import__('forge_library').state(r,descriptor(state),obj.preview_text)
  else:q=__import__('forge_library').state(ET.parse(source/'masters/hero-power_core.svg').getroot(),descriptor(state))
  place(root,q,x,y,w,h)
 screen_builder.frame=frame;screen_builder.asset=asset;screen_builder.hero=hero
 # Keep original screen layout commands; source image inlining resolves all new relative references.
 screen_builder.build(out)
 # Keep the live charge value below the bright core so it remains legible.
 charging=out/'screens/lock-and-charging.svg';doc=ET.parse(charging).getroot()
 for n in doc.findall('.//{'+SVG+'}text'):
  if n.text=='72%':n.set('y','682')
  elif n.text=='Charging':n.set('y','716')
  elif n.text=='Press power to wake':n.set('y','780')
  elif n.text=='Tuesday, 20 October':n.text='Wednesday, 21 October'
 charging.write_text(xml(doc),encoding='utf8');(out/'screens/lock-and-charging.png').write_bytes(render(screen_builder.inline_images(doc,out/'screens')))
 # Two additional existing material-expansion layouts, now made from matching new sources.
 def text(r,x,y,s,size=24,col='#eee7d9'):add(r,'text',x=x,y=y,fill=col,font_family='sans-serif',font_size=size).text=s
 r=screen_builder.screen(1280,720,'Upper quick settings / Reference Forge');text(r,40,52,'Quick settings',32)
 for i,(label,motif) in enumerate([('Wi-Fi','wifi'),('Bluetooth','bluetooth'),('Airplane','airplane'),('Privacy','shield')]):
  x=35+i*311;frame(r,x,90,285,270,'selected' if i<2 else 'idle');q=ET.parse(source/'masters'/f'hero-{motif}.svg').getroot();q=state(q,states['on' if i<2 else 'off']);place(r,q,x+75,110,135,150);text(r,x+28,315,label,24)
 asset(r,'notification',35,400,1210,240,labels=True);upper=r
 r=screen_builder.screen(800,600,'Lower game companion / Reference Forge');text(r,30,54,'Game companion',30)
 for i,(label,name) in enumerate([('Input','controller'),('Display','screen_swap'),('Cooling','fan')]):
  x=25+i*255;frame(r,x,100,240,260,'focused' if i==0 else 'idle');q=ET.parse(source/'masters'/f'{name}__detailed.svg').getroot();place(r,state(q,states['on' if i==0 else 'off']),x+64,140,112,112);text(r,x+35,315,label,24)
 text(r,30,420,'A  Select     B  Back     LB / RB  Change section',21);text(r,30,470,'Capture controls before navigating this panel.',20,'#b5bdc6');text(r,30,510,'Return input to the game when finished.',20,'#b5bdc6')
 for key,doc in [('upper-quick-settings',upper),('lower-game-companion',r)]:
  (out/'screens'/f'{key}.svg').write_text(xml(doc),encoding='utf8');(out/'screens'/f'{key}.png').write_bytes(render(screen_builder.inline_images(doc,out/'screens')))
 # Ensure gallery shows all eight screens, including calibration.
 names=['thor-upper-launcher','thor-upper-shade','thor-lower-dashboard','thor-lower-calibration','thor-lower-profile','lock-and-charging','upper-quick-settings','lower-game-companion']
 board=Image.new('RGB',(2200,2100),'#090d12');d=ImageDraw.Draw(board);d.text((45,25),'REFERENCE FORGE / ALL EIGHT SCREEN COMPOSITIONS',font=font(38,True),fill='#eee7d9')
 for i,name in enumerate(names):
  x=35+i%4*545;y=125+i//4*960;d.text((x,y),name.replace('thor-','').replace('-',' '),font=font(19,True),fill='#d8dfe2');im=Image.open(out/'screens'/f'{name}.png').convert('RGBA');im.thumbnail((510,860),Image.Resampling.LANCZOS);board.paste(im,(x+(510-im.width)//2,y+45),im)
 d.text((45,2040),'Logical design layouts. Live SVG text. Display metrics and device behavior remain unverified.',font=font(24),fill='#b5bdc6');board.save(out/'previews/all-eight-screens.png')
 (out/'components.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'scalable-frames.json').write_text(json.dumps(frame_rows,indent=2)+'\n')
 (out/'screens/layout-metadata.json').write_text(json.dumps({'screenCount':8,'names':names,'coordinateSystem':'logical design units; not verified hardware pixels or dp','nativeIntegrated':False,'targetGeometryVerified':False,'sampleContent':True},indent=2)+'\n')
 (out/'source/input-snapshot.json').write_text(json.dumps({'iteration11Source':str(source.name),'sourceHashes':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (source/'source').glob('*.png')},'componentCount':len(CONTROLS),'pilotCount':len(PILOT)},indent=2)+'\n')
 print(json.dumps({'controlVariants':len(CONTROLS),'pilotSpecimens':len(PILOT),'scalableFamilies':4,'ninePatches':112,'screenLayouts':8}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--symbols',type=Path,required=True);build(p.parse_args())
