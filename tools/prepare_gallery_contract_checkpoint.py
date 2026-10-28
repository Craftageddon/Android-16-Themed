'''Prepare complete and incremental Gallery patches plus bounded checkpoint documentation.'''
from pathlib import Path
import collections,datetime,difflib,hashlib,shutil,subprocess
from audit_os_resource_coverage import ROOT,read_json,write_json
BASE=ROOT/'iterations/26-gallery-workflows';OUT=ROOT/'iterations/27-gallery-contracts';UP=OUT/'upstream/packages/apps/Glimpse';PATCH=OUT/'native-patch/packages/apps/Glimpse'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files(root):return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file()}
def effective(patch):return files(UP)|files(patch)
def makepatch(before,after,name):
 lines=[];changed=[]
 for rel in sorted(before.keys()|after.keys()):
  old=before[rel].read_bytes() if rel in before else b'';new=after[rel].read_bytes() if rel in after else b''
  if old==new:continue
  if Path(rel).suffix=='.png':continue
  oldtext=old.decode('utf8');newtext=new.decode('utf8')
  for line in difflib.unified_diff(oldtext.splitlines(keepends=True),newtext.splitlines(keepends=True),fromfile='a/'+rel if rel in before else '/dev/null',tofile='b/'+rel if rel in after else '/dev/null'):
   lines.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
  changed.append({'path':rel,'beforeSha256':hashlib.sha256(old).hexdigest() if rel in before else None,'afterSha256':hashlib.sha256(new).hexdigest() if rel in after else None,'deleted':rel not in after})
 patch=OUT/name;patch.write_bytes(''.join(lines).encode('utf8'))
 work=ROOT/'build-work'/('gallery27-apply-'+Path(name).stem+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'));work.mkdir(parents=True);(work/'.gitattributes').write_bytes(b'* -text\n')
 for row in changed:
  if row['path'] in before:
   dest=work/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(before[row['path']].read_bytes())
 commands=[]
 for args in [['git','-c','core.bare=false','init','-q'],['git','-c','core.bare=false','-c','core.autocrlf=false','apply','--check','--whitespace=nowarn',str(patch)],['git','-c','core.bare=false','-c','core.autocrlf=false','apply','--whitespace=nowarn',str(patch)]]:
  p=subprocess.run(args,cwd=work,capture_output=True,text=True);commands.append({'command':args,'exitCode':p.returncode,'output':p.stdout+p.stderr});assert p.returncode==0,commands[-1]
 for row in changed:
  p=work/row['path']
  if row['deleted']:assert not p.exists()
  else:assert sha(p)==row['afterSha256']
 return changed,{'result':'PASS','patch':name,'patchSha256':sha(patch),'textFiles':len(changed),'deletedPaths':[r['path'] for r in changed if r['deleted']],'byteParity':True,'commands':commands,'nativeDeviceOperations':False}
def main():
 assert not (OUT/'complete-assets.zip').exists()
 clean,cleanproof=makepatch(files(UP),effective(PATCH),'Glimpse-forge-workflows.patch')
 upgrade,upgradeproof=makepatch(effective(BASE/'native-patch/packages/apps/Glimpse'),effective(PATCH),'Glimpse-forge26-to27.patch')
 removed=upgradeproof['deletedPaths'];assert len(removed)==23 and all(Path(x).stem.startswith('exo_') for x in removed)
 native=[{'path':rel,'sha256':sha(p),'bytes':p.stat().st_size,'binary':p.suffix=='.png'} for rel,p in sorted(files(PATCH).items())]
 for r in native:
  if r['binary']:assert sha(BASE/'native-patch/packages/apps/Glimpse'/r['path'])==r['sha256']
 write_json(OUT/'current-native-files.json',native);write_json(OUT/'changed-files.json',clean);write_json(OUT/'upgrade-changed-files.json',upgrade);write_json(OUT/'verification/evidence/clean-patch-application.json',cleanproof);write_json(OUT/'verification/evidence/upgrade-patch-application.json',upgradeproof)
 inventory=read_json(BASE/'asset-inventory.json');inventory.update(date='2026-10-28',nativeTextFiles=len(clean),newDrawings=0,newRasterExports=0,reusedExistingPngConfigs=1680,sourceOwnerEditStages=36,distinctSourceOwnerFiles=33,media3LayoutOverlays=5,typedDrawableBindings=61,actualJavaClasses=9,actualKotlinOwners=72,dependencyAarsLinked=82,compiledNativeDependencyModules=10,compiledNativeDependencySources=925,additionalEditableComposition=1,editableDesktopWorkflowFixtures=26,sourceContentAuditSheets=1,baselineFamilyRecords=10926,baselineSourceVariants=16559,baselineOpenFamilyDecisions=9575,nativeAcceptance='NOT RUN',wholeGoalComplete=False)
 # The53 art masters and1680 production raster layers are inherited byte-for-byte; only native composition/binding changed.
 inventory['treatmentsInheritedByteForByte']=53
 inventory['prior26NewExportConfigs']=inventory.pop('newExportConfigs');inventory['historical26PlatformCompatibilityLibraries']=inventory.pop('extraPlatformCompatibilityLibraries');inventory.pop('typedDrawableBindings');inventory['qualifiedGlyphBindings']=59;inventory['typedDrawableResourceFiles']=62
 write_json(OUT/'asset-inventory.json',inventory)
 write_json(OUT/'owner-workflow-progress.json',{'W-05':'Partial: all original63 Gallery families now have content-backed decisions, all72 actual Kotlin and9 Java owners compile against exact pinned native inputs, and all82 dependency AAR resources link. Shared/dependent visual presentation and official native acceptance remain incomplete.','newVerifiedScope':['Explicit adaptive foreground108dp composition using two reworked original leaves','23 scoped styled-player aliases;22 native other aliases preserved','One scoped source-identical player layout with a cold steel error background','All 232 Media3 drawable/layout variants cataloged, including 189 PNGs','Exact compiler and 925 native dependency source files compiled','Clean and26-to27 patches, including23 required obsolete override deletions'],'remainingOwnerChecks':['Shared legacy/notification/VR presentation and default album artwork owner','Track-selection dialog, remaining Material/AppCompat/platform widget visual scope','Official Soong, dex/R8, XML inflation and effective product overlays','Native text/scrolling, accessibility, playback/focus/input and performance','Thor dual-display/rotation/controller acceptance; device explicitly deferred'],'wholeGoalComplete':False})
 wip=read_json(OUT/'WORK-IN-PROGRESS.json');wip.update(newArtwork='No new drawings/raster exports. Existing cold/mask masters are reused in the two active original icon leaves and a scoped cold player error panel.',allKotlinOwnerCompilation='PASS -72 actual Kotlin files plus 9 Java classes',fullPinnedResourceLink='PASS -82 actual AAR resource sets, pinned SDK 36',nativeDependencySourceCompilation='PASS -925 actual source files across 10 native modules',openBaselineFamilyDecisions=9575,fullPinnedSoongBuild='NOT RUN',nativeInflationAndDeviceAcceptance='NOT RUN',wholeGoalComplete=False);write_json(OUT/'WORK-IN-PROGRESS.json',wip)
 (OUT/'README.md').write_text('''# Forge27 — Gallery contracts and complete source compilation

Gallery's styled player controls now use23 scoped steel aliases. Native legacy
and notification consumers keep their original aliases; the correction removes
nine unintended shared-consumer effects from 26. Upgrade users must remove the23
old shared override files through the supplied 26-to27 patch.

Both original launcher icon leaves now form the active steel identity, retaining
their original adaptive child names. The foreground has explicit 108dp bounds and
a 20 percent safe inset. Gallery's player selects a scoped copy of the native media
layout whose only subtree change is the error background: a cold steel panel.
Media data, subtitles, shutter, loading, error text/visibility and action owners
remain source-owned. Error state does not imply toggled-on ember.

Cold material and neutral reflection/spill/seam/core/focus/symbol masks remain
separate. All 53 SVG treatments and1680 production PNG configurations match26
byte-for-byte. No new drawing or baked emission is claimed. Authored captions
remain live English source text; desktop sample text is marked as a sample.

## Saved outputs

- masters and native-patch: editable artwork, layered production exports and
  exact scoped source/resource changes.
- Glimpse-forge-workflows.patch: combined text patch against the pinned original
  Glimpse 89b473594ec8ad01417624e670912450ce5df7e9.
- Glimpse-forge26-to27.patch: incremental upgrade, including23 obsolete resource
  deletions. Both patches have clean-application and byte-parity evidence.
- current-native-files.json: full copy/hash inventory. Binary layers remain
  identical to26; clean checkouts still need them copied after the text patch.
- workflow-previews:25 regenerated existing editable specimens plus one new
  adaptive-icon/error-panel composition; desktop approximations only.
- previews: nine regenerated artwork/workflow sheets and an original-source
  contact sheet. The source sheet intentionally shows native unthemed inputs.
- discovered-media3-visual-scope.json: all 45 drawable/layout families and 232
  physical variants, including 189 decoded PNGs. Extra dependency scope is
  separate from the original10926-family baseline.
- semantic-review-delta.json: two source-backed decisions for the reworked
  original icon leaves. 9575 baseline family decisions remain OPEN.

## Verification

All 72 actual Gallery Kotlin files and9 Java presentation classes compile using
the exact pinned native compiler 2.2.0-custom-branch-22 and real resource namespaces.
925 actual dependency sources compile across 10 native modules. The complete
82 AAR resource set and effective application resources link against the pinned
native API 36 jar; the original module SDK/minimum/target remain36/30/36.

Real linked IDs generate33 library R namespaces, preserving 3167 original styleable
indices.45 compiled alias targets, current source/resource hashes, all 1680 PNGs,
36 reversible edit stages across 33 original owners,472 earlier canonical masters,
and the frozen26 archive pass bounded checks. Actual compiled policy tests pass
1536 cases/14076 assertions; geometry probes pass 1302 cases/257083 assertions.

This is manual full-source compilation and resource linking. Official Soong,
ABI generation, dex/R8, native XML inflation/layout, installed effective overlays,
Android text/accessibility/performance, Thor input/display acceptance and V3 are
NOT RUN. It is not an installable Gallery APK or a completed OS release. The full
goal remains active; see REMAINING.md and BUILD.md.

## Apply and rollback

For clean pinned originals, apply Glimpse-forge-workflows.patch and copy/hash-check
binary=true entries of current-native-files.json. For an exact Forge26 overlay,
apply only Glimpse-forge26-to27.patch; the PNGs already match. Always run
git apply --check first. Do not layer the combined patch over 26 or leave its 23
old shared overrides installed. Do not copy unrelated build caches or receipts
into the app's res directory.

Rollback uses the untouched upstream snapshot, prior signed26 checkpoint and
the full hash inventories. No device/media/settings/permission/wallpaper operation
or hardware flashing is performed by this checkpoint.
''',encoding='utf8')
 (OUT/'BUILD.md').write_text('''# Reproduce the bounded source checks

Use the repository-root tools with the same pinned official manifest and saved
Glimpse source. The exact SDK/library/compiler/source acquisition receipts under
source identify revisions, URLs, Git objects and SHA256; downloaded SDK/compiler
binaries and native dependency sources stay in the ignored local build cache.
Original committed app dependencies and extracted Media3 source retain licenses.

Run the following tools with Python3.12 on the existing Windows/JDK21 toolchain,
in order. Paths to Android SDK/JDK are explicit inside the tools and may need
local adjustment on a different machine:

1. resolve_gallery_native_dependencies.py
2. fetch_gallery_native_compiler.py
3. verify_gallery_native_toolchain.py
4. fetch_gallery_native_source_inputs.py
5. compile_gallery_native_dependencies.py
6. link_gallery_complete_resources.py
7. generate_gallery_real_resource_namespaces.py
8. compile_gallery_complete_owners.py
9. test_gallery_compiled_policy.py
10. verify_gallery_alias_contracts.py
11. review_gallery_complete_contracts.py
12. verify_gallery_contract_checkpoint.py

The exact native listenablefuture binary is identified in
source/native-listener-interface.json; it must exist at its hash-verified cache
path before complete-owner compilation. It is not replaced by an invented
interface. The saved native-build-contracts sources document dependency ordering.
Both actual Material providers in the native graph are retained.

Rendering additionally uses the existing local Pillow/resvg environment via
CRAFTAGEDDON_RENDERLIB. render_gallery_contracts_review.py generates English
editable desktop specimens; it does not execute Android. Several scripts refuse
to modify a checkpoint after complete-assets.zip exists. Reproduce in a new
review copy, preserving signed checkpoints.

Earlier failed host/device compiler setup attempts are retained as diagnostic
history. The final native-dependency-compilation.json and
complete-owner-compilation.json report the successful invocations and source
hashes. No Gradle plugin script, downloaded project script, emulator or device
command was executed. These checks do not substitute for official Soong/dex/R8
or native/device acceptance.
''',encoding='utf8')
 (OUT/'REVIEW.md').write_text('''# Gallery contract review — 28 October 2026

Reviewed the original-source contact sheet across all 34 drawable families that
have density PNGs, and regenerated the four art/material and five workflow sheets.
Every 189 bitmap variant decodes and has recorded dimensions and pixel hashes;
all 43 XML drawable/layout variants have content/consumer records. Source content,
actual aliases, constructor defaults and call sites drive the dispositions.

The new adaptive composition shows the same cold photo badge under circle,
rounded and square desktop masks. Explicit108dp intrinsic bounds and 20 percent
inset preserve alpha inside the platform safe circle. The cold error housing
uses false_value; sample message text is live English and clearly identified.
The source player subtree differs only in its background reference.

All 23 styled aliases are checked in the actual compiled table.22 native legacy/
notification aliases still point to their original leaves; nine cross-consumer
effects are corrected. The original library vectors and PNG variants are kept
for those consumers. Their remaining presentation work is explicit, not approved
by assuming they are unreachable.

All actual app owners compile against real resource namespaces and pinned native
dependencies. Policy and geometry probes use the resulting real app class jar.
No fake app model/controller or placeholder resource ID is substituted.

This review is a bounded desktop/source review. Native Android inflation, actual
launcher masks, text layout/accessibility, playback/input, full official build
and independent whole-goal V3 remain unrun. No Inkscape roundtrip is claimed.
''',encoding='utf8')
 pending=collections.Counter((r['baselineFamily']['project'] for r in read_json(OUT/'semantic-family-ledger.json') if r['decision']=='OPEN'))
 remaining='''# Remaining work — checkpoint27

The whole goal remains ACTIVE. 9575 original semantic family decisions are OPEN.
That number is not a count of missing drawings. All 10926 families and16559 source
variants remain conserved. The two original Gallery icon leaves are now authored
and reviewed; original Gallery baseline decisions no longer remain open.

W05 remains partial: shared legacy/notification/VR presentation, default album
artwork owner, track-selection dialog, and additional Material/AppCompat/platform
widget scope still need completion. The dependency catalog's preserved native
contracts do not approve dependent presentation as finished. All actual app
source and full manual resource linking now pass, but official Soong/ABI/dex/R8,
native XML inflation, effective overlays, text/scroll/accessibility, playback,
focus/input/performance and Thor dual-display/rotation/controller acceptance
remain unrun. Device access was explicitly deferred.

W03 setup and W07 boot/charger/recovery still need authored workflow handoffs.
W04 retains three legacy/unbound resource decisions plus exact private/SPA owner
builds and integration gates. W01/W02/W06 have authored source/art handoffs;
those do not establish final native/device acceptance.

Continue all original unassigned/tentative-reuse families, the16 named gaps,
20 original app/component roles, seven workflow groups and newly discovered
scope. Earlier source-backed decisions are retained; dependencies are not silently
excluded from the full objective. A fresh independent whole-goal completeness,
state and content double-check must follow completion; it is NOT RUN.

Current open-family counts by project:
'''
 remaining+='\n'.join('- '+name+': '+str(n) for name,n in pending.most_common())+'\n';(OUT/'REMAINING.md').write_text(remaining,encoding='utf8')
 shutil.copy2(BASE/'THIRD_PARTY_SOURCES.md',OUT/'THIRD_PARTY_SOURCES.md')
 technical=read_json(OUT/'verification/evidence/gallery-source-art-checks.json');technical.update(date='2026-10-28',checkpointScope='Bounded Gallery native-source/resource contracts and artwork composition checkpoint; whole goal and native/device acceptance incomplete.',v1Scope='Actual styled-player alias consumers, two active original icon leaves, scoped cold error housing, complete dependency variant inventory and conserved semantic ledger.',v2Method='Fresh pinned source/pixel/hash/reuse audit; all actual app owners and 925 native source dependencies compiled with exact native compiler;82 AAR pinned SDK 36 resource link; real nonzero R namespaces and45 compiled aliases; clean/upgrade patch parity; actual compiled policy/geometry probes; English desktop rendering review.')
 write_json(OUT/'verification/evidence/technical.json',technical)
 print({'completeTextPatchFiles':len(clean),'upgradeTextPatchFiles':len(upgrade),'obsoleteSharedOverridesDeleted':len(removed),'binaryLayersUnchanged':1680,'openBaselineFamilies':9575})
if __name__=='__main__':main()
