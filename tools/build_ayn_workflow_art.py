"""Geometry for actual AynParts owners: no baked crosshair, position dot or RGB data."""
from pathlib import Path
import base64,hashlib,io,json,math,shutil,xml.etree.ElementTree as E
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,write_json
from build_pilot import path,add,font,resvg_py
from forge_library import ForgedPilot,joint,lights,xml,embed,layer,compose_layers,lighting_descriptor
from forge_completion_geometry import circle
from build_scalable_frames import bounds,ninepatch

OUT=ROOT/'iterations/21-native-workflows';PACKAGE=OUT/'native-patch/hardware/ayn/packages/AynParts';LAYERS=['cold','reflection','spill','seam','core','focus','symbol']

def gate():
    o=ForgedPilot(('ayn_gate','AYN live stick gate',120,120,''));x=y=60;r=56;rim=6
    path(o.b,circle(x,y,r),'url(#edge)',stroke='#030609',width=1.5);path(o.b,circle(x,y,r-1.2),'url(#forged)');add(o.b,'circle',cx=x,cy=y,r=r-rim,fill='#10151b',stroke='#684831',stroke_width='.6');d='';radius=r-rim*.55
    for start,end in [(-79,-11),(11,79),(101,169),(191,259)]:
        a=(x+radius*math.cos(math.radians(start)),y+radius*math.sin(math.radians(start)));b=(x+radius*math.cos(math.radians(end)),y+radius*math.sin(math.radians(end)));d+=f'M{a[0]:.3f} {a[1]:.3f} A{radius} {radius} 0 0 1 {b[0]:.3f} {b[1]:.3f} '
    path(o.b,d,stroke='#020407',width=2.1);lights(o.layers,d,.95)
    for angle in [-90,0,90,180]:
        a=math.radians(angle);joint(o.b,x+(r-1)*math.cos(a),y+(r-1)*math.sin(a),3)
    return o.finish()

