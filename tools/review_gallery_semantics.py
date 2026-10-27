'''Content-backed Gallery review delta; conserve every original family/variant.'''
import copy,collections,hashlib,xml.etree.ElementTree as E
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/26-gallery-workflows';UP=OUT/'upstream/packages/apps/Glimpse';PATCH=OUT/'native-patch/packages/apps/Glimpse'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (OUT/'complete-assets.zip').exists()
 ledger=read_json(ROOT/'iterations/25-updater-workflows/semantic-family-ledger.json');old=copy.deepcopy(ledger)
 bindings={r['resource']:r for r in read_json(OUT/'gallery-resource-bindings.json') if 'familyId' in r}
 sources={r['path']:r for r in read_json(OUT/'source-manifest.json')}
 graph=[r for r in read_json(ROOT/'iterations/22-native-contract-review/resource-reference-graph.json') if r['project']=='packages/apps/Glimpse']
 declarations=read_json(ROOT/'iterations/22-native-contract-review/resource-declarations.json')
 deltas=[];remaining=[];reaffirm=[]
 for r in ledger:
  b=r['baselineFamily']
  if b['project']!='packages/apps/Glimpse':continue
  path=b['examplePath'];source=sources[path];assert sha(UP/path)==source['sha256'];node=E.fromstring((UP/path).read_bytes());name=b['name']
  if r['decision']!='OPEN':
   reaffirm.append({'familyId':r['familyId'],'existingDecision':r['decision'],'resource':name,'newNativeBinding':bindings.get(name),'nativeAcceptance':'NOT RUN'});continue
  reason='';decision=''
  if name in ['ic_launcher_background','ic_launcher_foreground']:
   remaining.append({'familyId':r['familyId'],'resource':name,'reason':'Original legacy leaves retained after rebinding the adaptive owner. Repository/downstream consumer and reuse disposition still require review; absence from the new owner is not approval.'});continue
  if name in bindings:
   binding=bindings[name];decision='OWNER_PRESENTATION_ADAPTATION_AUTHORED';reason='Exact source glyph geometry/role reviewed with an authored material treatment and qualified native leaf bridge. True/false value leaves use explicit source-value mode; semantic/offline acceptance only.'
   if name=='ic_star_border':reason='Empty favorite value uses the reviewed outline favorite donor, cold-only source-value mode, and original selected-state selector. Original glyph source and donor hashes retained.'
  elif name in ['bg_media_viewer_top_sheet','bg_media_viewer_bottom_sheet']:
   decision='OWNER_PRESENTATION_ADAPTATION_AUTHORED';reason='Original viewer sheet owner gets a scoped layered steel housing. Existing fade, fullscreen, insets and constrained measured-height consumers remain source-owned.'
  elif name=='bg_thumbnail':
   assert node.find('corners').get('{http://schemas.android.com/apk/res/android}radius')=='4dp';decision='PRESERVE_NATIVE_REFERENCE_CONTRACT';reason='Original four-dp rectangle defines ImageView.clipToOutline geometry. Keep it byte-identical; a separate transparent foreground carries selected steel/ember without replacing photo clipping or content.'
  elif name=='thumbnail_placeholder':
   assert node.find('.//solid').get('{http://schemas.android.com/apk/res/android}color')=='?attr/colorSurfaceContainer';decision='PRESERVE_EMPTY_SLOT';reason='Real Glide loading placeholder is a solid theme surface, not a missing illustration. Preserve the native load/fallback contract; the scoped fixed dark palette supplies its color.'
  elif name=='settingslib_switch_thumb_icon' and b['kind']=='color':
   assert node.tag=='selector';decision='PRESERVE_NATIVE_REFERENCE_CONTRACT';reason='Keep the typed checked color selector and original SettingsLib style contract. New ForgeMaterialSwitch explicitly clears the native thumb decoration/tint before installing independent cold/mask layers; no global selector replacement.'
  elif name=='ic_launcher_monochrome':
   decision='OWNER_PRESENTATION_ADAPTATION_AUTHORED';reason='New neutral photo-and-round-housing vector matches the new app identity. The adaptive monochrome child remains a platform-tinted mask; do not bake ember or cold texture into that system contract.'
  elif b['kind']=='layout':
   if (PATCH/path).exists():decision='OWNER_PRESENTATION_ADAPTATION_AUTHORED';reason='Reviewed native IDs, widget and event owners; scoped presentation edits retain original data/action contracts. Edit receipts reverse byte-for-byte to the pinned inputs. No native layout acceptance claimed.'
   else:decision='PRESERVE_NATIVE_REFERENCE_CONTRACT';reason='Reviewed the actual layout contents and scoped resource references. Retain native containers, data text, grid/navigation wiring and accessibility roles; referenced glyphs, descendant frames and the activity palette are adapted in their own owners. Unreviewed referenced families remain separately open.'
  elif name=='attrs_ListItem':
   assert node.find('declare-styleable').get('name')=='ListItem';decision='PRESERVE_BUILD_CONTRACT';reason='Typed native custom-attribute declarations are consumed by ListItem inflation and metadata bindings. Preserve names, formats and generated styleable ordering; artwork does not replace an attribute schema.'
  elif name=='colors':
   assert all(e.text=='@android:color/transparent' for e in node if e.tag=='color');decision='PRESERVE_NATIVE_REFERENCE_CONTRACT';reason='Both real Media3 overrides remove overlays from the photo/video surface. Keep transparent values intact; player steel belongs only to compact control housings.'
  elif name in ['themes','themes_settingslib']:
   decision='OWNER_PRESENTATION_ADAPTATION_AUTHORED';reason='Exact native activity/style owners receive a fixed English-compatible dark palette and scoped control resources. Typed style inheritance and remaining dimensions/behavior stay native; no blanket drawable substitution.'
  elif name=='config':
   value=node.find('string');assert value.get('name')=='config_systemGallery' and value.text=='org.lineageos.glimpse';decision='PRESERVE_BUILD_CONTRACT';reason='System gallery role package string in the framework RRO is a native role-binding contract. It is not an illustration or a visible caption; retain the exact package identity.'
  else:raise AssertionError((b['kind'],name))
  owners=[x for x in graph if any(declarations[c]['path']==path and declarations[c]['project']=='packages/apps/Glimpse' for c in x.get('candidates',[])) or x['path']==path]
  proof={'source':source,'xmlRoot':node.tag,'scopedReferenceEvidenceCount':len(owners),'scopedReferences':owners,'nativeBinding':bindings.get(name),'patchedPath':path if (PATCH/path).exists() else None,'patchedSha256':sha(PATCH/path) if (PATCH/path).exists() else None,'decisionKept':decision,'nativeDropInApproval':False,'fullSoongOrDeviceAcceptance':'NOT RUN','wholeGoalComplete':False}
  r['decision']=decision;r['requiredAction']='Complete full native resource/owner build, inflation, accessibility and target acceptance; this semantic decision does not close those gates.';r['rationale']=reason;r['forge26Review']=proof
  deltas.append({'familyId':r['familyId'],'previousDecision':'OPEN','decision':decision,'source':b,'rationale':reason,'evidence':proof})
 assert len(ledger)==10926 and sum(r['baselineFamily']['variants'] for r in ledger)==16559
 assert {r['familyId'] for r in ledger}=={r['familyId'] for r in old}
 for before,after in zip(old,ledger):assert before['baselineFamily']==after['baselineFamily']
 counts=dict(collections.Counter(r['decision'] for r in ledger));assert len(deltas)==47 and counts['OPEN']==9577
 write_json(OUT/'semantic-family-ledger.json',ledger);write_json(OUT/'semantic-review-delta.json',deltas);write_json(OUT/'gallery-existing-decisions-reaffirmed.json',reaffirm)
 write_json(OUT/'semantic-review-progress.json',{'date':'2026-10-27','familyRecords':10926,'sourceFileVariants':16559,'previousOpenFamilyDecisions':9624,'newContentBackedDecisions':len(deltas),'openFamilyDecisions':counts['OPEN'],'decisions':counts,'previouslyAuthoredWorkflowGroups':['W-01','W-02','W-06'],'partiallyAuthoredWorkflowGroups':['W-04','W-05'],'unauthoredWorkflowGroups':['W-03','W-07'],'incompleteWorkflowGroups':['W-03','W-04','W-05','W-07'],'remainingGalleryFamilyReviews':remaining,'wholeSemanticReviewFinished':False,'wholeGoalComplete':False,'finalWholeGoalDoubleCheck':'NOT RUN - all required scope must be complete first'})
 write_json(OUT/'gallery-family-review.json',{'baselineGalleryFamilies':63,'newDecisions':47,'existingDecisionsReaffirmed':len(reaffirm),'remainingOpen':remaining,'newDependencyScope':'Media3 dependency drawings/layouts are separate discoveries beyond the original baseline; they are not silently added to or closed in the 10926-family ledger.'})
 print({'contentBackedDecisions':len(deltas),'openFamilies':counts['OPEN'],'complete':False})
if __name__=='__main__':main()
