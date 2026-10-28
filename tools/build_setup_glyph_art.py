'''First artwork pass for setup source glyphs; owner bindings remain pending.'''
from pathlib import Path
import base64,collections,hashlib,math,shutil,xml.etree.ElementTree as E
from PIL import Image,ImageDraw
from audit_os_resource_coverage import ROOT,read_json,write_json
from forge_library import layer,raster,xml
from build_pilot import SVG,font
import build_gallery_art as geometry
import preview_gallery_art as preview
OUT=ROOT/'iterations/28-setup-workflows';UP=OUT/'upstream/packages/apps/SetupWizard';RES=OUT/'artwork-resources';A='{http://schemas.android.com/apk/res/android}'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol'];DENSITIES=[('mdpi',1),('hdpi',1.5),('xhdpi',2),('xxhdpi',3)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (OUT/'complete-assets.zip').exists()
 source=OUT/'source';source.mkdir(exist_ok=True);steel=ROOT/'iterations/27-gallery-contracts/source/steel-material.png';shutil.copy2(steel,source/'steel-material.png');texture=base64.b64encode(steel.read_bytes()).decode();masters=OUT/'masters';masters.mkdir(exist_ok=True);inputs=source/'geometry-inputs';inputs.mkdir(exist_ok=True);rows=[];geometry.OUT=OUT
 for file in sorted((UP/'app/src/main/res/drawable').glob('ic_*.xml')):
  if file.stem.startswith('ic_launcher'):continue
  original=E.parse(file).getroot();assert original.tag=='vector';vw=float(original.get(A+'viewportWidth'));vh=float(original.get(A+'viewportHeight'));native_w=float(original.get(A+'width').removesuffix('dp'));native_h=float(original.get(A+'height').removesuffix('dp'));assert abs(native_w/native_h-vw/vh)<.00001
  normal=E.fromstring(file.read_bytes());changes=[]
  for node in normal.iter():
   for attribute in ['fillColor','strokeColor']:
    value=node.get(A+attribute)
    if value in ['?android:colorControlNormal','@color/finish_swipe_arrow']:
     changes.append({'attribute':attribute,'sourceColorRole':value,'newGeometryMaskColor':'@android:color/white','pathData':node.get(A+'pathData')});node.set(A+attribute,'@android:color/white')
  lettering_free_globe=file.stem=='ic_locale'
  if lettering_free_globe:
   for child in list(normal):normal.remove(child)
   for d in ['M12,2A10,10 0 1,0 12,22A10,10 0 1,0 12,2Z','M12,2C6.5,5 6.5,19 12,22C17.5,19 17.5,5 12,2Z','M3.4,7Q12,10.4 20.6,7','M3.4,17Q12,13.6 20.6,17','M2,12H22']:
    E.SubElement(normal,'path',{A+'pathData':d,A+'fillColor':'@android:color/transparent',A+'strokeColor':'@android:color/white',A+'strokeWidth':'1.15'})
  normalized=inputs/file.name;normalized.write_bytes(E.tostring(normal,encoding='utf-8',xml_declaration=True)+b'\n')
  before=[n.get(A+'pathData') for n in original.iter('path')];after=[n.get(A+'pathData') for n in normal.iter('path')];assert (before!=after) if lettering_free_globe else (before==after)
  root,origin=geometry.source_treatment(normalized)
  if vw!=vh:
   root.set('height',str(96*vh/vw));root.set('viewBox',f'0 0 96 {96*vh/vw}')
   for name in LAYERS:root.find('{'+SVG+'}g[@id="'+name+'"]').set('transform',f'scale(1 {vh/vw})')
  root.find('{'+SVG+'}title').text='Craftageddon Setup / '+file.stem;key='cg_sw_'+file.stem.removeprefix('ic_');master=masters/(key+'.svg');master.write_bytes(xml(root).encode('utf8'));exports=[]
  for density,scale in DENSITIES:
   folder=RES/('drawable-'+density);folder.mkdir(parents=True,exist_ok=True)
   for name in LAYERS:
    image=raster(layer(root,name),round(native_w*scale),texture);p=folder/(key+'_'+name+'.png');image.save(p);rgba=image.convert('RGBA')
    if name!='cold':assert all(r==g==b for r,g,b,a in rgba.get_flattened_data() if a),p
    exports.append({'path':p.relative_to(OUT).as_posix(),'sha256':sha(p),'density':density,'scale':scale,'layer':name,'size':list(image.size)})
  high=[]
  folder=RES/'drawable-nodpi';folder.mkdir(exist_ok=True)
  for name in LAYERS:
   im=raster(layer(root,name),384,texture);p=folder/(key+'_hi_'+name+'.png');im.save(p)
   if name!='cold':assert all(r==g==b for r,g,b,a in im.convert('RGBA').get_flattened_data() if a),p
   high.append({'path':p.relative_to(OUT).as_posix(),'sha256':sha(p),'layer':name,'size':list(im.size),'purpose':'Higher pixel resolution for native Glif upscaling; original intrinsic dp retained separately'})
  rows.append({'id':key,'kind':'new-lettering-free-language-globe' if lettering_free_globe else 'source-geometry-artwork-pass','logicalSize':max(native_w,native_h),'nativeIntrinsicDp':[native_w,native_h],'master':master.relative_to(OUT).as_posix(),'masterSha256':sha(master),'source':{'original':file.relative_to(ROOT).as_posix(),'sha256':sha(file),'nativeViewport':origin['nativeViewport'],'sourcePathData':before,'newPathData':after,'sourcePathGeometryPreserved':not lettering_free_globe,'semanticGeometryChange':'Language lettering replaced by a newly drawn globe; native English label remains live source text' if lettering_free_globe else None,'geometryNormalization':normalized.relative_to(OUT).as_posix(),'normalizedSha256':sha(normalized),'materialRoleChanges':changes,'sourceFillAlphaRetained':True,'sourceColorRoleReview':'This is a geometry/material authoring pass. Dynamic theme color roles become new cold material and separate neutral light masks; actual native tint/state binding still requires review.','autoMirrored':original.get(A+'autoMirrored')=='true'},'files':exports,'nativeHighResolution':high,'nativeOwnerBinding':'NOT YET AUTHORED','semanticDecision':'OPEN; no reuse/drop-in approval inferred'})
 assert len(rows)==18 and sum(len(r['files']) for r in rows)==504
 write_json(OUT/'setup-art-components.json',rows)
 preview.OUT=OUT;preview.RES=RES/'drawable-mdpi';dest=OUT/'previews';dest.mkdir(exist_ok=True);sheet=Image.new('RGB',(1320,1100),'#080c11');d=ImageDraw.Draw(sheet)
 d.text((20,16),'SETUP / SOURCE GLYPH MATERIAL PASS',font=font(26),fill='#eee7d9');d.text((20,54),'Cold material and separate light-mask demonstrations / native owner bindings pending',font=font(16),fill='#b5bdc6')
 for i,row in enumerate(rows):
  x=20+(i%4)*330;y=100+(i//4)*195;d.text((x,y),row['id'].removeprefix('cg_sw_').replace('_',' '),font=font(15),fill='#eee7d9')
  for j,state in enumerate(['cold','on']):
   im=preview.compose(row['id'],state,detail=True);sheet.paste(im,(x+j*145,y+27),im);d.text((x+j*145,y+131),'Cold' if state=='cold' else 'Mask sample',font=font(13),fill='#b5bdc6')
  tiny=preview.compose(row['id']);tiny.thumbnail((48,26));sheet.paste(tiny,(x,y+157),tiny)
 sheet.save(dest/'setup-source-glyphs-pass1.preview.png')
 write_json(OUT/'verification/evidence/setup-glyph-artwork-pass.json',{'result':'PASS','sourceGeometryTreatments':17,'newLetteringFreeLanguageGlobe':1,'editableLayeredMasters':18,'densityPngConfigurations':504,'higherResolutionNodpiLayers':126,'totalPngConfigurations':630,'coldPngConfigurations':90,'neutralMaskPngConfigurations':540,'sourcePathGeometryPreservedFor17OriginalGlyphs':True,'originalNativeAspectRatiosPreserved':True,'productionImageTextBaked':False,'runtimeGlowBakedIntoColdImages':False,'priorSteelTextureHash':sha(steel),'nativeSourceBindings':'NOT YET AUTHORED','nativeCompileInflationDeviceAcceptance':'NOT RUN','baselineFamilyDecisionsClosed':0,'wholeGoalComplete':False})
 wip=read_json(OUT/'WORK-IN-PROGRESS.json');wip.update(artworkAndOwnerAdaptation='First artwork pass:17 source-geometry glyph masters plus1 newly drawn lettering-free language globe and630 separate cold/mask PNG configurations, including126 higher-resolution header layers. Native owner bindings, larger illustrations/identity/Lottie/template work remain pending.',baselineSetupFamilyDecisionsClosed=0);write_json(OUT/'WORK-IN-PROGRESS.json',wip)
 print({'sourceGlyphTreatments':18,'editableMasters':18,'coldPngs':90,'neutralMaskPngs':540,'nativeBindings':'PENDING','baselineDecisionsClosed':0})
if __name__=='__main__':main()
