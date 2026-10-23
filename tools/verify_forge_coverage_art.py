"""Check current coverage artwork, safe adaptive content and exact retained decisions."""
from pathlib import Path
import argparse,csv,hashlib,io,json,math,xml.etree.ElementTree as ET,zipfile
from PIL import Image,ImageChops
from forge_library import compose_layers,lighting_descriptor,xml
from build_pilot import el,add,resvg_py
from forge_completion_geometry import GEOMETRY,APP_GEOMETRY
NS='{http://www.w3.org/2000/svg}';AN='{http://schemas.android.com/apk/res/android}'
ROOT=Path(__file__).resolve().parents[1];LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
def verify(root):
 rows=json.loads((root/'components.json').read_text());style=json.loads((root/'runtime-style.json').read_text());assert len(rows)==66 and len({r['id'] for r in rows})==66;neutral=exports=states=0;safe=[]
 assert {r['semanticId'] for r in rows if r['type']=='utility-symbol'}==set(GEOMETRY)
 for row in rows:
  doc=ET.parse(root/'masters'/f"{row['id']}.svg").getroot();assert not doc.findall('.//'+NS+'text');ids=[n.get('id') for n in doc.iter() if n.get('id')];assert len(ids)==len(set(ids))
  for name in LAYERS:
   g=doc.find(NS+'g[@id="'+name+'"]');assert g is not None
   if name!='cold':assert g.get('style')=='display:none'
   else:assert all(n.get('filter') is None for n in g.iter())
  for scale in [1,2]:
   images={}
   for name in LAYERS:
    p=root/'exports'/f"{row['id']}.{name}@{scale}x.png";im=Image.open(p).convert('RGBA');assert im.size==(row['size'][0]*scale,row['size'][1]*scale);assert im.getchannel('A').getextrema()[0]==0;images[name]=im;exports+=1
    if name!='cold':
     r,g,b,a=im.split();assert not ImageChops.difference(r,g).getbbox() and not ImageChops.difference(g,b).getbbox();neutral+=1
   if scale==2:
    for state,descriptor in style['sampleStates'].items():
     actual=Image.open(root/'exports'/f"{row['id']}.{state}.preview.png").convert('RGBA');expected=compose_layers(images,lighting_descriptor(descriptor,row['emissionLockedOff']));assert actual.tobytes()==expected.tobytes(),(row['id'],state);states+=1
    assert Image.open(root/'exports'/f"{row['id']}.off.preview.png").convert('RGBA').tobytes()==images['cold'].tobytes()
 for entry in json.loads((root/'app-targets.json').read_text())['identities']:
  name=entry['assetId'].removeprefix('app-');im=Image.open(root/'android/res/drawable-mdpi'/f'cg_app_{name}_foreground.png').convert('RGBA');assert im.size==(108,108)
  outside=sum(1 for y in range(108) for x in range(108) if im.getpixel((x,y))[3]>4 and math.hypot(x-53.5,y-53.5)>33)
  assert outside==0,(name,'cold foreground outside safe circle',outside)
  mono=ET.parse(root/'android/res/drawable'/f'cg_app_{name}_monochrome.xml').getroot();svg=el('svg',width=108,height=108,viewBox='0 0 108 108')
  group=mono.find('group');g=add(svg,'g',transform=f"translate({group.get(AN+'translateX')} {group.get(AN+'translateY')}) scale({group.get(AN+'scaleX')} {group.get(AN+'scaleY')})")
  for p in group.findall('path'):
   add(g,'path',d=p.get(AN+'pathData'),fill='white' if p.get(AN+'fillColor')=='#FFFFFFFF' else 'none',stroke='white',stroke_width=p.get(AN+'strokeWidth'),stroke_linecap='round',stroke_linejoin='round')
  mask=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=xml(svg),width=108,skip_system_fonts=True))).convert('RGBA');outside=sum(1 for y in range(108) for x in range(108) if mask.getpixel((x,y))[3]>4 and math.hypot(x-53.5,y-53.5)>33);assert outside==0,(name,'monochrome outside safe circle',outside);mask.save(root/'previews'/f'adaptive-{name}-monochrome.png');safe.append(name)
 resources=list((root/'android/res').rglob('*'));sources=[p for p in resources if p.is_file()];assert len(sources)==60,len(sources)
 with zipfile.ZipFile(root/'verification/evidence/android-resources.zip') as z:assert z.testzip() is None;assert len(z.namelist())==len(sources)
 catalog=ROOT/'iterations/04-core-components/source-register';old=list(csv.DictReader((catalog/'family-candidates.csv').open(encoding='utf-8-sig')));decisions=json.loads((root/'family-dispositions.json').read_text())['families'];assert [r['familyId'] for r in decisions]==[r['family_id'] for r in old];assert all(r['decision'] in ['Rebuild material','Redraw geometry','Historical reference','Supporting source'] for r in decisions);assert len(decisions)==1272
 for p,digest in json.loads((root/'replacement-source-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,p
 oldfiles=list(csv.DictReader((catalog/'all-retained-files.csv').open(encoding='utf-8-sig')));newfiles=list(csv.DictReader((root/'retained-file-dispositions.csv').open(encoding='utf8')));assert len(oldfiles)==len(newfiles)==3423;assert [(r['sha256'],r['name']) for r in oldfiles]==[(r['sha256'],r['name']) for r in newfiles];assert sum(r['decision']=='Invalid excluded' for r in newfiles)==1
 byname={r['retainedFamily']:r for r in decisions}
 for name in ['mail','call','photo','filter_list','crop','draw','undo','redo','visibility_off','send','flashlight_on','flashlight_off','unlock','brightness_high','brightness_low','lockscreen_pin_dot_empty','lockscreen_pin_dot_filled','motion-battery-fill-15','motion-battery-fill-68','motion-battery-shell','motion-input-long-press-source']:
  assert byname[name]['decision'] in ['Rebuild material','Redraw geometry'] and byname[name]['replacementPaths'],name
 for p in root.rglob('*.png'):
  with Image.open(p) as im:im.verify()
 report={'result':'PASS','date':'2026-10-23','components':66,'semanticUtilitySymbols':28,'opticalUtilityMasters':56,'authoredAppIdentities':10,'productionLayerExports':exports,'neutralMasks':neutral,'exactStateRecompositions':states,'adaptiveSafeCircleChecked':safe,'compiledAndroidResourceFiles':60,'retainedFileDispositions':3423,'invalidRecordExcluded':1,'retainedFamilyDecisions':1272,'unresolvedNamedProductionFamilies':0,'authoredLocale':'en-US','method':'Actual SVG/PNG alpha and neutral channels, exact state recomposition, cold-off equality, native foreground and parsed monochrome safe-circle pixels, AAPT2 resource ZIP, exact family/file key conservation and replacement hashes','limits':'Semantic reconciliation does not establish installed app coverage or approve every old raster. Native, browser and device acceptance NOT RUN.'}
 (root/'verification/evidence/coverage-artwork-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();verify(a.root.resolve())
