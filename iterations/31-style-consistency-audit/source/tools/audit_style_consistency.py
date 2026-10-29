"""Repeatable whole-authored-catalog style audit with explicit recovery precedence."""
from pathlib import Path
import collections,copy,hashlib,json,unicodedata,xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'iterations/31-style-consistency-audit'
N='{http://www.w3.org/2000/svg}'
EXPECTED={'reflection':'#dc5920','spill':'#ff4908','seam':'#ff5b0b','core':'#ffd083','focus':'#d5e7f2','symbol':'#ffe5bc'}
BAD_STOPS={'#c9d0d6','#71808f','#ced7de','#8fa4b5','#bfcdd8','#cbd4d9','#b8c0c4'}
THUMB_SOURCE='iterations/12-forge-controls-and-screens/masters/control-scrollbar.svg'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2)+'\n',encoding='utf8')
def active():
 canonical=json.loads((ROOT/'iterations/17-forge-coverage/canonical-masters.json').read_text())['masters']
 records={r['source']:{'source':r['source'],'kind':r['kind'],'optical':r.get('optical')} for r in canonical}
 for i in range(20,29):
  folder=next((ROOT/'iterations').glob(str(i)+'-*'))
  for p in (folder/'masters').rglob('*.svg'):
   if 'original-donors' in p.parts:continue
   s=p.relative_to(ROOT).as_posix();records[s]={'source':s,'kind':'later-master','optical':'compact' if '__compact' in p.name else None}
 # The semantic review also authors app identities and correction glyphs outside
 # its top-level masters directory. Approved reuse copies retain their own roles.
 semantic=ROOT/'iterations/20-semantic-review'
 extra=list((semantic/'app-masters').glob('*.svg'))+list((semantic/'review-corrections/masters').glob('*.svg'))+list((semantic/'approved-reuse').rglob('masters/*.svg'))
 for p in extra:
  s=p.relative_to(ROOT).as_posix();records[s]={'source':s,'kind':'app-identity' if p.parent.name=='app-masters' else 'semantic-review-master','optical':'compact' if '__compact' in p.name else None}
 recovery=ROOT/'iterations/30-reference-style-recovery';over={}
 for row in json.loads((recovery/'components.json').read_text()):
  over[row['sourceMaster']]=recovery/row['master']
  if row['category']=='gallery':over[row['sourceMaster'].replace('26-gallery-workflows','27-gallery-contracts')]=recovery/row['master']
 for row in json.loads((recovery/'border-appearance-examples.json').read_text()):over[row['source']]=recovery/row['corrected']
 correction=OUT/'masters/control-scrollbar.svg'
 if correction.exists():over[THUMB_SOURCE]=correction
 for source,row in records.items():row['effective']=over.get(source,ROOT/source).relative_to(ROOT).as_posix()
 return list(records.values())

