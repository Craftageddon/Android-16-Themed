"""Current production master inventory; optical treatments and copies stay explicit."""
from pathlib import Path
import argparse,hashlib,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
FOLDERS=['11-forge-symbol-library','12-forge-controls-and-screens','13-forge-android-and-thor-flows','14-forge-atmosphere','16-forge-motion','17-forge-coverage']
NS='{http://www.w3.org/2000/svg}'
def build(out):
 rows=[];copies=0
 for folder in FOLDERS:
  metadata_path=ROOT/'iterations'/folder/'components.json';metadata={r['id']:r for r in json.loads(metadata_path.read_text(encoding='utf8'))} if metadata_path.is_file() else {}
  for file in sorted((ROOT/'iterations'/folder/'masters').glob('*.svg')):
   doc=ET.parse(file).getroot();assert not doc.findall('.//'+NS+'text');size=[float(doc.get(k)) for k in ['width','height']];ids={n.get('id') for n in doc.findall(NS+'g')};assert {'cold','reflection','spill','seam','core','focus','symbol'}<=ids
   stem=file.stem;source=file.relative_to(ROOT).as_posix();digest=hashlib.sha256(file.read_bytes()).hexdigest();entry={'assetId':folder.split('-')[0]+'/'+stem,'semanticId':stem.split('__')[0],'optical':stem.split('__')[1] if '__' in stem else 'component','source':source,'sha256':digest,'size':size,'layers':['cold','reflection','spill','seam','core','focus','symbol'],'kind':metadata.get(stem,{}).get('type','scalable-frame' if stem.startswith('scalable-') else 'component'),'emissionLockedOff':metadata.get(stem,{}).get('emissionLockedOff',False),'sourceRole':'Current unlabelled production master','copies':[],'applicationIntegration':'NOT RUN','platformIntegration':'NOT RUN','deviceVerified':False}
   if folder.startswith('13-'):
    other=ROOT/'iterations/15-forge-journey-states/masters'/file.name;assert other.read_bytes()==file.read_bytes();entry['copies'].append({'source':other.relative_to(ROOT).as_posix(),'sha256':digest,'role':'Unchanged journey-state reuse; not another independent master'});copies+=1
   rows.append(entry)
 assert len(rows)==472,len(rows)
 report={'date':'2026-10-23','currentMasterFiles':len(rows),'namedUtilityAndSystemSymbols':164,'opticalSymbolMasters':328,'sculptedMotifs':9,'controlsAndPilotMasters':64,'scalableFrameMasters':4,'flowComponentMasters':18,'atmosphereAndWallpaperMasters':9,'motionComponentMasters':30,'appIdentityMasters':10,'reusedJourneyCopiesExcluded':copies,'sourceDirectories':FOLDERS,'scope':'Current authored production SVG inventory. Counts are source files, not 472 unrelated icon families or complete Android OS implementation. Historical captures, previews, density exports and portable copies are excluded.','masters':rows}
 (out/'canonical-masters.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='masters'}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();build(a.root.resolve())
