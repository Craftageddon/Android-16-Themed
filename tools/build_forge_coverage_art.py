"""Reference Forge 17: retained utility and app-identity completion."""
from pathlib import Path
import argparse,base64,copy,io,json,shutil,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
from build_pilot import add,path,el,font,resvg_py,SVG
from forge_library import setup,steel,lights,layer,xml,embed,compose_layers,lighting_descriptor,ForgedPilot
from forge_completion_geometry import GEOMETRY,APP_GEOMETRY,geometry
from build_symbols import geometry as system_geometry
LAYERS=['cold','reflection','spill','seam','core','focus','symbol'];ROOT=Path(__file__).resolve().parents[1]
APP_NAMES={**{k:k.replace('_',' ').title() for k in APP_GEOMETRY},'emberchat':'EmberChat','pattern_forge':'Pattern Forge','files':'Files','gallery':'Gallery','settings':'Settings'}
def symbol(name,optical):
 compact=optical=='compact';r,g=setup(24 if compact else 96,24 if compact else 96,name+' / '+optical,view='0 0 24 24' if compact else '-3 -3 30 30')
 for i,(d,fill) in enumerate(geometry(name)):
  if compact:
   path(g['cold'],d,'#c0c7c9' if fill else 'none',stroke='#c0c7c9',width=1.7 if fill else 1.85)
   if i==0:path(g['seam'],d,stroke='white',width=.35,stroke_dasharray='1.5 120')
  else:steel(g['cold'],d,2.65,fill);lights(g,d,.31)
 if not compact:
  path(g['focus'],'M-2 2 V-2 H2 M22 -2 H26 V2 M-2 22 V26 H2 M22 26 H26 V22',stroke='white',width='.35');path(g['symbol'],'M24 23 l.7 .7 l-.7 .7 l-.7 -.7 Z','white')
 return r
def app_shapes(name):
 if name in APP_GEOMETRY:return geometry(name)
 return system_geometry({'files':'document','gallery':'photo','settings':'settings'}[name]) if name!='gallery' else geometry('photo')
def app(name):
 o=ForgedPilot((name,APP_NAMES[name],128,128,''));o.circle(64,64,54)
 groups={key:add(o.layers[key],'g',transform='translate(37.6 37.6) scale(2.2)') for key in LAYERS}
 for d,fill in app_shapes(name):
  steel(groups['cold'],d,1.7,fill);lights(groups,d,.23)
 return o.finish()
def render(root,width,texture):
 return Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(embed(root,texture)),width=width,skip_system_fonts=True))).convert('RGBA')
def native_vector(shapes,adaptive=False):
 ns='http://schemas.android.com/apk/res/android';ET.register_namespace('android',ns)
 def attrs(**x):return {'{'+ns+'}'+k:str(v) for k,v in x.items()}
 r=ET.Element('vector',attrs(width='108dp' if adaptive else '24dp',height='108dp' if adaptive else '24dp',viewportWidth=108 if adaptive else 24,viewportHeight=108 if adaptive else 24));g=ET.SubElement(r,'group',attrs(scaleX=2,scaleY=2,translateX=30,translateY=30)) if adaptive else r
 for d,fill in shapes:ET.SubElement(g,'path',attrs(pathData=d,fillColor='#FFFFFFFF' if fill else '#00000000',strokeColor='#FFFFFFFF' if adaptive else '#FFC0C7C9',strokeWidth=1.7 if adaptive else 1.85,strokeLineCap='round',strokeLineJoin='round'))
 return ET.tostring(r,encoding='unicode')
