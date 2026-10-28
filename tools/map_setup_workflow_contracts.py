'''Map exact setup owners/resources and native acceptance gates before presentation changes.'''
from pathlib import Path
import collections,hashlib,re,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/28-setup-workflows';UP=OUT/'upstream/packages/apps/SetupWizard';A='{http://schemas.android.com/apk/res/android}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 sources=read_json(OUT/'source-manifest.json')
 for row in sources:
  data=(OUT/row['saved']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlobSha1']
 kotlin=[];refs=collections.defaultdict(list)
 for p in sorted((UP/'app/src/main/java').rglob('*.kt')):
  lines=p.read_text(encoding='utf8').splitlines();hits=[]
  for i,line in enumerate(lines):
   for kind,name in re.findall(r'\bR\.(layout|drawable|color|style|raw|xml|id|string)\.([A-Za-z0-9_]+)',line):
    row={'source':p.relative_to(UP).as_posix(),'line':i+1,'text':line.strip()};hits.append(dict(row,kind=kind,name=name));refs[(kind,name)].append(row)
  kotlin.append({'path':p.relative_to(UP).as_posix(),'sha256':sha(p),'resourceReferences':hits})
 resources=[]
 for p in sorted((UP/'app/src/main/res').rglob('*')):
  if not p.is_file():continue
  row={'path':p.relative_to(UP).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'qualifier':p.parent.name,'resource':p.stem,'semanticDecision':'PENDING - source map does not approve artwork or reuse'}
  if p.suffix=='.xml':
   n=E.parse(p).getroot();row.update(xmlRoot=n.tag,widgets=sorted({x.tag for x in n.iter()}),nativeIds=[x.get(A+'id') for x in n.iter() if x.get(A+'id')],nativeTextReferences=[v for x in n.iter() for k,v in x.attrib.items() if k in [A+'text',A+'contentDescription']])
  row['directCodeReferences']=refs.get((p.parent.name.split('-')[0],p.stem),[]);resources.append(row)
 ledger=read_json(ROOT/'iterations/27-gallery-contracts/semantic-family-ledger.json');families=[r for r in ledger if r['baselineFamily']['project']=='packages/apps/SetupWizard'];assert sum(r['decision']=='OPEN' for r in families)==56
 bp=(UP/'app/Android.bp').read_text(encoding='utf8');assert 'platform_apis: true' in bp and 'privileged: true' in bp
 gates=[{'area':'Native source/build','required':'Official platform API build for privileged LineageSetupWizard with SettingsLib, setupcompat, setupdesign, Lottie, SystemUISharedLib, Lineage internal and telephony-common. Public SDK core checks alone cannot establish complete app compatibility.','status':'NOT RUN'},{'area':'Actual source values','required':'SwitchItem.isChecked and MaterialSwitch.isChecked drive toggle ember. Theme/navigation checked groups drive selection. NextAllowed/enabled, focus/hover and generic loading do not imply on.','status':'OWNER PROOF MAPPED; IMPLEMENTATION PENDING'},{'area':'Live data/actions','required':'Keep wizard scripts/results, restored focus, locale and timezone data, permission/security/touch filtering, telephony/managed-profile/TV conditions, callbacks and settings/overlay operations in their original owners. Execute no setup action during artwork work.','status':'SOURCE CONTRACT MAPPED'},{'area':'Finish/reveal','required':'Keep RevealHoleView CLEAR compositing, wallpaper reveal, native animation/swipe/key state machine and alpha punch contract. Do not cover the reveal with opaque decoration.','status':'SOURCE CONTRACT MAPPED; PRESENTATION PENDING'},{'area':'Partner templates','required':'Inspect actual pinned Glif/Footer/Icon mixin source and partner overlay/theme behavior before binding custom textures or removing tints.','status':'DEPENDENCY REVIEW REQUIRED'},{'area':'Native target acceptance','required':'Native inflation/text, large fonts/scrolling, focus/controller, accessibility, rotation/dual display, effective overlays and independent final acceptance. Device explicitly deferred.','status':'NOT RUN'}]
 plan={'revision':'69174527a30bc72a28a5d55acdec8ce5edaba9e0','actualModule':'LineageSetupWizard','platformApis':True,'privilegedPlatformSigned':True,'sourceFilesHashVerified':len(sources),'productionKotlinOwners':len(kotlin),'baselineFamilies':len(families),'baselineFamiliesStillOpen':56,'nativeOwners':kotlin,'resources':resources,'acceptanceGates':gates,'newDiscoveredScope':['Actual external setupcompat/setupdesign templates and Lottie widget resources','SettingsLib/Material/Leanback and platform widget presentation dependencies','Theme preview includes native vector/JPEG artwork; new live labels and separate cold/light layering need a scoped composition','All three native Lottie resources need motion/content-preserving treatment; native motion completion not inferred from static masters'],'wholeGoalComplete':False}
 write_json(OUT/'source-owner-resource-map.json',plan)
 wip=read_json(OUT/'WORK-IN-PROGRESS.json');wip.update(sourceResourceAndAcceptanceMap='source-owner-resource-map.json',sourceOwnerMapping='39 production Kotlin owners mapped, privileged private-platform build distinguished from public core checks',baselineSetupFamilyDecisionsClosed=0);write_json(OUT/'WORK-IN-PROGRESS.json',wip)
 print({'pinnedFilesVerified':len(sources),'actualKotlinOwners':len(kotlin),'resourceFilesMapped':len(resources),'baselineSetupFamilies':len(families),'baselineSetupOpen':56,'platformApis':True,'nativeActionsExecuted':False})
if __name__=='__main__':main()
