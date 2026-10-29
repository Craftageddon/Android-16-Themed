"""Reference-based material recovery; all prior checkpoints remain frozen."""
from pathlib import Path
import base64, collections, copy, difflib, hashlib, io, json, math, shutil
import xml.etree.ElementTree as E
from PIL import Image, ImageDraw
from forge_library import layer, raster, xml
from build_pilot import font
from build_scalable_frames import stretch
from build_reference_correction_pilot import compose, STATES, COLORS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'iterations/30-reference-style-recovery'
NS='{http://www.w3.org/2000/svg}'
LAYERS=['cold','reflection','spill','seam','core','focus','symbol']
EDGE=['#929390','#3c4145','#111418','#596066','#111419']
OPTICAL=['#84817a','#4b4c49','#282b2c','#66645f','#252829']
GROUPS={'magnification':'23-magnification','updater':'25-updater-workflows',
        'gallery':'26-gallery-workflows','setup':'28-setup-workflows','ayn':'21-native-workflows'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save_json(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8')
def group(root,name):return root.find(NS+"g[@id='"+name+"']")
def palette(root,gid,colors):
 node=root.find('.//'+NS+"linearGradient[@id='"+gid+"']")
 if node is not None:
  assert len(node)==len(colors)
  for stop,color in zip(node,colors):stop.set('stop-color',color)

def correct_material(root,category,viewport=None):
 """Restore texture coats from the known five-path steel construction."""
 root=copy.deepcopy(root);cold=group(root,'cold');assert cold is not None
 palette(root,'edge',OPTICAL if category=='magnification' else EDGE)
 palette(root,'native-bevel',OPTICAL)
 filled={p.get('d') for p in cold.iter(NS+'path') if p.get('fill') in ['url(#edge)','url(#steel)','url(#glyph-steel)']}
 for node in cold.iter():
  if node.get('fill')=='url(#glyph-steel)':node.set('fill','url(#forged)')
  if node.get('stroke')=='url(#forged)':
   node.attrib.pop('opacity',None)
   if node.get('d') in filled:node.set('fill','url(#forged)')
  if node.get('stroke')=='url(#edge)' and node.get('d') in filled:node.set('fill','url(#forged)')
  if node.get('fill')=='url(#forged)' and node.get('opacity') in ['0.14','.14']:node.attrib.pop('opacity',None)
  for a in ['stroke','fill']:
   color=node.get(a,'').lower()
   if color in ['#b8c0c4','#c0c7c9']:node.set(a,'url(#edge)')
   if color=='#cbd4d9':node.set(a,'#6d6c66')
   if color=='#b2bdc6':node.set(a,'#77776f')
 if viewport:
  pattern=root.find('.//'+NS+"pattern[@id='forged']")
  if pattern is not None:
   for n in pattern.iter():
    for a in ['width','height']:
     if n.get(a):n.set(a,str(round(viewport*.8,4)))
 # Eliminate the old unused silver gradient, not just its live use.
 defs=root.find(NS+'defs')
 # Original reference spill blur is about one percent of the artwork width.
 # The later 24-unit glyphs inherited a 1.5-unit blur (over six percent).
 local_width=viewport or float(root.get('viewBox').split()[2])
 for fid,ratio in [('light-spill',.010),('light-reflection',.004)]:
  filt=defs.find(NS+"filter[@id='"+fid+"']")
  if filt is not None:
   blur=filt.find(NS+'feGaussianBlur')
   if blur is not None:blur.set('stdDeviation',str(round(local_width*ratio,5)))
 old=defs.find(NS+"linearGradient[@id='glyph-steel']")
 if old is not None:
  assert not any('url(#glyph-steel)' in v for n in cold.iter() for v in n.attrib.values())
  defs.remove(old)
 return root

def entries():
 result=[]
 for category in GROUPS:
  old=ROOT/'iterations'/GROUPS[category]
  if category=='magnification':
   for row in json.loads((old/'components.json').read_text()):
    if not row.get('nativeSourceResource'):continue
    configs=[{'path':v['file'],'layer':v['layer'],'density':v['density']} for v in row['densityConfigurations']]
    vw=float(row['sourceVectorGeometry'][0]['attributes']['{http://schemas.android.com/apk/res/android}viewportWidth'])
    result.append(dict(category=category,id=row['id'],old=old,master=old/'masters'/(row['id']+'.svg'),configs=configs,viewport=vw))
  elif category=='ayn':
   configs=[{'path':f'native-patch/hardware/ayn/packages/AynParts/res/drawable-{density}/cg_ayn_dot_{name}.png','layer':name,'density':density} for density in ['mdpi','xhdpi','xxhdpi'] for name in LAYERS]
   result.append(dict(category=category,id='ayn_dot',old=old,master=old/'masters/ayn_dot.svg',configs=configs,viewport=20))
  else:
   filename={'updater':'workflow-art-components.json','gallery':'gallery-art-components.json','setup':'setup-art-components.json'}[category]
   for row in json.loads((old/filename).read_text()):
    if category=='updater':
     key=row['id'];master={'cg_upd_pause':'optical_pause_32','cg_upd_resume':'optical_play_32','cg_upd_badge':'optical_app_updater'}.get(key)
     if master is None:master=('update_' if key in ['cg_upd_scan','cg_upd_error','cg_upd_ready'] else 'glyph_')+key.removeprefix('cg_upd_')
     p=old/'masters'/(master+'.svg')
    else:p=old/row['master']
    source=row.get('source',{});vw=source.get('nativeViewport',[None])[0] if isinstance(source,dict) else None
    if category=='gallery' and not vw and row['logicalSize']==24:vw=24
    configs=[{'path':v['path'],'layer':v['layer'],'density':v['density']} for v in row['files']]
    configs += [{'path':v['path'],'layer':v['layer'],'density':'nodpi'} for v in row.get('nativeHighResolution',[])]
    result.append(dict(category=category,id=row['id'],old=old,master=p,configs=configs,viewport=vw))
 assert len(result)==99 and sum(len(e['configs']) for e in result)==2895
 return result

def portable_links(root,href):
 for n in root.iter(NS+'image'):
  if 'steel-material.png' in n.get('href','') or n.get('href','').startswith('data:image/png'):n.set('href',href)

def isolate(root,name):
 q=layer(root,name)
 if name!='cold':
  # Neutral masks never use a material texture; remove unused pattern payloads.
  for defs in q.findall(NS+'defs'):
   for n in list(defs):
    if n.tag==NS+'pattern':
     assert not any('url(#'+n.get('id','')+')' in v for g in q.findall(NS+'g') for e in g.iter() for v in e.attrib.values())
     defs.remove(n)
 return q

def ninepatch_like(image,original):
 assert image.size==(original.width-2,original.height-2)
 out=Image.new('RGBA',original.size);out.paste(image,(1,1))
 for box in [(0,0,original.width,1),(0,original.height-1,original.width,original.height),(0,0,1,original.height),(original.width-1,0,original.width,original.height)]:out.paste(original.crop(box),box[:2])
 return out

def border_patch():
 old=ROOT/'iterations/23-magnification/native-patch/frameworks/base/packages/SystemUI/src/com/android/systemui/accessibility/ForgeMagnificationBorderDrawable.java'
 original=old.read_text(encoding='utf8')
 changes={'0xff9da9b2':'0xff84817a','0xff394957':'0xff4b4c49','0xff101924':'0xff282b2c','0xff576b7b':'0xff66645f','0xffb0bec8':'0xff252829','0xffb2bdc6':'0xff77776f'}
 fixed=original
 for a,b in changes.items():assert fixed.count(a)==1;fixed=fixed.replace(a,b)
 check=fixed
 for a,b in changes.items():check=check.replace(b,a)
 assert check==original
 rel=Path('frameworks/base/packages/SystemUI/src/com/android/systemui/accessibility/ForgeMagnificationBorderDrawable.java')
 p=OUT/'native-appearance-proposal'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(fixed,encoding='utf8')
 patch=''.join(difflib.unified_diff(original.splitlines(True),fixed.splitlines(True),fromfile='a/'+rel.as_posix(),tofile='b/'+rel.as_posix()))
 (OUT/'native-appearance-proposal/magnification-material-only.patch').write_text(patch,encoding='utf8')
 save_json(OUT/'native-appearance-proposal/source-resource-acceptance-map.json',{'source':old.relative_to(ROOT).as_posix(),'sourceSha256':sha(old),'proposal':p.relative_to(OUT).as_posix(),'proposalSha256':sha(p),'exactChange':'Six color literals only; shader operations, alpha, paths, dimensions, radius, state and callbacks unchanged','nativeGeometryOwner':'ForgeBorderGeometry','resourcesUnchanged':['magnifier_border_width','magnifier_border_width_fullscreen','magnifier_border_width_fullscreen_with_offset','magnifier_corner_radius','magnifier_edit_corner_radius','magnifier_edit_dash_gap'],'materialChanges':changes,'compile':'NOT RUN for this cosmetic proposal','nativeInflationDeviceAndPerformance':'NOT RUN','hardwareOperations':False})

def compact_audit():
 rows=[]
 for folder in ['11-forge-symbol-library','17-forge-coverage','20-semantic-review']:
  for p in sorted((ROOT/'iterations'/folder/'masters').glob('*__compact.svg')):
   donor=p.with_name(p.name.replace('__compact','__detailed'));assert donor.exists()
   rows.append({'compact':p.relative_to(ROOT).as_posix(),'compactSha256':sha(p),'detailedCounterpart':donor.relative_to(ROOT).as_posix(),'detailedSha256':sha(donor),'disposition':'Preserve neutral compact/vector mask. Use the detailed counterpart for forged presentation; owner-specific placement and installed tint behavior remain unverified.'})
 save_json(OUT/'compact-mask-role-audit.json',{'records':len(rows),'distinctCompactContents':len({r['compactSha256'] for r in rows}),'everyCompactHasDetailedCounterpart':True,'sourceEvidence':['tools/forge_library.py:57','tools/build_forge_coverage_art.py:12','tools/build_forge_coverage_art.py:57','tools/build_semantic_gap_art.py:28'],'neutralMaskRecoloringPerformed':False,'installedRoleAcceptance':'NOT RUN','mappings':rows})

def build():
 assert not (OUT/'complete-assets.zip').exists(),'Frozen checkpoint: use a new iteration.'
 (OUT/'source').mkdir(parents=True,exist_ok=True)
 tex=ROOT/'iterations/11-forge-symbol-library/source/steel-material.png';shutil.copy2(tex,OUT/'source/steel-material.png');texture=base64.b64encode(tex.read_bytes()).decode()
 inputs=entries();rows=[];comparisons={};preserved={}
 # All earlier master files and native source proposal inputs are hash-bound before authoring.
 for folder in (ROOT/'iterations').iterdir():
  if folder.is_dir() and folder.name[:2].isdigit() and 10<=int(folder.name[:2])<=29:
   for p in (folder/'masters').rglob('*.svg'):preserved[p.relative_to(ROOT).as_posix()]=sha(p)
 pilot={('magnification','close'):'close',('setup','cg_sw_location'):'location',('gallery','cg_gl_media_frame'):'photo_frame',('gallery','cg_gl_app_gallery'):'gallery_badge'}
 for at,item in enumerate(inputs,1):
  category,key=item['category'],item['id'];oldroot=E.parse(item['master']).getroot()
  pilot_key=pilot.get((category,key))
  if pilot_key:root=E.parse(ROOT/'iterations/29-reference-correction-pilot/masters'/(pilot_key+'.svg')).getroot()
  else:root=correct_material(oldroot,category,item['viewport'])
  portable_links(root,'../../source/steel-material.png')
  dest=OUT/'masters'/category/(key+'.svg');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(xml(root),encoding='utf8')
  layernames=[n.get('id') for n in root.findall(NS+'g') if n.get('id') in LAYERS+['motion']]
  cache={};files=[]
  for name in layernames:
   doc=isolate(root,name);lp=OUT/'layers'/category/(key+'.'+name+'.svg');lp.parent.mkdir(parents=True,exist_ok=True);lp.write_text(xml(doc),encoding='utf8');cache[name]=doc
  for config in item['configs']:
   original=item['old']/config['path'];assert original.exists(),original
   oldim=Image.open(original).convert('RGBA');nine=original.name.endswith('.9.png');width=oldim.width-2 if nine else oldim.width
   im=raster(cache[config['layer']],width,texture)
   assert im.size==((oldim.width-2,oldim.height-2) if nine else oldim.size),(key,config,im.size,oldim.size)
   if config['layer']!='cold':assert all(r==g==b for r,g,b,a in im.get_flattened_data() if a)
   if nine:im=ninepatch_like(im,oldim)
   p=OUT/'resources'/category/original.parent.name/original.name;p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
   files.append({'path':p.relative_to(OUT).as_posix(),'sha256':sha(p),'layer':config['layer'],'density':config['density'],'size':list(im.size),'source':original.relative_to(ROOT).as_posix(),'sourceSha256':sha(original),'ninePatchMetadataPreserved':nine})
  native=next(f for f in files if f['layer']=='cold' and f['density']=='mdpi');size=Image.open(OUT/native['path']).size
  if native['ninePatchMetadataPreserved']:size=(size[0]-2,size[1]-2)
  bank={name:raster(cache[name],160,texture) for name in LAYERS}
  before={name:raster(isolate(oldroot,name),160,texture) for name in LAYERS}
  comparisons[(category,key)]=(compose(before,'cold'),compose(bank,'cold'),compose(bank,'on'))
  for state in ['cold','on','focused_off','selected_focused','disabled','reduced_motion_on']:
   p=OUT/'previews/individual'/category/(key+'.'+state+'.preview.png');p.parent.mkdir(parents=True,exist_ok=True);compose(bank,state).save(p)
  rows.append({'id':key,'category':category,'sourceMaster':item['master'].relative_to(ROOT).as_posix(),'sourceMasterSha256':sha(item['master']),'master':dest.relative_to(OUT).as_posix(),'masterSha256':sha(dest),'textureViewport':item['viewport'],'pilotTreatmentReused':pilot_key,'nativeReviewSize':list(size),'layers':layernames,'files':files,'scope':'Artwork replacement bank; not installed or bound into native source.'})
  if at%10==0 or at==len(inputs):print(json.dumps({'completedMasters':at,'total':len(inputs)}),flush=True)
 # Additional vector parameter specimens use the same corrected border colors.
 borderrows=[]
 for p in sorted((ROOT/'iterations/23-magnification/masters').glob('border-*-parameter-example.svg')):
  doc=correct_material(E.parse(p).getroot(),'border');portable_links(doc,'../../source/steel-material.png');out=OUT/'masters/border-examples'/p.name;out.parent.mkdir(exist_ok=True);out.write_text(xml(doc),encoding='utf8')
  borderrows.append({'source':p.relative_to(ROOT).as_posix(),'sourceSha256':sha(p),'corrected':out.relative_to(OUT).as_posix(),'sha256':sha(out),'productionPngConfigurations':0})
 save_json(OUT/'border-appearance-examples.json',borderrows)
 # Alias the exact iteration27 duplicates without claiming 53 additional designs.
 aliases=[]
 for row in rows:
  if row['category']=='gallery':
   alias=ROOT/row['sourceMaster'].replace('26-gallery-workflows','27-gallery-contracts');assert sha(alias)==row['sourceMasterSha256']
   aliases.append({'sourceAlias':alias.relative_to(ROOT).as_posix(),'sameAs':row['sourceMaster'],'correctedMaster':row['master'],'configs':len(row['files'])})
 save_json(OUT/'gallery27-alias-map.json',aliases)
 compact_audit();border_patch()
 for p,digest in preserved.items():assert sha(ROOT/p)==digest,p
 save_json(OUT/'source/prior-master-preservation.json',preserved)
 save_json(OUT/'components.json',rows)
 save_json(OUT/'runtime-style.json',{'colors':COLORS,'states':STATES,'scope':'Static asset comparison only; original native feature/state owners unchanged','glowBakedIntoCold':False,'motion':'No new motion. Reduced-motion on is the same steady composition.'})
 # Every changed master is shown cold and on in the group sheets.
 sheet_index=[]
 for category in GROUPS:
  selected=[r for r in rows if r['category']==category]
  for batch in range(math.ceil(len(selected)/16)):
   chunk=selected[batch*16:(batch+1)*16];height=100+math.ceil(len(chunk)/4)*245
   board=Image.new('RGB',(1480,height),'#080c11');d=ImageDraw.Draw(board)
   d.text((24,16),category.upper()+' / CORRECTED FORGED STEEL',font=font(26,True),fill='#eee7d9')
   d.text((24,55),'Cold and separate ember layers / individual asset renders / native device validation pending',font=font(16),fill='#b5bdc6')
   for i,row in enumerate(chunk):
    x=20+(i%4)*370;y=95+(i//4)*245
    label=row['id'].removeprefix('cg_gl_').removeprefix('cg_sw_').removeprefix('cg_upd_').replace('_',' ')
    d.text((x,y),label,font=font(16,True),fill='#eee7d9')
    for j,im in enumerate(comparisons[(category,row['id'])][1:]):board.paste(im,(x+j*180,y+27),im)
    d.text((x,y+194),'COLD                         ON',font=font(14),fill='#b5bdc6')
    # Actual mdpi small-symbol strip; large art is explicitly scaled for this sheet.
    f=next(f for f in row['files'] if f['layer']=='cold' and f['density']=='mdpi');im=Image.open(OUT/f['path']);im.thumbnail((38,24));board.paste(im,(x,y+216),im)
    d.text((x+46,y+218),str(row['nativeReviewSize'][0])+'px source',font=font(12),fill='#8f9ba7')
   p=OUT/'previews'/f'{category}-{batch+1:02}.png';board.save(p);sheet_index.append(p.relative_to(OUT).as_posix())
 overview=[('setup','cg_sw_location'),('setup','cg_sw_datetime'),('setup','cg_sw_locale'),('magnification','close'),('magnification','settings_gear'),('updater','cg_upd_scan'),('updater','cg_upd_remote'),('gallery','cg_gl_media_frame'),('gallery','cg_gl_app_gallery'),('gallery','cg_gl_camera'),('gallery','cg_gl_ic_play_circle_filled'),('ayn','ayn_dot')]
 board=Image.new('RGB',(1320,1050),'#080c11');d=ImageDraw.Draw(board)
 d.text((24,16),'CRAFTAGEDDON / STYLE RECOVERY',font=font(30,True),fill='#eee7d9')
 d.text((24,58),'99 material treatments / representative BEFORE, COLD, ON samples / full group sheets included',font=font(18),fill='#b5bdc6')
 for i,key in enumerate(overview):
  x=24+(i%4)*330;y=110+(i//4)*295;d.text((x,y),key[1].removeprefix('cg_sw_').removeprefix('cg_gl_').removeprefix('cg_upd_').replace('_',' '),font=font(16,True),fill='#eee7d9')
  for j,im in enumerate(comparisons[key]):
   thumb=im.copy();thumb.thumbnail((96,170));board.paste(thumb,(x+j*104,y+40),thumb);d.text((x+j*104,y+214),['Before','Cold','On'][j],font=font(14),fill='#b5bdc6')
 d.text((24,1010),'Cold remains unlit. App-icon glow is a layer demonstration only. No hardware or native owners changed.',font=font(16),fill='#b5bdc6');board.save(OUT/'previews/recovery-overview.png')
 save_json(OUT/'preview-index.json',sheet_index)
 save_json(OUT/'verification/evidence/build-checks.json',{'result':'PASS','productionMasters':99,'priorMaterialDriftMasters':98,'additionalAynMarker':1,'additionalBorderExamples':3,'uniquePngConfigurations':sum(len(r['files']) for r in rows),'coldPngConfigurations':sum(f['layer']=='cold' for r in rows for f in r['files']),'neutralMaskConfigurations':sum(f['layer']!='cold' for r in rows for f in r['files']),'preservedEarlierMasters':len(preserved),'gallery27DuplicatedMastersNotDoubleCounted':53,'compactRecordsPreserved':183,'visualAcceptance':'PENDING','nativeDeviceRendering':'NOT RUN'})
 print(json.dumps({'masters':len(rows),'pngs':sum(len(r['files']) for r in rows),'sheets':len(sheet_index),'out':str(OUT)}),flush=True)

if __name__=='__main__':build()