def build():
    assert not (OUT/'complete-assets.zip').exists()
    for name in ['masters','source','exports','previews','verification/evidence']:(OUT/name).mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'iterations/20-semantic-review/source/steel-material.png',OUT/'source/steel-material.png');shutil.copy2(ROOT/'iterations/20-semantic-review/runtime-style.json',OUT/'runtime-style.json');texture=base64.b64encode((OUT/'source/steel-material.png').read_bytes()).decode();style=json.loads((OUT/'runtime-style.json').read_text());dot=ForgedPilot(('ayn_dot','AYN live position',20,20,''));dot.circle(10,10,7.25);path(dot.b,circle(10,10,6.4),stroke='#C0C7C9',width=1.0);thumb=ForgedPilot(('ayn_rgb_thumb','AYN RGB channel thumb',36,36,''));thumb.circle(18,18,13.5);entries=[('ayn_gate',gate(),120,120),('ayn_dot',dot.finish(),20,20),('ayn_rgb_thumb',thumb.finish(),36,36)];rows=[]
    for key,doc,width,height in entries:
        (OUT/'masters'/f'{key}.svg').write_text(xml(doc),encoding='utf8');cached={}
        for name in LAYERS:
            for scale,qualifier in [(1,'mdpi'),(2,'xhdpi'),(3,'xxhdpi')]:
                im=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(embed(layer(doc,name),texture)),width=width*scale,skip_system_fonts=True))).convert('RGBA');im.save(OUT/'exports'/f'{key}.{name}@{scale}x.png');folder=PACKAGE/'res'/('drawable-'+qualifier);folder.mkdir(parents=True,exist_ok=True);im.save(folder/f'cg_{key}_{name}.png')
                if scale==2:cached[name]=im
        for state,descriptor in style['sampleStates'].items():compose_layers(cached,lighting_descriptor(descriptor,False)).save(OUT/'exports'/f'{key}.{state}.preview.png')
        rows.append({'id':key,'size':[width,height],'layers':LAYERS,'exportScales':[1,2,3],'productionTextBaked':False,'dynamicDataBaked':False,'nativeFamily':'cg_'+key,'purpose':{'ayn_gate':'Outer120dp stick gate; preserve actual native circle56dp and live crosshair/clamped dot geometry. No center-position illustration is baked into this frame.','ayn_dot':'Position ornament centered by the actual source clamp; visible cold radius8dp including stroke. Travel and raw/calibrated identity remain native.','ayn_rgb_thumb':'Cold36dp thumb housing. A live native flat RGB channel swatch is drawn separately; gesture glow uses neutral masks.'}[key]})
    reused=[];adapted=[]
    for family in ['button','field','panel']:
        source=ROOT/'iterations/12-forge-controls-and-screens/masters'/f'scalable-{family}.svg';reference=OUT/'source'/('reference-'+source.name);shutil.copy2(source,reference);reused.append({'source':source.relative_to(ROOT).as_posix(),'target':reference.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'unchanged':True})
        compact=E.parse(source).getroot();compact.set('width',str(float(compact.get('width'))*.5));compact.set('height',str(float(compact.get('height'))*.5));(OUT/'masters'/source.name).write_text(xml(compact),encoding='utf8')
        for p in (source.parent.parent/'source').glob(f'scalable-{family}-*-raw.png'):shutil.copy2(p,OUT/'source'/p.name)
        for p in (ROOT/'iterations/18-native-runtime/native/res').glob(f'drawable-*/cg_rf_{family}_*.9.png'):
            im=Image.open(p).convert('RGBA');(x0,x1),(y0,y1)=bounds(im);w,h=im.width-2,im.height-2;bottom=[i for i in range(im.width) if im.getpixel((i,im.height-1))==(0,0,0,255)];right=[i for i in range(im.height) if im.getpixel((im.width-1,i))==(0,0,0,255)];padding=[bottom[0]-1,right[0]-1,w-bottom[-1],h-right[-1]];content=im.crop((1,1,im.width-1,im.height-1)).resize((round(w*.5),round(h*.5)),Image.Resampling.LANCZOS);stretch=[round(x*.5) for x in [x0,x1,y0,y1]];new=ninepatch(content,stretch,[round(x*.5) for x in padding]);target=PACKAGE/'res'/p.parent.name/p.name;target.parent.mkdir(parents=True,exist_ok=True);new.save(target);adapted.append({'source':p.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'target':target.relative_to(OUT).as_posix(),'targetSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'opticalScale':.5,'sourceContentSize':[w,h],'contentSize':list(content.size),'stretch':stretch,'padding':[round(x*.5) for x in padding],'method':'Resize content only; reconstruct metadata bands separately.'})
    write_json(OUT/'components.json',rows);write_json(OUT/'unchanged-resource-reuse.json',reused);write_json(OUT/'adapted-native-frames.json',adapted)
    board=Image.new('RGB',(1450,620),'#080c11');draw=ImageDraw.Draw(board);draw.text((25,18),'FORGE / ACTUAL AYN LIVE-DATA CONTROL HOUSINGS',font=font(29,True),fill='#eee7d9');draw.text((25,65),'Cold and active input. Crosshair, moving dot position, channel color and numeric values remain native data.',font=font(18),fill='#b5bdc6')
    for i,(key,_,w,h) in enumerate(entries):
        x=30+i*475;draw.text((x,125),{'ayn_gate':'Stick gate','ayn_dot':'Live position ornament','ayn_rgb_thumb':'RGB channel housing'}[key],font=font(24),fill='#eee7d9')
        for j,state in enumerate(['off','on']):
            im=Image.open(OUT/'exports'/f'{key}.{state}.preview.png');im=im.resize((190,190),Image.Resampling.LANCZOS) if key!='ayn_gate' else im;im.thumbnail((200,200));board.paste(im,(x+j*225,195),im)
        draw.text((x,445),'Cold                      Active input',font=font(18),fill='#b5bdc6')
    board.save(OUT/'previews/ayn-live-control-housings.png');print(json.dumps({'newGeometryMasters':3,'newProductionLayers':63,'compactFrameTreatments':3,'adaptedNativeNinePatchFiles':len(adapted),'nativeResRoot':str(PACKAGE/'res')}))

if __name__=='__main__':build()
