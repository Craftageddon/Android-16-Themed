"""Forge the actual magnification glyphs and native stateful control resources.

Cold material and seven neutral masks remain editable; native XML tints masks
from real view states. No glowing raster or visible label is a production input.
"""
from pathlib import Path
import base64, copy, hashlib, io, json, re, shutil
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from audit_os_resource_coverage import ROOT, write_json, read_json
from build_pilot import add, path, font, resvg_py
from forge_library import setup, xml, embed, layer, ForgedPilot, compose_layers
from build_scalable_frames import ninepatch, stretch

OUT = ROOT/'iterations/23-magnification'
NATIVE = OUT/'native-patch/frameworks/base/packages/SystemUI'
UP = OUT/'upstream/frameworks/base/packages/SystemUI/res/drawable'
A = '{http://schemas.android.com/apk/res/android}'
SVG = '{http://www.w3.org/2000/svg}'
LAYERS = ['cold','reflection','spill','seam','core','focus','symbol']
DENSITIES = [('mdpi',1),('hdpi',1.5),('xhdpi',2),('xxhdpi',3)]
GLYPHS = {
    'size_small': ('ic_magnification_menu_small','Small window preset'),
    'size_medium': ('ic_magnification_menu_medium','Medium window preset'),
    'size_large': ('ic_magnification_menu_large','Large window preset'),
    'fullscreen': ('ic_open_in_full','Switch to fullscreen magnification'),
    'move': ('ic_move_magnification','Move magnifier / open settings'),
    'close': ('ic_magnification_menu_close','Finish editing window size'),
    'resize_a': ('ic_arrow_top_left_and_bottom_right','Native diagonal resize arrow A'),
    'resize_b': ('ic_arrow_top_right_and_bottom_left','Native diagonal resize arrow B'),
    'corner_top_left': ('ic_magnification_corner_top_left','Retained corner guide top left'),
    'corner_top_right': ('ic_magnification_corner_top_right','Retained corner guide top right'),
    'corner_bottom_left': ('ic_magnification_corner_bottom_left','Retained corner guide bottom left'),
    'corner_bottom_right': ('ic_magnification_corner_bottom_right','Retained corner guide bottom right'),
    'controller': ('ic_control_magnification_grey','Retained four-direction magnifier controller'),
    'settings_gear': ('ic_open_in_new_window','Actual settings gear inside the misleadingly named native resource'),
    'zoom_in': ('ic_add','Native zoom-in button'),
    'zoom_out': ('ic_remove','Native zoom-out button'),
}


def native_geometry(root):
    keys = {'pathData','viewportWidth','viewportHeight','fillType','rotation','pivotX','pivotY',
            'scaleX','scaleY','translateX','translateY','strokeWidth','strokeLineCap','strokeLineJoin'}
    return [{'tag': n.tag, 'attributes': {k:v for k,v in n.attrib.items() if k.split('}')[-1] in keys}} for n in root.iter()]


