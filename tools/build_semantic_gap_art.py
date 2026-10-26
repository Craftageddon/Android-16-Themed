"""Current-style gap artwork with exact-byte reuse aliases and separate lighting masks."""
from pathlib import Path
import argparse,base64,hashlib,io,json,shutil,xml.etree.ElementTree as E
from PIL import Image,ImageDraw
from build_pilot import add,path,font,resvg_py
from forge_library import setup,steel,lights,layer,xml,embed,compose_layers,lighting_descriptor
from forge_semantic_gap_geometry import GEOMETRY,DETAIL_WIDTH,ALIASES,LABELS
from build_forge_coverage_art import native_vector
from build_symbols import geometry as old_geometry
from forge_completion_geometry import geometry as utility_geometry

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'iterations/20-semantic-review';LAYERS=['cold','reflection','spill','seam','core','focus','symbol']

def native_from_compact(doc):
    android='http://schemas.android.com/apk/res/android';svg='{http://www.w3.org/2000/svg}';E.register_namespace('android',android)
    def attr(**values):return {'{'+android+'}'+k:str(v) for k,v in values.items()}
    root=E.Element('vector',attr(width='24dp',height='24dp',viewportWidth=24,viewportHeight=24))
    cold=doc.find(svg+'g[@id="cold"]')
    for node in cold:
        assert node.tag==svg+'path' and not node.get('transform'),'Compact native adapter needs explicit geometry'
        def color(value):
            if value in [None,'none']:return '#00000000'
            assert value.startswith('#') and len(value)==7;return '#FF'+value[1:]
        E.SubElement(root,'path',attr(pathData=node.get('d'),fillColor=color(node.get('fill')),strokeColor=color(node.get('stroke')),strokeWidth=node.get('stroke-width','0'),strokeLineCap=node.get('stroke-linecap','butt'),strokeLineJoin=node.get('stroke-linejoin','miter'),fillAlpha=float(node.get('opacity','1'))*float(node.get('fill-opacity','1')),strokeAlpha=float(node.get('opacity','1'))*float(node.get('stroke-opacity','1'))))
    return E.tostring(root,encoding='unicode')

def symbol(name,optical,shapes=None):
    compact=optical=='compact';size=24 if compact else 96;r,g=setup(size,size,name+' / '+optical,view='0 0 24 24' if compact else '-3 -3 30 30')
    for i,(d,fill) in enumerate(GEOMETRY[name] if shapes is None else shapes):
        if compact:
            path(g['cold'],d,'#c0c7c9' if fill else 'none',stroke='#c0c7c9',width=1.35 if name=='qr_scanner' else 1.7)
            if i==0:path(g['seam'],d,stroke='white',width=.35,stroke_dasharray='1.5 120')
        else:steel(g['cold'],d,DETAIL_WIDTH.get(name,2.35),fill);lights(g,d,.24 if name=='qr_scanner' else .30)
    if not compact:
        path(g['focus'],'M-2 2 V-2 H2 M22 -2 H26 V2 M-2 22 V26 H2 M22 26 H26 V22',stroke='white',width=.35);path(g['symbol'],'M24 23 l.7 .7 l-.7 .7 l-.7 -.7 Z','white')
    return r

