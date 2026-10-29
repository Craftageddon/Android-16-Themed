"""Reopen and verify saved correction outputs independently of the authoring loop."""
from pathlib import Path
import hashlib,json,unicodedata,xml.etree.ElementTree as E
from PIL import Image,ImageChops
from build_scalable_frames import bounds,stretch

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'iterations/30-reference-style-recovery'
NS='{http://www.w3.org/2000/svg}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 rows=json.loads((OUT/'components.json').read_text());assert len(rows)==99
 banned=['#c9d0d6','#71808f','#ced7de','#8fa4b5','#bfcdd8','#b8c0c4','#cbd4d9']
 configs=0;neutral=0;nine=0;geometry=0;source_hashes={};source_hashes.update(json.loads((OUT/'source/prior-master-preservation.json').read_text()))
 for row in rows:
  master=OUT/row['master'];assert sha(master)==row['masterSha256'];doc=E.parse(master).getroot()
  assert not doc.findall('.//'+NS+'text'),master
  assert not any(c in master.read_text().lower() for c in banned),master
  original=E.parse(ROOT/row['sourceMaster']).getroot();source_hashes[row['sourceMaster']]=row['sourceMasterSha256']
  if not row['pilotTreatmentReused']:
   before=[n.get('d') for n in original.find(NS+"g[@id='cold']").iter(NS+'path')]
   after=[n.get('d') for n in doc.find(NS+"g[@id='cold']").iter(NS+'path')]
   assert before==after,row['id'];geometry+=1
  assert doc.get('width')==original.get('width') and doc.get('height')==original.get('height'),row['id']
  for node in doc.findall('.//'+NS+'image'):
   p=(master.parent/node.get('href')).resolve();assert p.is_relative_to(OUT.resolve()) and p.exists()
  for f in row['files']:
   p=OUT/f['path'];assert sha(p)==f['sha256'];im=Image.open(p);im.load();assert im.mode=='RGBA' and list(im.size)==f['size']
   orig=Image.open(ROOT/f['source']).convert('RGBA');assert im.size==orig.size
   source_hashes[f['source']]=f['sourceSha256'];configs+=1
   content=im
   if f['ninePatchMetadataPreserved']:
    for box in [(0,0,im.width,1),(0,im.height-1,im.width,im.height),(0,0,1,im.height),(im.width-1,0,im.width,im.height)]:assert im.crop(box).tobytes()==orig.crop(box).tobytes()
    (x0,x1),(y0,y1)=bounds(im);content=im.crop((1,1,im.width-1,im.height-1))
    for w,h in [(content.width*2,content.height*2),(content.width*3,content.height*2),(content.width*2,content.height*3)]:
     expanded=stretch(im,(w,h));assert expanded.size==(w,h)
     assert expanded.crop((0,0,x0,y0)).tobytes()==content.crop((0,0,x0,y0)).tobytes()
    nine+=1
   assert content.getchannel('A').getextrema()[0]==0,p
   if f['layer']!='cold':
    r,g,b,a=content.split();assert ImageChops.difference(r,g).getbbox() is None and ImageChops.difference(g,b).getbbox() is None,p;neutral+=1
  for name in ['cold','on','focused_off','selected_focused','disabled','reduced_motion_on']:
   p=OUT/'previews/individual'/row['category']/(row['id']+'.'+name+'.preview.png');Image.open(p).verify()
  a=OUT/'previews/individual'/row['category']/(row['id']+'.on.preview.png');b=a.with_name(row['id']+'.reduced_motion_on.preview.png');assert a.read_bytes()==b.read_bytes()
 for p,digest in source_hashes.items():assert sha(ROOT/p)==digest,p
 state=json.loads((OUT/'runtime-style.json').read_text())['states']
 assert state['cold']==state['pressed_off']
 for key in ['cold','focused_off','pressed_off','disabled']:assert state[key][1:5]==[0,0,0,0]
 assert state['reduced_motion_on']==state['on']
 texts=0;fixtures=0
 for p in (OUT/'workflow-review').rglob('workflow-previews/*.svg'):
  doc=E.parse(p).getroot();fixtures+=1
  for t in doc.findall('.//'+NS+'text'):
   for c in ''.join(t.itertext()):assert not (unicodedata.category(c).startswith('L') and ord(c)>127),(p,c)
   texts+=1
 assert fixtures==71,fixtures
 audit=json.loads((OUT/'compact-mask-role-audit.json').read_text());assert audit['records']==183 and audit['distinctCompactContents']==181 and len(audit['mappings'])==183
 for v in audit['mappings']:
  assert sha(ROOT/v['compact'])==v['compactSha256'] and sha(ROOT/v['detailedCounterpart'])==v['detailedSha256']
 assert configs==2895 and neutral==2482 and nine==28,(configs,neutral,nine)
 result={'result':'PASS','reopenedPngConfigurations':configs,'neutralGrayscaleMasks':neutral,'coldConfigurations':configs-neutral,'ninePatchConfigurationsWithIdenticalMetadataAndThreeStretchChecks':nine,'genericMastersWithIdenticalColdPathData':geometry,'pilotMastersWithDocumentedDecorationChanges':4,'unchangedEarlierSourcesRehashed':len(source_hashes),'refreshedEditableWorkflowSpecimens':fixtures,'EnglishTextNodesChecked':texts,'compactRecordsAndDetailedCounterpartsPreserved':183,'finalUserVisualAcceptance':'PENDING','independentTargetRendererAndDeviceValidation':'NOT RUN','nativeBorderProposalCompile':'NOT RUN','releaseFinalized':False}
 dest=OUT/'verification/evidence/saved-output-checks.json';dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result))

if __name__=='__main__':verify()
