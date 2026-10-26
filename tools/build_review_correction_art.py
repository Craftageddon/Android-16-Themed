"""Additional deliberate glyphs discovered by actual source-to-donor inspection."""
import base64,hashlib,io,json,shutil,xml.etree.ElementTree as E
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,write_json
from build_pilot import resvg_py,font
from build_semantic_gap_art import symbol,native_from_compact
from forge_library import xml,embed,layer,compose_layers,lighting_descriptor

OUT=ROOT/'iterations/20-semantic-review/review-corrections';LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
CORRECTIONS={
 'accessibility_figure':('Accessibility',[('M12 2 a2 2 0 1 0 .01 0 M3 8 L12 10 L21 8 M12 10 V15 M12 15 L7 23 M12 15 L17 23',False)],'A wide-arm accessibility figure remains distinct from a generic person/account silhouette.'),
 'notifications_muted':('Notifications muted',[('M5 16 L7 13 V9 Q7 3 12 3 Q17 3 17 9 V13 L19 17 H5 M10 21 Q12 23 14 21 M2 2 L22 22',False)],'Native source is a crossed bell; a crossed speaker would change the notification domain.'),
 'pin_entry':('PIN entry',[('M3 3 H21 V21 H3 Z M7 8 H8 V11 M12 8 H14 V9.5 L12 11 H14 M17 8 H19 V11 H17 M7 15 H8 M12 15 H13 M17 15 H18',False)],'Actual source shows a numeric PIN pad, not a pushpin. Small geometric numerals are symbol geometry; live labels remain English resources.'),
 'error_alert':('Error',[('M2 12 a10 10 0 1 0 20 0 a10 10 0 1 0 -20 0 M12 5 V13 M12 17 V18',False)],'Actual source is an exclamation alert; an X conflates an error condition with cancel/close.'),
 'screenshot_frame':('Screenshot',[('M8 3 H3 V8 M16 3 H21 V8 M3 16 V21 H8 M21 16 V21 H16 M7 9 H17 V16 H7 Z',False)],'Capture brackets and an inner display denote screen capture rather than a physical camera.'),
 'headphones':('Headphones',[('M3 13 V11 Q3 2 12 2 Q21 2 21 11 V20 H16 V12 H21 M3 12 H8 V20 H3 Z',False)],'Headphones remain distinct from a headset with microphone.'),
 'data_disabled':('Mobile data off',[('M4 4 V17 M1 14 L4 17 L7 14 M20 20 V7 M17 10 L20 7 L23 10 M2 2 L22 22',False)],'Actual Settings source uses opposed data arrows with a slash; signal-strength bars would change the represented function.'),
 'recents_square':('Recent apps',[('M4 4 H20 V20 H4 Z',False)],'Native recents square remains distinct from the two-bar pause-shaped donor in the three-button navigation context.'),
}

def main():
    assert not (OUT.parent/'complete-assets.zip').exists()
    for folder in ['masters','source','exports','previews','android/res/drawable','android/res/values','verification/evidence']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    shutil.copy2(OUT.parent/'source/steel-material.png',OUT/'source/steel-material.png');shutil.copy2(OUT.parent/'runtime-style.json',OUT/'runtime-style.json');texture=base64.b64encode((OUT/'source/steel-material.png').read_bytes()).decode();style=json.loads((OUT/'runtime-style.json').read_text());rows=[];strings=E.Element('resources')
    for name,(label,shapes,rationale) in CORRECTIONS.items():
        for optical in ['compact','detailed']:
            doc=symbol(name,optical,shapes);key=name+'__'+optical;size=24 if optical=='compact' else 96;(OUT/'masters'/f'{key}.svg').write_text(xml(doc),encoding='utf8');cached={}
            for layer_name in LAYERS:
                for scale in [1,2]:
                    im=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(embed(layer(doc,layer_name),texture)),width=size*scale,skip_system_fonts=True))).convert('RGBA');im.save(OUT/'exports'/f'{key}.{layer_name}@{scale}x.png')
                    if scale==2:cached[layer_name]=im
            locked=name=='data_disabled'
            for state,descriptor in style['sampleStates'].items():compose_layers(cached,lighting_descriptor(descriptor,locked)).save(OUT/'exports'/f'{key}.{state}.preview.png')
            rows.append({'id':key,'semanticId':name,'type':'source-review-correction','optical':optical,'size':[size,size],'layers':LAYERS,'emissionLockedOff':locked,'unchangedReuse':False,'labelsBaked':False,'nativeIntegrated':False,'deviceVerified':False,'rationale':rationale})
            if optical=='compact':(OUT/'android/res/drawable'/f'cg_es_{name}.xml').write_text(native_from_compact(doc),encoding='utf8')
        E.SubElement(strings,'string',name='cg_semantic_'+name+'_label').text=label
    (OUT/'android/res/values/strings.xml').write_bytes(E.tostring(strings,encoding='utf-8',xml_declaration=True));write_json(OUT/'components.json',rows);write_json(OUT/'reuse-approvals.json',[])
    board=Image.new('RGB',(1600,835),'#080c11');draw=ImageDraw.Draw(board);draw.text((20,15),'FORGE / CORRECTIONS DISCOVERED BY SEMANTIC REVIEW',font=font(29,True),fill='#eee7d9');draw.text((20,60),'New dedicated geometry; cold and on previews. Mobile-data-off value remains cold.',font=font(18),fill='#b5bdc6')
    for i,(name,(label,_,_)) in enumerate(CORRECTIONS.items()):
        x=i%4*400;y=115+i//4*350;draw.text((x+18,y),label,font=font(23),fill='#eee7d9')
        for col,state in enumerate(['off','on']):
            im=Image.open(OUT/'exports'/f'{name}__detailed.{state}.preview.png');im.thumbnail((145,145));board.paste(im,(x+20+col*185,y+50),im);im=Image.open(OUT/'exports'/f'{name}__compact.{state}.preview.png');im.thumbnail((24,24));board.paste(im,(x+80+col*185,y+230),im)
        draw.text((x+18,y+280),'Cold                    On / selected',font=font(16),fill='#b5bdc6')
    board.save(OUT/'previews/source-review-corrections.png');print(json.dumps({'newSemanticCorrections':8,'masterFiles':16,'productionLayerExports':224}))

if __name__=='__main__':main()
