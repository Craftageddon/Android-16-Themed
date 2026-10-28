'''Verify the scoped alias correction with actual library consumer declarations.'''
import hashlib,re,collections,xml.etree.ElementTree as E
from pathlib import Path
from audit_os_resource_coverage import ROOT,read_json,write_json
BASE=ROOT/'iterations/26-gallery-workflows';OUT=ROOT/'iterations/27-gallery-contracts';RES=OUT/'native-patch/packages/apps/Glimpse/app/src/main/res';SRC=OUT/'source/media3-ui/original-resources/res';JAVA=OUT/'source/media3-ui/original-java/androidx/media3/ui'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 original={n.get('name'):n.text.removeprefix('@drawable/') for n in E.parse(SRC/'values/values.xml').getroot() if n.tag=='drawable'}
 scoped={n.get('name'):n.text.removeprefix('@drawable/') for n in E.parse(RES/'values/cg_gallery_media3_aliases.xml').getroot() if n.tag=='drawable'}
 assert len(scoped)==23 and all(n.startswith('exo_styled_controls_') for n in scoped)
 old_overrides={r['resource'] for r in read_json(BASE/'gallery-resource-bindings.json') if r.get('library')}
 new_bridges={r['resource'] for r in read_json(OUT/'gallery-resource-bindings.json') if r.get('library')}
 aliases=dict(original);aliases.update(scoped)
 def resolve(name,table):
  path=[name]
  while name in table:
   name=table[name];assert name not in path;path.append(name)
  return name,path
 consumers=[];shared_before=[]
 for name in sorted(original):
  if not name.startswith(('exo_notification_','exo_legacy_controls_')):continue
  before,_=resolve(name,original);after,chain=resolve(name,aliases);assert after==before and after not in new_bridges
  files=sorted(SRC.glob('drawable*/'+after+'.*'));assert files,name
  hashes=[{'path':p.relative_to(OUT).as_posix(),'sha256':sha(p)} for p in files]
  owner='PlayerNotificationManager.java' if name.startswith('exo_notification_') else 'LegacyPlayerControlView.java'
  lines=(JAVA/owner).read_text(encoding='utf8').splitlines();matches=[{'line':i+1,'text':s.strip()} for i,s in enumerate(lines) if name in s]
  # Legacy static icons also bind through their original source layout/style IDs.
  refs=[]
  if not matches:
   for p in SRC.rglob('*.xml'):
    if name in p.read_text(encoding='utf8'):refs.append({'path':p.relative_to(OUT).as_posix(),'sha256':sha(p)})
  assert matches or refs,name
  consumers.append({'alias':name,'sourceAlias':original[name],'effectiveChain':chain,'originalLeavesBytePreserved':hashes,'consumerSource':{'path':(JAVA/owner).relative_to(OUT).as_posix(),'sha256':sha(JAVA/owner),'references':matches,'layoutOrStyleReferences':refs},'decision':'PRESERVE_NATIVE_SHARED_CONSUMER_CONTRACT','sourceReviewed':True,'nativeRuntimeAcceptance':'NOT RUN'})
  if before in old_overrides:shared_before.append(name)
 for name,target in scoped.items():
  final,_=resolve(name,aliases);assert final==target and target in new_bridges
  p=next(RES.glob('drawable*/'+target+'.xml'));assert E.parse(p).getroot().get('class')=='org.lineageos.glimpse.forge.ForgeDrawable'
 for old in old_overrides:assert not list(RES.glob('drawable*/'+old+'.xml')),old
 pn=0
 for p in RES.rglob('*.png'):
  prior=BASE/'native-patch/packages/apps/Glimpse/app/src/main/res'/p.relative_to(RES);assert sha(p)==sha(prior);pn+=1
 assert pn==1680
 source_rows=[]
 for r in read_json(OUT/'source/media3-ui-contract.json')['members']:
  assert sha(OUT/r['saved'])==r['sha256'];source_rows.append(r)
 write_json(OUT/'source/shared-media3-consumer-review.json',{'nativeConsumers':consumers,'sharedAliasesAffectedByForge26LeafOverrides':shared_before,'currentPlayerAliasesRetargeted':scoped,'nativeOtherConsumerAliasesPreserved':len(consumers),'sourceMembersVerified':len(source_rows),'nativePngConfigurationsUnchanged':pn,'result':'PASS','wholeGoalComplete':False})
 evidence=OUT/'verification/evidence';evidence.mkdir(parents=True,exist_ok=True)
 write_json(evidence/'shared-alias-checks.json',{'result':'PASS','styledAliasesScoped':len(scoped),'legacyAndNotificationAliasesPreserved':len(consumers),'oldSharedOverridesRemoved':len(old_overrides),'priorCrossConsumerEffectsCorrected':len(shared_before),'unchangedPngConfigurations':pn,'actualKotlinOwnersCompiled':read_json(OUT/'verification/evidence/complete-owner-compilation.json')['actualKotlinSources'] if (OUT/'verification/evidence/complete-owner-compilation.json').exists() else 'NOT RUN','nativeXmlInflation':'NOT RUN','fullSoongBuild':'NOT RUN','wholeGoalComplete':False})
 print({'playerAliasesScoped':len(scoped),'nativeOtherConsumerAliasesPreserved':len(consumers),'crossConsumerEffectsCorrected':len(shared_before),'productionPngChanges':0})
if __name__=='__main__':main()