def build(root):
 assert not (root/'complete-assets.zip').exists()
 for folder in ['masters','source','exports','previews','android/res/drawable','android/res/drawable-mdpi','android/res/mipmap-anydpi-v33','android/res/values','verification/evidence']:(root/folder).mkdir(parents=True,exist_ok=True)
 shutil.copy2(ROOT/'iterations/13-forge-android-and-thor-flows/source/steel-material.png',root/'source/steel-material.png');shutil.copy2(ROOT/'iterations/12-forge-controls-and-screens/runtime-style.json',root/'runtime-style.json')
 texture=base64.b64encode((root/'source/steel-material.png').read_bytes()).decode();states=json.loads((root/'runtime-style.json').read_text(encoding='utf8'))['sampleStates'];rows=[]
 entries=[(key+'__'+optical,symbol(key,optical),24 if optical=='compact' else 96,'utility-symbol',key,optical) for key in GEOMETRY for optical in ['compact','detailed']]+[('app-'+name,app(name),128,'app-identity',name,'app') for name in APP_NAMES]
 for key,doc,size,kind,name,optical in entries:
  (root/'masters'/f'{key}.svg').write_text(xml(doc),encoding='utf8');cached={}
  for layer_name in LAYERS:
   for scale in [1,2]:
    im=render(layer(doc,layer_name),size*scale,texture);im.save(root/'exports'/f'{key}.{layer_name}@{scale}x.png')
    if scale==2:cached[layer_name]=im
  locked=name in ['visibility_off','flashlight_off']
  for state,descriptor in states.items():compose_layers(cached,lighting_descriptor(descriptor,locked)).save(root/'exports'/f'{key}.{state}.preview.png')
  rows.append({'id':key,'semanticId':name,'type':kind,'optical':optical,'size':[size,size],'layers':LAYERS,'exportScales':[1,2],'emissionLockedOff':locked,'labelsBaked':False,'nativeIntegrated':False,'deviceVerified':False})
  if kind=='app-identity':
   foreground=copy.deepcopy(doc);foreground.set('viewBox','-51.2 -51.2 230.4 230.4');foreground.set('width','108');foreground.set('height','108');render(foreground,108,texture).save(root/'android/res/drawable-mdpi'/f'cg_app_{name}_foreground.png')
   (root/'android/res/drawable'/f'cg_app_{name}_monochrome.xml').write_text(native_vector(app_shapes(name),True))
   (root/'android/res/mipmap-anydpi-v33'/f'cg_app_{name}.xml').write_text('<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android"><background android:drawable="@color/cg_forge_background"/><foreground android:drawable="@drawable/cg_app_'+name+'_foreground"/><monochrome android:drawable="@drawable/cg_app_'+name+'_monochrome"/></adaptive-icon>\n')
  elif optical=='compact':(root/'android/res/drawable'/f'cg_es_{name}.xml').write_text(native_vector(geometry(name)))
  print(key,flush=True)
 (root/'android/res/values/colors.xml').write_text('<resources><color name="cg_forge_background">#0B1015</color></resources>\n')
 strings=ET.Element('resources')
 for name,title in APP_NAMES.items():ET.SubElement(strings,'string',name='cg_app_'+name+'_name').text=title
 for name in GEOMETRY:ET.SubElement(strings,'string',name='cg_symbol_'+name+'_name').text=name.replace('_',' ').capitalize().replace('Pin dot','PIN dot').replace('Sim download','SIM download')
 (root/'android/res/values/strings.xml').write_bytes(ET.tostring(strings,encoding='utf-8',xml_declaration=True))
 (root/'components.json').write_text(json.dumps(rows,indent=2)+'\n')
 (root/'source/semantic-symbols.json').write_text(json.dumps({k:geometry(k) for k in GEOMETRY},indent=2)+'\n')
 for start in range(0,len(GEOMETRY),16):
  board=Image.new('RGB',(1800,1180),'#080c11');draw=ImageDraw.Draw(board);draw.text((28,18),'Reference Forge / retained utility symbols',font=font(30,True),fill='#eee7d9')
  for i,name in enumerate(list(GEOMETRY)[start:start+16]):
   x=i%4*450;y=90+i//4*270;draw.text((x+20,y),name.replace('_',' ').title(),font=font(21),fill='#eee7d9')
   for col,state in enumerate(['off','on']):
    im=Image.open(root/'exports'/f'{name}__detailed.{state}.preview.png');im.thumbnail((145,145));board.paste(im,(x+35+col*200,y+40),im)
    small=Image.open(root/'exports'/f'{name}__compact.{state}.preview.png');small.thumbnail((24,24));board.paste(small,(x+92+col*200,y+205),small)
  board.save(root/'previews'/f'utility-symbols-{start//16+1:02}.png')
 board=Image.new('RGB',(1800,1020),'#080c11');draw=ImageDraw.Draw(board);draw.text((28,18),'Reference Forge / authored app identities - cold and selected',font=font(29,True),fill='#eee7d9')
 for i,(name,title) in enumerate(APP_NAMES.items()):
  x=i%5*360;y=95+i//5*450;draw.text((x+24,y),title,font=font(24,True),fill='#eee7d9')
  for col,state in enumerate(['off','on']):
   im=Image.open(root/'exports'/f'app-{name}.{state}.preview.png');im.thumbnail((160,160));board.paste(im,(x+15+col*175,y+65),im)
  draw.text((x+24,y+255),'Cold / off       Selected / on',font=font(17),fill='#b5bdc6')
 board.save(root/'previews/app-identities-cold-selected.png')
 print(json.dumps({'newSemanticSymbols':len(GEOMETRY),'opticalSymbolMasters':len(GEOMETRY)*2,'authoredAppIdentities':len(APP_NAMES),'totalMasters':len(rows),'layerExports':len(rows)*14}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();build(a.root.resolve())
