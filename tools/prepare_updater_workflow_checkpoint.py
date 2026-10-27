'''Save the bounded updater workflow handoff without narrowing the full goal.'''
import collections,shutil
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/25-updater-workflows';BASE=ROOT/'iterations/24-updater'
def main():
    assert not (OUT/'complete-assets.zip').exists()
    check=read_json(OUT/'verification/evidence/workflow-source-art-checks.json')
    build=read_json(OUT/'verification/evidence/material-subset-build.json')
    assert check['result']==build['result']=='PASS'
    ledger=read_json(BASE/'semantic-family-ledger.json');delta=[];bindings=[]
    reviews={
      'ic_notification':('PRESERVE_NATIVE_REFERENCE_CONTRACT','Native notification/action alpha silhouette; actual UpdaterService, ExportUpdateService and NotificationHelper small-icon consumers are preserved. Rich dialog badge is a separate owner resource; no global bitmap substitution.','controller/UpdaterService.java; ExportUpdateService.java; notifications/NotificationHelper.kt; updates/action/UpdateActionDialog.kt'),
      'lineage_mark_tight':('PRESERVE_NATIVE_REFERENCE_CONTRACT','Original 300:120 brand geometry/translation and white-on-dark treatment stay exact. Scoped cold steel housing replaces the teal header presentation.','deviceinfo/UpdaterCard.kt'),
      'progress_dialog':('OWNER_PRESENTATION_ADAPTATION_AUTHORED','Actual import layout retains indicator ID, indeterminate behavior and 16sp live English label. Weighted text wraps. Owner keeps noncancelable import, show/dismiss order, success/error messages and callbacks; native indicator/ring styled separately.','UpdatesActivity.java; res/layout/progress_dialog.xml; forge/ForgeDialogStyle.java'),
      'sysupdater_error':('OWNER_PRESENTATION_ADAPTATION_AUTHORED','Original 60fps/60-frame JSON remains exact as one-iteration timing input. New cold exclamation/gear and separate transient red masks replace visual geometry and end cold; original morph paths are not rendered.','updatescheck/UpdatesCheck.kt; forge/ForgeIllustrationClock.kt; forge/ForgeIllustrations.kt'),
      'sysupdater_progress':('OWNER_PRESENTATION_ADAPTATION_AUTHORED','Original 60fps/120-frame JSON stays exact as repeating timing input. New layered update arrow/gear and neutral sweep replace visual paths. Source 2000ms minimum, system scale, lifecycle and iteration roles retained in source; native execution unrun.','updatescheck/UpdatesCheck.kt; forge/ForgeIllustrationClock.kt; forge/ForgeIllustrations.kt'),
      'config':('OWNER_PRESENTATION_ADAPTATION_AUTHORED','Four typed brand colors and formatted download URL remain exact. Actual UpdaterCard uses cold housing and transparent interior instead of executing its teal pattern modifier. White brand tint and device URL formatting remain source-owned; no global override or effective-overlay acceptance inferred.','res/values/config.xml; deviceinfo/UpdaterCard.kt; deviceinfo/actions/DeviceInfoActionButtons.kt')}
    for row in ledger:
        b=row['baselineFamily']
        if b['project']!='packages/apps/Updater':continue
        name=b['name'];binding={'familyId':row['familyId'],'source':b,'sourceEvidence':row['evidence'],'decisionKept':row['decision'],'nativeDropInApproval':False,'fullSoongOrDeviceAcceptance':'NOT RUN'}
        if name in reviews:
            decision,rationale,owners=reviews[name];assert row['decision']=='OPEN'
            row.update(decision=decision,rationale=rationale,requiredAction='Use scoped iteration25 handoff; pinned private-owner/SPA compile, effective resources, Android rendering/input/lifecycle/accessibility and device acceptance remain separate.')
            binding.update(decisionKept=decision,rationale=rationale,actualOwners=owners,sourcePatch='Updater-forge-workflows.patch',wholeFamilySemanticReviewRecorded=True)
            delta.append({'familyId':row['familyId'],'previousDecision':'OPEN','decision':decision,'source':b,'sourceEvidence':row['evidence'],'ownerBinding':binding,'runtimeValidationComplete':False})
        elif name=='ic_launcher':
            binding.update(role='Actual manifest keeps @mipmap/ic_launcher; cold badge with18 percent inset and original monochrome geometry bound to adaptive owner. Manifest actions/categories unchanged.',newOwnerBindingAuthored=True)
        elif name=='ic_pause':
            binding.update(role='Existing semantic artwork decision retained. Actual Compose pause uses original-donor optical treatment; shared notification vector unchanged.',newOwnerBindingAuthored=True)
        else:
            binding.update(role='Original legacy launcher input or unbound system-update vector preserved. Broader/effective consumer selection unresolved; lack of indexed reference is not unreachability proof.',wholeFamilySemanticReviewRecorded=False)
        bindings.append(binding)
    assert len(bindings)==11 and len(delta)==6 and len(ledger)==10926 and sum(len(r['evidence']) for r in ledger)==16559
    counts=collections.Counter(r['decision'] for r in ledger);assert counts['OPEN']==9624
    write_json(OUT/'semantic-family-ledger.json',ledger);write_json(OUT/'semantic-review-delta.json',delta);write_json(OUT/'owner-binding-review.json',bindings)
    write_json(OUT/'semantic-review-progress.json',{'date':'2026-10-27','familyRecords':10926,'sourceFileVariants':16559,'previousOpenFamilyDecisions':9630,'newContentBackedDecisions':6,'openFamilyDecisions':9624,'decisions':dict(counts),'previouslyAuthoredWorkflowGroups':['W-01','W-02','W-06'],'partiallyAuthoredWorkflowGroups':['W-04'],'unauthoredWorkflowGroups':['W-03','W-05','W-07'],'incompleteWorkflowGroups':['W-03','W-04','W-05','W-07'],'remainingUpdaterFamilyReviews':['ic_launcher_background','ic_launcher_foreground','ic_system_update'],'wholeSemanticReviewFinished':False,'wholeGoalComplete':False,'finalWholeGoalDoubleCheck':'NOT RUN - full required scope remains unfinished'})
    current=read_json(OUT/'current-native-files.json');up=OUT/'upstream/packages/apps/Updater'
    write_json(OUT/'asset-inventory.json',{'newArtworkMasters':8,'newIllustrationMasters':3,'newMiniGlyphMasters':5,'materialOnlyDerivativesOfExistingMasters':3,'exactReusedResourceConfigurations':168,'newDensityExportConfigurations':312,'nativePngConfigurations':480,'neutralMaskConfigurations':412,'newNativeTextFiles':sum(not (up/r['path']).exists() for r in current),'modifiedActualNativeSourceOrResourceFiles':sum((up/r['path']).exists() for r in current),'combinedTextPatchFiles':len(current),'newRenderingSupportClasses':6,'newKotlinPresentationFiles':6,'pinnedOriginalSourceAndDependencyFiles':90,'editableScreenFixtures':25,'editableCardFixtures':18,'comparisonSheets':7,'sourceProductionBakedGlows':0,'sourceProductionBakedLabels':0,'wholeUpdaterNativeAcceptance':False})
    write_json(OUT/'owner-workflow-progress.json',{'workflow':'W-04','revision':'6d50e0bf1b16fe7bca818375a3e734f4959e2e57','sourceArtScreensAuthored':['scaffold and dark palette','device banner and link actions','operation cards/actions/progress','A/B and non-A/B preferences','AC-forced-on locked switch','interval picker','operation dialogs','legacy import progress/success/error','checking/offline/error/zero illustrations','adaptive application icon and scoped action glyphs'],'tvQr':'Native encoded data/generator preserved; not simulated as a working code','stillOpen':['Three legacy/unbound source-family consumer reviews','Compile actual SPA adapters and complete private Updater owners in pinned Soong','Effective overlay/resource selection','Android layout/scroll/input/accessibility/lifecycle and animator behavior','Physical Thor acceptance'],'fullSourceFamilyReviewComplete':False,'fullPinnedNativeBuild':'NOT RUN','fullWorkflowComplete':False,'wholeGoalComplete':False})
    technical={**check,'components':17,'checkpointScope':'Bounded W04 source/artwork extension: actual scaffold/banner/preferences/dialog/import/checking/zero owners, layered glyphs and adaptive identity. Not a complete corpus, updater build or Android release.','v1Scope':'Six content-backed decisions; scoped owner changes preserve domain conditions, callbacks, logging contracts, QR, notification silhouettes and timing JSON. Full10926-family baseline and remaining work stay open.','v2Method':'90 pinned source identities; clean33-file patch;16 owner reverse chains;480 PNGs/168 exact reuses; resource compilation/link and6 Java/9 whole Kotlin compatibility compilations plus verbatim enum;17720 actual compiled presentation assertions;234 phase cases;43 editable English desktop fixtures;472 preserved masters/signed24 archive;adaptive safe-circle geometry.','targetV3':'NOT RUN - pinned Soong/private owners/SPA adapters, effective resources, Android rendering/input/accessibility/lifecycle and physical Thor acceptance remain open.','desktopVisualReview':'REVIEW.md;7 sheets and detailed fixtures inspected. Desktop approximations only.'}
    write_json(OUT/'verification/evidence/technical.json',technical)
    shutil.copy2(BASE/'signing-public-key.pem',OUT/'signing-public-key.pem');shutil.copy2(ROOT/'iterations/21-native-workflows/source/LICENSE-APACHE-2.0.txt',OUT/'source/LICENSE-APACHE-2.0.txt')
    c=read_json(OUT/'source-contract-review.json');c.update(scope='Current source phase/action contract inherited from24 and rechecked in25; presentation authored; full native acceptance NOT RUN.',pinnedSourceFilesVerified=90,pinnedOriginalSourceFiles=76,pinnedUiDependencyFiles=14)
    for row in c['phaseBindingsProposed']:row['bindingImplemented']=True
    write_json(OUT/'source-contract-review.json',c)
    (OUT/'README.md').write_text('''# Forge 25 — updater workflow artwork and source handoff

Actual updater main screens, device banner, preferences, interval picker,
operation dialogs, local import, checking/error/zero illustrations, action
glyphs and adaptive identity now have scoped steel presentation. Eight new
layered drawings and three optical material treatments extend the prior art.
Cold bases and neutral light masks stay separate. Native text stays live and
defaults to English; no lettering or ember is baked into production skins.

Running operations glow; paused/suspended/ready/reboot states stay cold.
AC-forced-on preferences stay on/glowing while interaction is locked.
Focus/hover stays cool; enabled pressing is momentary ember. Error light is
transient red, ending cold, rather than a selected/on state. Original Lottie
JSON provides timing; new geometry replaces the old visual/morph paths.

## Usable outputs

- Updater-forge-workflows.patch: combined text patch against exact Updater
  revision6d50e0bf1b16fe7bca818375a3e734f4959e2e57.
- native-patch/packages/apps/Updater:480 PNG configurations (68 cold/412 neutral
  masks), including168 exact prior reuses. Copy binaries to module-relative
  paths after applying text patch; current-native-files.json lists33 text files.
- masters:8 new editable SVGs,3 material-only optical derivatives, exact original
  aliases and portable texture inputs. Earlier canonical masters stay unchanged.
- workflow-previews:25 screen/control/dialog and18 operation-card fixtures,
  editable SVG plus PNG. previews contains7 comparison sheets.
- owner-binding-review.json, full semantic ledger and verification/evidence:
  explicit source decisions, checks and remaining target gates.

Fixture metadata is sample data. Segoe UI/layout/glyph/progress metrics are
desktop approximations, not Android screenshots or installed-device facts.
Large-font fixtures show full content; native viewport scrolling is untested.

The source600dp breakpoint/equal wide panes, native scroll/data/link owners,
A/B and recovery-presence branches, repository callbacks and original logging
wrappers stay in place. Interval selection closes before its original callback.
Import remains noncancelable with unchanged show/dismiss/success/error flow.
Shared notification silhouettes and native QR generation/payload stay exact.
The rich dialog badge is scoped separately; no notification raster substitution.

## Verification and limits

Bounded checks pass:90 pinned source/dependency identities;16 reverse-byte owner
chains;clean33-file patch parity;480 layer exports;168 exact reuses;17,720
assertions against actual compiled pure presentation classes;234 phase cases;
strict XML/English desktop bounds;472 earlier master hashes;unchanged signed24
ZIP. The cold badge fits the66/108 adaptive safe circle with18% foreground inset.

SDK37 compiles all patch resources and links a separate rendering bank.
Six actual Java classes,nine whole Kotlin files and a verbatim source enum
compile with recorded Kotlin/Compose2.3.21,cached Material3 1.4.0 compatibility
libraries. Actual Lottie6.5.2 artifacts match official Maven SHA512 sidecars.
Verification outputs are not installable apps or official pinned Soong builds.

Actual SPA public-model adapters and complete private Updater owners are NOT
compiled. Full pinned Soong,effective resources/overlays,Android rendering,
scroll/input/accessibility/lifecycle/animator behavior and physical Thor
acceptance remain NOT RUN. Static API/source review does not replace these gates.
TV QR output is not simulated as a working code. No updater/controller/installer
or hardware operation is executed. V1/V2 pass for bounded source/art/desktop
scope only;V3 is unrun.

The whole goal remains active:9,624 open family decisions;W03/W05/W07 still
unauthored;W04 consumer review/native gates incomplete;remaining app/glyph owners,
further discovered art and final independent whole-goal review still required.
Updater legacy launcher foreground/background and ic_system_update remain open.
Preserving them does not establish global unreachability or finished coverage.

Original code/geometry retains notices/Apache-2.0 terms;new art uses project
CC0 terms. Source artifact signing identifies a checkpoint,not APK/OTA/AVB trust.
Restore distribution parts with Restore-Archive.ps1.

## Reproduction

Preserve frozen24. In a scratch copy retain exact24 inputs,run
bind_updater_workflow_owners.py before recorded glyph-owner-edits.json operations.
Apply those glyph operations with exact occurrence/input/output hash checks.
Current editable helpers are authoritative;do not rerun earlier owner stages
over later edits. Run build_updater_workflow_art.py,snapshot_updater_workflow_patch.py,
compile_updater_workflow_sources.py,preview_updater_workflow_art.py,
render_updater_workflow_fixtures.py,render_updater_workflow_cards.py and
verify_updater_workflow_stage.py with recorded runtime/render library/SDK37/JDK.
Windows SDK compilation runs on host.Builders refuse to rewrite packaged outputs.
''',encoding='utf8')
    (OUT/'WORK-IN-PROGRESS.md').write_text('''# Saved work-in-progress checkpoint
See README.md,owner-workflow-progress.json and semantic-review-progress.json.
Bounded checks pass;full private-owner/SPA compile,Android/device acceptance
and complete semantic/visual goal remain open.
''',encoding='utf8')
    (OUT/'REVIEW.md').write_text('''# Desktop visual and source review

All seven comparison sheets were inspected,with detailed main,AC-locked
preference,adaptive identity and large-font installation-dialog fixtures.
This is offline artwork/source review,not Android pixel parity or target
scrolling,input,lifecycle,accessibility,color calibration or performance.

Two passes brightened cold edges and reduced texture to14 percent for unlit
glyph legibility. Original geometry and all six original neutral mask subtrees
are preserved;earlier masters stay exact.The launcher foreground inset18 percent
fits the66/108 safe circle.Error cue uses separate runtime tint masks.

Main checking/offline/error/zero,preferences A/B/non-A/B/AC/recovery/periodic-off,
interval choices,operation confirmations,legacy import progress/success/error,
large English text,source phase cards and cool focus/momentary press are shown.
Legacy import uses a native circular-indicator approximation,not a checking
arrow.QR generation is preserved without simulating a working code.

Remaining:pinned SPA/private-owner compilation,effective resources/overlays,
Android typography,large-font viewport scroll,dialog sizing,input/focus,
lifecycle and animator behavior.The three legacy/unbound updater families and
broader9,624-family/remaining workflow work stay open.No final independent
whole-goal review or V3 completion is claimed.
''',encoding='utf8')
    print({'openFamilyDecisions':9624,'newDecisions':6,'screenFixtures':25,'cardFixtures':18,'wholeGoalComplete':False})
if __name__=='__main__':main()