def run():
 assert not (OUT/'complete-assets.zip').exists(),'Frozen audit: use a new review folder.'
 rows=active();defects=[];indicator_marks=[];all_layers=collections.Counter();text_count=0;embedded_images=[];mask_definitions=0;cold_gradients=0
 for row in rows:
  p=ROOT/row['effective'];root=E.parse(p).getroot();row['sourceSha256']=sha(ROOT/row['source']);row['effectiveSha256']=sha(p)
  cold=root.find(N+"g[@id='cold']")
  if cold is None:defects.append({'source':row['source'],'issue':'No cold layer'});continue
  # Check used cold gradients rather than a whole-file color search.
  referenced={v[5:-1] for n in cold.iter() for v in n.attrib.values() if v.startswith('url(#') and v.endswith(')')}
  for gradient in root.findall('.//'+N+'linearGradient'):
   if gradient.get('id') in referenced:
    cold_gradients+=1
    colors={s.get('stop-color','').lower() for s in gradient}
    if colors&BAD_STOPS:defects.append({'source':row['source'],'issue':'Active cold silver gradient','colors':sorted(colors&BAD_STOPS)})
    # A broader brightness test catches unlisted pale neutral gradients too.
    for color in colors:
     if color.startswith('#') and len(color)==7:
      values=[int(color[i:i+2],16) for i in (1,3,5)]
      if min(values)>155 and max(values)-min(values)<50:defects.append({'source':row['source'],'issue':'Additional pale neutral cold gradient','color':color})
  for node in cold.iter():
   if node.get('fill')=='url(#edge)' and node.get('stroke') is None:
    defects.append({'source':row['source'],'issue':'Untextured standalone edge-gradient surface','path':node.get('d')})
   if node.get('stroke')=='url(#forged)' and node.get('opacity') in ['.14','0.14']:
    defects.append({'source':row['source'],'issue':'Suppressed forged texture coat'})
   if any(node.get(a,'').lower() in ['#bdc4c8','#d0d8df','#c6d2db','#b7c7d3'] for a in ['fill','stroke']):
    indicator_marks.append({'source':row['source'],'tag':node.tag.split('}')[-1],'role':'Persistent semantic/value/contrast mark; not a broad steel face','optical':row['optical']})
  for layer in root.findall(N+'g'):
   name=layer.get('id','');all_layers[name]+=1
   if name in ['reflection','spill','seam','core','focus','symbol','motion']:
    if 'display:none' not in layer.get('style','').replace(' ',''):defects.append({'source':row['source'],'issue':'Light/mask layer visible in default master','layer':name})
    for node in layer.iter():
     for a in ['fill','stroke']:
      color=node.get(a,'')
      if color and color.lower() not in ['none','white','black','#fff','#ffffff','#000','#000000'] and not color.startswith('url('):defects.append({'source':row['source'],'issue':'Non-neutral mask paint','layer':name,'color':color})
    # Resolve referenced gradients, filters and clips rather than exempting url().
    definitions={n.get('id'):n for n in root.iter() if n.get('id')}
    queue=[v[5:-1] for n in layer.iter() for v in n.attrib.values() if v.startswith('url(#') and v.endswith(')')];seen=set()
    while queue:
     key=queue.pop()
     if key in seen:continue
     seen.add(key);target=definitions.get(key);mask_definitions+=1
     if target is None:defects.append({'source':row['source'],'issue':'Missing mask definition','id':key});continue
     for node in target.iter():
      for attr in ['fill','stroke','stop-color','flood-color']:
       value=node.get(attr,'')
       if value.startswith('url(#'):queue.append(value[5:-1])
       elif value and value.lower() not in ['none','white','black','#fff','#ffffff','#000','#000000']:defects.append({'source':row['source'],'issue':'Non-neutral referenced mask paint','id':key,'color':value})
  for text in root.findall('.//'+N+'text'):
   text_count+=1
   if any(unicodedata.category(c).startswith('L') and ord(c)>127 for c in ''.join(text.itertext())):defects.append({'source':row['source'],'issue':'Non-English alphabet in visible text'})
  for image in root.findall('.//'+N+'image'):
   href=image.get('href','')
   if not href.startswith('data:'):
    target=(p.parent/href).resolve()
    if not target.exists():defects.append({'source':row['source'],'issue':'Missing linked material/image','href':href})
    else:embedded_images.append({'path':target.relative_to(ROOT).as_posix(),'sha256':sha(target)})
 # Revalidate the canonical/portable catalog evidence used for visual review.
 catalog=ROOT/'iterations/17-forge-coverage';manifest=json.loads((catalog/'current-library/manifest.json').read_text())
 for row in manifest['masters']:
  assert sha(ROOT/row['source'])==row['sha256']
  assert sha(catalog/row['portableMaster'])==row['portableSha256']
 for raster in manifest['rasters']:assert sha(catalog/raster['path'])==raster['sha256']
 compositions=json.loads((catalog/'current-library/compositions.json').read_text())['compositions']
 for row in compositions:
  assert sha(ROOT/row['original'])==row['originalSha256']
  assert sha(catalog/row['portable'])==row['portableSha256']
  doc=E.parse(catalog/row['portable']).getroot()
  for node in doc.findall('.//'+N+'text'):
   if any(unicodedata.category(c).startswith('L') and ord(c)>127 for c in ''.join(node.itertext())):defects.append({'source':row['original'],'issue':'Non-English alphabet in review label'})
 # Exact palette and idle/disabled state contract in every relevant current style file.
 styles=[]
 for i in [11,12,13,14,17,20,23,25,26,28,29,30]:
  folder=next((ROOT/'iterations').glob(str(i)+'-*'));p=folder/'runtime-style.json'
  if not p.exists():continue
  obj=json.loads(p.read_text());colors=obj.get('colors')
  if colors is not None:
   if colors!=EXPECTED:defects.append({'source':p.relative_to(ROOT).as_posix(),'issue':'Runtime palette differs','colors':colors})
  styles.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'mainPalette':colors})
 # Fresh integrity of the complete latest recovery, not old PASS text.
 bank=ROOT/'iterations/30-reference-style-recovery';integrity=json.loads((bank/'ARTIFACTS.json').read_text())
 for file,digest in integrity.items():assert sha(bank/file)==digest,file
 effective_hashes={r['effectiveSha256'] for r in rows}
 summary={'result':'PASS' if not defects else 'FINDINGS','activeSourceRecords':len(rows),'distinctEffectiveMasterContents':len(effective_hashes),'canonicalRecordsVerified':len(manifest['masters']),'canonicalPortableImagesVerified':len(manifest['rasters']),'earlierScreenCompositionsHashVerified':len(compositions),'latestRecoveryArtifactsFreshlyRehashed':len(integrity),'mainPaletteFilesChecked':len(styles),'activeColdLinearGradientsChecked':cold_gradients,'resolvedMaskDefinitionsChecked':mask_definitions,'directAndReferencedMaskPaintsNeutral':not any('mask paint' in d['issue'] for d in defects),'visibleMasterTextNodes':text_count,'remainingDefects':len(defects),'sourceLevelOnly':True,'nativeTintContrastAndTargetDeviceAcceptance':'NOT RUN','historicalSupersededMastersAreNotCountedAsNewFailures':True}
 write(OUT/'audit/active-source-index.json',rows);write(OUT/'audit/structural-and-palette-findings.json',defects)
 write(OUT/'audit/indicator-role-exceptions.json',indicator_marks);write(OUT/'audit/material-image-evidence.json',embedded_images);write(OUT/'audit/palette-file-evidence.json',styles);write(OUT/'audit/summary.json',summary)
 print(json.dumps(summary),flush=True)

if __name__=='__main__':run()