def main():
    assert not (OUT/'complete-assets.zip').exists(),'Preserve packaged checkpoints'
    for name in ['masters','source','exports','previews','android/res/drawable','android/res/values']:(OUT/name).mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'iterations/17-forge-coverage/source/steel-material.png',OUT/'source/steel-material.png');shutil.copy2(ROOT/'iterations/17-forge-coverage/runtime-style.json',OUT/'runtime-style.json')
    texture=base64.b64encode((OUT/'source/steel-material.png').read_bytes()).decode();style=json.loads((OUT/'runtime-style.json').read_text());records=[];approvals=[]
    def render(doc,width):return Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(embed(doc,texture)),width=width,skip_system_fonts=True))).convert('RGBA')
    for name in LABELS:
        for optical in ['compact','detailed']:
            key=name+'__'+optical;size=24 if optical=='compact' else 96;target=OUT/'masters'/f'{key}.svg'
            source=None
            if name in ALIASES:
                folder,donor=ALIASES[name];source=ROOT/'iterations'/folder/'masters'/f'{donor}__{optical}.svg';doc=E.parse(source).getroot()
                for im in doc.findall('.//{http://www.w3.org/2000/svg}image'):
                    href=im.get('href','');assert href=='../source/steel-material.png';assert (source.parent/href).read_bytes()==(OUT/'source/steel-material.png').read_bytes()
                shutil.copy2(source,target);approvals.append({'semanticId':name,'optical':optical,'source':source.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'target':target.relative_to(OUT).as_posix(),'targetSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'status':'Approved reuse of unchanged Forge geometry for this semantic target','reviewedBy':'Codex under the user instruction to resolve semantic reuse decisions','reviewedAt':'2026-10-26','reviewMethod':'Parsed upstream semantic glyph, compared actual rendered cold/on Forge donor, independently checked native compact cold pixel parity and exact donor SVG hashes','conditions':'Owner retains the distinct semantic resource ID and native English label/content description; this approves artwork reuse, not hardware or OS-owner runtime acceptance','rationale':'Same established low-brightness metaphor with native Extra dim label' if name=='extra_dim' else 'Same established pen metaphor with native Stylus label; physical-input context supplied by owner'})
            else:doc=symbol(name,optical);target.write_text(xml(doc),encoding='utf8')
            cached={}
            for layer_name in LAYERS:
                for scale in [1,2]:
                    image=render(layer(doc,layer_name),size*scale);image.save(OUT/'exports'/f'{key}.{layer_name}@{scale}x.png')
                    if scale==2:cached[layer_name]=image
            # Sensors Off is an ACTIVE privacy mode, not an inactive control value.
            # Exact source-owner evidence is recorded in state-domain-decisions.json.
            locked=name in ['live_captions_off','work_profile_paused','favorite_outline']
            for state,descriptor in style['sampleStates'].items():compose_layers(cached,lighting_descriptor(descriptor,locked)).save(OUT/'exports'/f'{key}.{state}.preview.png')
            records.append({'id':key,'semanticId':name,'type':'semantic-source-gap','optical':optical,'size':[size,size],'layers':LAYERS,'emissionLockedOff':locked,'unchangedReuse':source is not None,'source':source.relative_to(ROOT).as_posix() if source else None,'labelsBaked':False,'nativeIntegrated':False,'deviceVerified':False})
            print(key,flush=True)
        compact=E.parse(OUT/'masters'/f'{name}__compact.svg').getroot()
        (OUT/'android/res/drawable'/f'cg_es_{name}.xml').write_text(native_from_compact(compact),encoding='utf8')
    resources=E.Element('resources')
    for name,label in LABELS.items():E.SubElement(resources,'string',name='cg_semantic_'+name+'_label').text=label
    (OUT/'android/res/values/strings.xml').write_bytes(E.tostring(resources,encoding='utf-8',xml_declaration=True))
    (OUT/'android/res/drawable/cg_es_favorite_state.xml').write_text('<selector xmlns:android="http://schemas.android.com/apk/res/android"><item android:state_checked="true" android:drawable="@drawable/cg_es_favorite"/><item android:drawable="@drawable/cg_es_favorite_outline"/></selector>\n',encoding='utf8')
    (OUT/'components.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8');(OUT/'reuse-approvals.json').write_text(json.dumps(approvals,indent=2)+'\n',encoding='utf8')
    for start in range(0,len(LABELS),12):
        board=Image.new('RGB',(1600,1120),'#080c11');draw=ImageDraw.Draw(board);draw.text((25,18),'FORGE / SOURCE GAP ARTWORK / COLD AND ON',font=font(29,True),fill='#eee7d9');draw.text((25,62),'Existing low-brightness and pen geometry reused; all other treatments are new. Off-value variants stay cold.',font=font(17),fill='#b5bdc6')
        for i,name in enumerate(list(LABELS)[start:start+12]):
            x=i%4*400;y=110+i//4*325;draw.text((x+18,y),LABELS[name],font=font(20),fill='#eee7d9')
            for col,state in enumerate(['off','on']):
                im=Image.open(OUT/'exports'/f'{name}__detailed.{state}.preview.png');im.thumbnail((145,145));board.paste(im,(x+25+col*185,y+50),im)
                im=Image.open(OUT/'exports'/f'{name}__compact.{state}.preview.png');im.thumbnail((24,24));board.paste(im,(x+84+col*185,y+228),im)
            draw.text((x+25,y+278),'Cold / off             On / selected',font=font(16),fill='#b5bdc6')
        board.save(OUT/'previews'/f'semantic-gap-art-{start//12+1:02}.png')
    print(json.dumps({'semanticTreatments':len(LABELS),'newTreatmentsIncludingStateVariants':len(GEOMETRY),'unchangedAliasTreatments':len(ALIASES),'masterFiles':len(records),'productionExports':len(records)*14}))

if __name__=='__main__':main()