def glyph(native, label):
    source = ET.parse(UP/(native+'.xml')).getroot()
    vector = source if source.tag == 'vector' else source.find('.//vector')
    assert vector is not None
    vw = float(vector.get(A+'viewportWidth')); vh = float(vector.get(A+'viewportHeight'))
    width = float(vector.get(A+'width').replace('dp','')); height = float(vector.get(A+'height').replace('dp',''))
    if native=='ic_control_magnification_grey':width=height=144
    # The12dp diagonal arrows need room for neutral spill inside their26dp
    # native holder. Add transparent optical padding while retaining their
    # exact physical path scale and centered placement.
    optical_pad = 2 if width == vw == 12 and height == vh == 12 else 0
    width += optical_pad*2; height += optical_pad*2
    root, groups = setup(width,height,label,view=f'{-optical_pad:g} {-optical_pad:g} {vw+2*optical_pad:g} {vh+2*optical_pad:g}'); defs = root.find(SVG+'defs'); count = 0
    source_notice=(UP/(native+'.xml')).read_text(encoding='utf8').split('-->')[0]
    add(root,'metadata',id='upstream-attribution').text='Pinned Android source geometry, Apache-2.0. Original source retained at '+str((UP/(native+'.xml')).relative_to(OUT))+'. '+source_notice
    steel = add(defs,'linearGradient',id='glyph-steel',x1='0',y1='0',x2='0',y2='1')
    for offset,color in [(0,'#ced7de'),(.24,'#8fa4b5'),(.48,'#6c8293'),(.68,'#849aad'),(1,'#bfcdd8')]:add(steel,'stop',offset=offset,stop_color=color)
    for effect,sigma in [('light-spill',max(.16,min(.55,min(vw,vh)/50))),('light-reflection',.20)]:
        filt=defs.find(SVG+"filter[@id='"+effect+"']")
        filt.find(SVG+'feGaussianBlur').set('stdDeviation',str(sigma))
    def walk(nodes, parents):
        nonlocal count
        for node in nodes:
            if node.tag == 'group':
                val = lambda k, d: float(node.get(A+k,str(d)))
                px,py = val('pivotX',0),val('pivotY',0)
                transform = f"translate({val('translateX',0)+px} {val('translateY',0)+py}) rotate({val('rotation',0)}) scale({val('scaleX',1)} {val('scaleY',1)}) translate({-px} {-py})"
                children = {k:add(g,'g',transform=transform) for k,g in parents.items()}; walk(node,children)
            elif node.tag == 'path':
                count += 1; d=node.get(A+'pathData'); assert d and '@' not in d
                fill = node.get(A+'fillColor'); stroke = node.get(A+'strokeColor')
                visible = lambda color: color is not None and color not in {'#00000000','@android:color/transparent','@null'}
                filled, stroked = visible(fill),visible(stroke)
                sw = float(node.get(A+'strokeWidth','0')); rule='evenodd' if node.get(A+'fillType')=='evenOdd' else 'nonzero'
                assert filled or (stroked and sw>0), native
                attrs = {'fill-rule':rule,'stroke-linecap':node.get(A+'strokeLineCap','butt'),
                         'stroke-linejoin':node.get(A+'strokeLineJoin','miter')}
                if filled:
                    path(parents['cold'],d,'url(#glyph-steel)',**attrs)
                    path(parents['cold'],d,'url(#forged)',opacity=.14,**attrs)
                    clip_id='geometry-'+str(count); clip=add(defs,'clipPath',id=clip_id)
                    path(clip,d,'white',fill_rule=rule,clip_rule=rule)
                    # Edge/bevel and all emission seams stay inside the exact
                    # source silhouette. Preserve holes and group transforms.
                    for color, offset, weight in [('#05090e',0,.95),('#cbd4d9',-.18,.62),('#0b1118',.22,.45)]:
                        path(parents['cold'],d,stroke=color,width=weight,transform=f'translate({offset} {offset})',clip_path='url(#'+clip_id+')',**attrs)
                    weight=max(.30,min(.72,min(vw,vh)/48*.72))
                else:
                    path(parents['cold'],d,stroke='#1a2028',width=sw,**attrs)
                    path(parents['cold'],d,stroke='#b8c0c4',width=sw*.58,**attrs); weight=sw*.60
                    clip_id=None
                for name, gain, weight_factor, blur in [('reflection',.5,2.5,'light-reflection'),('spill',1,2.4,'light-spill'),('seam',1,1,None),('core',1,.24,None)]:
                    extra={**attrs,'opacity':gain}
                    if blur: extra['filter']='url(#'+blur+')'
                    if filled and name in {'seam','core'}: extra['clip-path']='url(#'+clip_id+')'
                    path(parents[name],d,stroke='white',width=max(.16,weight*weight_factor) if name=='core' else weight*weight_factor,**extra)
            else:
                raise AssertionError('Dedicated geometry review required: '+node.tag)
    walk(vector,groups)
    if native == 'ic_control_magnification_grey':
        path(groups['focus'],'M1 5V1H5 M19 1H23V5 M1 19V23H5 M19 23H23V19',stroke='white',width=.45)
    geom=native_geometry(vector)
    return root,width,height,{'nativeSourceResource':native,'sourceVectorGeometry':geom,
                              'sourceVectorGeometrySha256':hashlib.sha256(json.dumps(geom,sort_keys=True).encode()).hexdigest(),
                              'sourcePath':(UP/(native+'.xml')).relative_to(OUT).as_posix(),
                              'sourceSha256':hashlib.sha256((UP/(native+'.xml')).read_bytes()).hexdigest(),
                              'sourceGroupsAndPathsRetained':True,'sourcePaletteReplacedByColdMaterial':True,
                              'transparentOpticalPaddingNativeUnits':optical_pad,
                              'sourceStrokeWidthsRetained':True,'ownerFocusCue':'Container except retained96dp controller',
                              'sourceAutoMirrored':vector.get(A+'autoMirrored','false')}


def control(key,w,h):
    o=ForgedPilot((key,'Magnification '+key,w,h,''))
    if key in {'switch_thumb','seek_thumb','drag_handle'}:
        o.circle(w/2,h/2,min(w,h)/2-2.0)
    elif key=='switch_track':
        o.frame(1,3,w-2,h-6,False)
    elif key=='zoom_rail':
        o.frame(1,2,w-2,h-4,False)
    else: o.frame(1,1,w-2,h-2,key not in {'corner_handle'})
    return o.finish()


def native_xml(pathname, root):
    p=NATIVE/'res'/pathname;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n')


