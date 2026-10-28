'''Record the two authored original icon leaves without changing the baseline corpus.'''
import collections,copy,hashlib
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/27-gallery-contracts';BASE=ROOT/'iterations/26-gallery-workflows'
def main():
 checks=read_json(OUT/'verification/evidence/compiled-gallery-contracts.json');assert checks['result']=='PASS' and checks['explicitAdaptiveIntrinsicDp']==108 and checks['adaptiveSafeCircleAlphaPixels']>0
 ledger=read_json(BASE/'semantic-family-ledger.json');old=copy.deepcopy(ledger);identity=read_json(OUT/'source/legacy-gallery-identity-rework.json');leaves={r['path']:r for r in identity['sourceLeaves']};delta=[]
 for row in ledger:
  b=row['baselineFamily']
  if b['project']!='packages/apps/Glimpse' or row['decision']!='OPEN':continue
  assert b['name'] in ['ic_launcher_background','ic_launcher_foreground'];assert b['examplePath'] in leaves
  proof=leaves[b['examplePath']];assert hashlib.sha256((OUT/'upstream/packages/apps/Glimpse'/proof['path']).read_bytes()).hexdigest()==proof['originalSha256']
  row['decision']='OWNER_PRESENTATION_ADAPTATION_AUTHORED';row['rationale']='Original108dp landscape/aperture leaves are reworked in their actual retained adaptive child names: opaque dark field plus the approved cold steel photo badge, with explicit108dp foreground bounds and20percent safe inset. Original composition and source hashes are retained; this is an active leaf adaptation, not retirement by absence.';row['requiredAction']='Complete full official Soong build, native Drawable inflation/launcher masking, installed overlay and target acceptance. This source/art decision does not close those gates.';row['forge27Review']={'sourceLeaf':proof,'actualAdaptiveOwner':'app/src/main/res/mipmap-anydpi/ic_launcher.xml','resourceLink':'verification/evidence/full-resource-link.json','compiledContracts':'verification/evidence/compiled-gallery-contracts.json','originalSourcesPreserved':True,'runtimeOrDeviceAcceptance':'NOT RUN','wholeGoalComplete':False};delta.append({'familyId':row['familyId'],'previousDecision':'OPEN','decision':row['decision'],'source':b,'rationale':row['rationale'],'evidence':row['forge27Review']})
 assert len(delta)==2 and len(ledger)==10926 and sum(r['baselineFamily']['variants'] for r in ledger)==16559
 for before,after in zip(old,ledger):assert before['familyId']==after['familyId'] and before['baselineFamily']==after['baselineFamily']
 counts=dict(collections.Counter(r['decision'] for r in ledger));assert counts['OPEN']==9575
 progress=read_json(BASE/'semantic-review-progress.json');progress.update(date='2026-10-28',previousOpenFamilyDecisions=9577,newContentBackedDecisions=2,openFamilyDecisions=9575,decisions=counts,remainingGalleryFamilyReviews=[],wholeSemanticReviewFinished=False,wholeGoalComplete=False,finalWholeGoalDoubleCheck='NOT RUN - all required scope must be complete first')
 write_json(OUT/'semantic-family-ledger.json',ledger);write_json(OUT/'semantic-review-delta.json',delta);write_json(OUT/'semantic-review-progress.json',progress);write_json(OUT/'gallery-family-review.json',{'baselineGalleryFamilies':63,'previousDecisionsRetained':61,'newDecisions':2,'remainingOriginalGalleryFamilyReviews':0,'dependencyScope':'Separate discovered families remain open; baseline decisions do not constitute whole Gallery visual acceptance.','wholeGoalComplete':False});print({'newContentBackedDecisions':2,'openBaselineFamilies':9575,'conservedFamilies':10926,'conservedVariants':16559})
if __name__=='__main__':main()
