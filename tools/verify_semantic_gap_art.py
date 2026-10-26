"""Check actual exports, aliases, state lighting and independent native-vector pixels."""
from pathlib import Path
import argparse,hashlib,io,json,xml.etree.ElementTree as E,zipfile
from PIL import Image,ImageChops
from build_pilot import resvg_py
from forge_library import compose_layers,lighting_descriptor
from forge_semantic_gap_geometry import LABELS,ALIASES,GEOMETRY
from audit_os_resource_coverage import ROOT,write_json

OUT=ROOT/'iterations/20-semantic-review';NS='{http://www.w3.org/2000/svg}';AN='{http://schemas.android.com/apk/res/android}'

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=OUT);args=parser.parse_args();OUT=args.root.resolve()
    rows=json.loads((OUT/'components.json').read_text());style=json.loads((OUT/'runtime-style.json').read_text());assert len(rows)==(16 if OUT.name=='review-corrections' else 38)
    clipping=[];exports=states=native=0
    for row in rows:
        doc=E.parse(OUT/'masters'/f"{row['id']}.svg").getroot();assert not doc.findall('.//'+NS+'text')
        for name in ['reflection','spill','seam','core','focus','symbol']:assert doc.find(NS+'g[@id="'+name+'"]').get('style')=='display:none'
        for scale in [1,2]:
            images={}
            for name in row['layers']:
                im=Image.open(OUT/'exports'/f"{row['id']}.{name}@{scale}x.png").convert('RGBA');assert im.size==(row['size'][0]*scale,row['size'][1]*scale);assert im.getchannel('A').getextrema()[0]==0
                if name!='cold':
                    r,g,b,a=im.split();assert not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox()
                images[name]=im;exports+=1
            if scale==2:
                for st,descriptor in style['sampleStates'].items():
                    expected=compose_layers(images,lighting_descriptor(descriptor,row['emissionLockedOff']));actual=Image.open(OUT/'exports'/f"{row['id']}.{st}.preview.png").convert('RGBA');assert expected.tobytes()==actual.tobytes();states+=1
                assert Image.open(OUT/'exports'/f"{row['id']}.off.preview.png").convert('RGBA').tobytes()==images['cold'].tobytes()
        if row['optical']=='compact':
            # Expanded viewport exposes any pixels that the24px source canvas would clip.
            doc.set('viewBox','-1 -1 26 26');doc.set('width','26');doc.set('height','26')
            image=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(doc,encoding='unicode'),width=260,skip_system_fonts=True))).convert('RGBA');alpha=image.getchannel('A');bounds=alpha.point(lambda x:255 if x>8 else 0).getbbox()
            if bounds and (bounds[0]<10 or bounds[1]<10 or bounds[2]>250 or bounds[3]>250):clipping.append({'asset':row['id'],'expandedAlphaBounds':bounds})
            vector=E.parse(OUT/'android/res/drawable'/('cg_es_'+row['semanticId']+'.xml')).getroot();svg=E.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':'0 0 24 24','width':'24','height':'24'})
            def color(value):return 'none' if value=='#00000000' else '#'+value[3:]
            for node in vector.findall('path'):
                E.SubElement(svg,'path',{'d':node.get(AN+'pathData'),'fill':color(node.get(AN+'fillColor')),'stroke':color(node.get(AN+'strokeColor')),'stroke-width':node.get(AN+'strokeWidth'),'stroke-linecap':node.get(AN+'strokeLineCap'),'stroke-linejoin':node.get(AN+'strokeLineJoin'),'fill-opacity':node.get(AN+'fillAlpha'),'stroke-opacity':node.get(AN+'strokeAlpha')})
            nativepng=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=E.tostring(svg,encoding='unicode'),width=48,skip_system_fonts=True))).convert('RGBA');cold=Image.open(OUT/'exports'/f"{row['id']}.cold@2x.png").convert('RGBA');assert nativepng.tobytes()==cold.tobytes(),('Native cold parity',row['id']);native+=1
    for approval in json.loads((OUT/'reuse-approvals.json').read_text()):
        assert (ROOT/approval['source']).read_bytes()==(OUT/approval['target']).read_bytes();assert hashlib.sha256((OUT/approval['target']).read_bytes()).hexdigest()==approval['sourceSha256']
    report={'result':'FAIL' if clipping else 'PASS','masterFiles':len(rows),'newIndependentMasters':sum(not x['unchangedReuse'] for x in rows),'unchangedReuseMasterCopies':sum(x['unchangedReuse'] for x in rows),'semanticTreatmentsIncludingVariants':len({x['semanticId'] for x in rows}),'productionExports':exports,'exactStateRecompositions':states,'nativeCompactPixelComparisons':native,'compactClipping':clipping,'authoredEnglishLabels':len(E.parse(OUT/'android/res/values/strings.xml').getroot()),'method':'Actual PNG alpha and neutral-channel checks; exact independent state recomposition and off/cold equality; expanded-viewport clipping; parse native vector XML independently and compare all cold pixels; unchanged donor byte hashes','nativeDeviceAcceptance':'NOT RUN'}
    write_json(OUT/'verification/evidence/gap-art-checks.json',report);print(json.dumps(report));assert not clipping,'Compact geometry clipped'

if __name__=='__main__':main()