def layer_list(key,disabled=False):
    root=ET.Element('layer-list')
    for name in ['cold'] if disabled else LAYERS:
        item=ET.SubElement(root,'item')
        tag='nine-patch' if key in {'control','switch_track','zoom_rail','panel'} else 'bitmap'
        attrs={A+'src':'@drawable/cg_mag_'+key+'_'+name,A+'dither':'true'}
        if tag=='bitmap':attrs[A+'gravity']='fill'
        if name!='cold':attrs.update({A+'tint':'@color/cg_mag_'+name+'_state',A+'tintMode':'src_in'})
        if disabled:attrs[A+'alpha']='0.42'
        ET.SubElement(item,tag,attrs)
    return root


def build():
    assert not (OUT/'complete-assets.zip').exists()
    for name in ['source','masters','layers','exports','previews','verification/evidence']:(OUT/name).mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'iterations/21-native-workflows/source/steel-material.png',OUT/'source/steel-material.png')
    shutil.copy2(ROOT/'iterations/21-native-workflows/runtime-style.json',OUT/'runtime-style.json')
    texture=base64.b64encode((OUT/'source/steel-material.png').read_bytes()).decode();style=read_json(OUT/'runtime-style.json')
    entries=[]
    for key,(native,label) in GLYPHS.items():
        doc,w,h,meta=glyph(native,label);entries.append((key,doc,w,h,False,meta))
    for key,w,h in [('control',48,48),('corner_handle',26,26),('drag_handle',36,36),
                    ('switch_thumb',32,32),('switch_track',52,32),('seek_thumb',28,28),('zoom_rail',48,12)]:
        entries.append((key,control(key,w,h),w,h,key in {'control','switch_track','zoom_rail'},
                        {'purpose':'Native magnification '+key,'newGeometry':True}))
    records=[];cached={}
    for key,doc,w,h,is_nine,meta in entries:
        p=OUT/'masters'/(key+'.svg');p.write_text(xml(doc),encoding='utf8'); layers={}; configs=[]
        st=[round(w/2-1),round(w/2+1),round(h/2-1),round(h/2+1)]
        padding=([9,9,9,9] if key=='control' else [0,0,0,0] if key=='switch_track' else [3,2,3,2])
        for name in LAYERS:
            source=layer(doc,name);(OUT/'layers'/(key+'.'+name+'.svg')).write_text(xml(source),encoding='utf8')
            for qualifier,scale in DENSITIES:
                im=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(embed(source,texture)),width=round(w*scale),skip_system_fonts=True))).convert('RGBA')
                assert im.height==round(h*scale)
                target=NATIVE/'res'/('drawable-'+qualifier)/('cg_mag_'+key+'_'+name+('.9.png' if is_nine else '.png'))
                target.parent.mkdir(parents=True,exist_ok=True)
                out=ninepatch(im,[round(v*scale) for v in st],[round(v*scale) for v in padding]) if is_nine else im
                out.save(target);configs.append({'layer':name,'density':qualifier,'file':target.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
                if qualifier=='mdpi':layers[name]=im
        cached[key]=layers
        for state,descriptor in style['sampleStates'].items():compose_layers(layers,descriptor).save(OUT/'exports'/(key+'.'+state+'.preview.png'))
        native_xml('drawable/cg_mag_'+key+'_layers.xml',layer_list(key))
        native_xml('drawable/cg_mag_'+key+'_disabled.xml',layer_list(key,True))
        selector=ET.Element('selector');ET.SubElement(selector,'item',{A+'state_enabled':'false',A+'drawable':'@drawable/cg_mag_'+key+'_disabled'})
        ET.SubElement(selector,'item',{A+'drawable':'@drawable/cg_mag_'+key+'_layers'});native_xml('drawable/cg_mag_'+key+'.xml',selector)
        records.append({'id':key,'size':[w,h],'ninePatch':is_nine,'stretch':st if is_nine else None,
                        'padding':padding if is_nine else None,'layers':LAYERS,'nativeResource':'cg_mag_'+key,
                        'densityConfigurations':configs,'productionTextBaked':False,'emberBakedIntoRasters':False,**meta})
    # Color is wholly separate from neutral production mask pixels. Native
    # first-match selectors consume checked/selected/activated/pressed states.
    values=ET.Element('resources')
    for name,color in style['colors'].items():ET.SubElement(values,'color',{'name':'cg_mag_'+name}).text=color
    ET.SubElement(values,'color',{'name':'cg_mag_text'}).text='#eee7d9'
    ET.SubElement(values,'color',{'name':'cg_mag_secondary'}).text='#b5bdc6'
    ET.SubElement(values,'color',{'name':'cg_mag_cold_progress'}).text='#b8c4cf'
    native_xml('values/cg_magnification_colors.xml',values)
    dimensions=ET.Element('resources')
    ET.SubElement(dimensions,'dimen',{'name':'cg_mag_min_touch_target'}).text='48dp'
    ET.SubElement(dimensions,'dimen',{'name':'cg_mag_resize_target_inset'}).text='11dp'
    native_xml('values/cg_magnification_dimensions.xml',dimensions)
    for name in LAYERS[1:]:
        selector=ET.Element('selector')
        ET.SubElement(selector,'item',{A+'state_enabled':'false',A+'color':'@android:color/transparent'})
        if name=='focus':
            ET.SubElement(selector,'item',{A+'state_focused':'true',A+'color':'@color/cg_mag_focus'})
        else:
            for flag,state in [('pressed','active_pressed'),('checked','on'),('selected','on'),('activated','on')]:
                gain=style['sampleStates'][state]['gains'][name]
                ET.SubElement(selector,'item',{A+'state_'+flag:'true',A+'color':'@color/cg_mag_'+name,A+'alpha':str(gain)})
        ET.SubElement(selector,'item',{A+'color':'@android:color/transparent'});native_xml('color/cg_mag_'+name+'_state.xml',selector)
    text_state=ET.Element('selector')
    ET.SubElement(text_state,'item',{A+'state_enabled':'false',A+'color':'@color/cg_mag_secondary',A+'alpha':'0.6'})
    ET.SubElement(text_state,'item',{A+'color':'@color/cg_mag_text'})
    native_xml('color/cg_mag_text_state.xml',text_state)
    write_json(OUT/'components.json',records)
    # Reuse the already-reviewed native panel and its editable source exactly.
    panel_source=ROOT/'iterations/21-native-workflows'
    shutil.copy2(panel_source/'masters/scalable-panel.svg',OUT/'masters/panel.svg')
    for p in (panel_source/'source').glob('scalable-panel-*-raw.png'):shutil.copy2(p,OUT/'source'/p.name)
    panel_configs=[]
    for p in (panel_source/'native-patch/hardware/ayn/packages/AynParts/res').glob('drawable-*/cg_rf_panel_*.9.png'):
        name=p.name.replace('cg_rf_panel_','cg_mag_panel_');target=NATIVE/'res'/p.parent.name/name
        shutil.copy2(p,target);panel_configs.append({'source':p.relative_to(ROOT).as_posix(),'target':target.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'unchanged':True})
    native_xml('drawable/cg_mag_panel.xml',layer_list('panel'))
    write_json(OUT/'unchanged-panel-reuse.json',{'masterSource':(panel_source/'masters/scalable-panel.svg').relative_to(ROOT).as_posix(),
                'masterTarget':'masters/panel.svg','masterSha256':hashlib.sha256((OUT/'masters/panel.svg').read_bytes()).hexdigest(),
                'nativeNinePatches':panel_configs,'sourceRole':'Exact-byte reviewed panel reuse, not a newly authored drawing.'})
    board=Image.new('RGB',(1680,1540),'#080c11');draw=ImageDraw.Draw(board)
    draw.text((24,18),'FORGE / ACTUAL MAGNIFICATION CONTROLS',font=font(30,True),fill='#eee7d9')
    draw.text((24,62),'Cold and selected. Exact native glyph roles; independent neutral masks and runtime color.',font=font(19),fill='#b5bdc6')
    for i,(key,_,_,_,_,_) in enumerate(entries):
        x=24+(i%4)*414;y=112+(i//4)*232
        draw.text((x,y),key.replace('_',' ').title(),font=font(19),fill='#eee7d9')
        for j,state in enumerate(['off','on']):
            im=Image.open(OUT/'exports'/(key+'.'+state+'.preview.png')).convert('RGBA')
            im=im.resize((round(im.width*min(3,142/im.width,142/im.height)),round(im.height*min(3,142/im.width,142/im.height))),Image.Resampling.LANCZOS)
            board.paste(im,(x+j*195+(150-im.width)//2,y+36+(142-im.height)//2),im)
        draw.text((x+15,y+191),'Cold                   Selected / active',font=font(14),fill='#b5bdc6')
    draw.text((24,1510),'Source-backed artwork sheet. Native owner/resource adaptation and target rendering are separate gates.',font=font(17),fill='#b5bdc6')
    board.save(OUT/'previews/magnification-controls-cold-and-on.png')
    print(json.dumps({'masters':len(records),'sourceGeometryTreatments':len(GLYPHS),'newControlGeometry':7,
                      'nativePngConfigurations':sum(len(r['densityConfigurations']) for r in records),'reusedPanelConfigurations':len(panel_configs),
                      'nativeXmlStateResources':len(list((NATIVE/'res').rglob('*.xml'))),'bakedGlowingRasters':0}))


if __name__=='__main__':build()
