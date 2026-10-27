'''Save a bounded card foundation checkpoint without narrowing the full goal.'''
from pathlib import Path
import collections,hashlib,json,shutil
from audit_os_resource_coverage import ROOT,read_json,write_json
OUT=ROOT/'iterations/24-updater'
BASE=ROOT/'iterations/23-magnification'
def main():
    assert not (OUT/'complete-assets.zip').exists()
    checks=read_json(OUT/'verification/evidence/card-stage-checks.json')
    build=read_json(OUT/'verification/evidence/material-subset-build.json')
    assert checks['result']==build['result']=='PASS'
    # Full baseline, unchanged decisions. A phase/code review is not counted as
    # closing unrelated drawable, layout, value or motion families.
    ledger=read_json(BASE/'semantic-family-ledger.json')
    counts=collections.Counter(r['decision'] for r in ledger)
    assert len(ledger)==10926 and counts['OPEN']==9630
    write_json(OUT/'semantic-family-ledger.json',ledger)
    write_json(OUT/'semantic-review-progress.json',{
        'date':'2026-10-27','familyRecords':len(ledger),'sourceFileVariants':16559,
        'openFamilyDecisions':9630,'newFamilyDecisions':0,'decisions':dict(counts),
        'previouslyAuthoredWorkflowGroups':['W-01','W-02','W-06'],
        'partiallyAuthoredWorkflowGroups':['W-04'],
        'unauthoredWorkflowGroups':['W-03','W-05','W-07'],
        'incompleteWorkflowGroups':['W-03','W-04','W-05','W-07'],
        'wholeSemanticReviewFinished':False,'wholeGoalComplete':False,
        'finalWholeGoalDoubleCheck':'NOT RUN - full required scope remains unfinished'})
    write_json(OUT/'asset-inventory.json',{
        'newlyAuthoredDrawings':0,'exactReusedSvgMasters':4,'exactSourceTextures':2,
        'exactReusedNativePngConfigurations':112,'neutralMaskConfigurations':96,
        'editableCardFixtures':18,'composedCardPreviewPngs':18,'comparisonSheets':2,
        'modifiedActualNativeSourceFiles':4,'newRenderingAndSupportSourceFiles':5,
        'currentTextPatchFiles':9,'pinnedOriginalSourceAndDependencyFiles':83,
        'fullUpdaterWorkflowComplete':False})
    write_json(OUT/'owner-workflow-progress.json',{
        'workflow':'W-04','revision':'6d50e0bf1b16fe7bca818375a3e734f4959e2e57',
        'domainPhaseTransport':'AUTHORED - required phase reaches actual presentation model',
        'cardActionAndRailPresentation':'AUTHORED - four reused material families',
        'runningPausedErrorReadyDistinction':'HOST/SOURCE CHECKS PASS',
        'responsiveActionAndProgressRows':'AUTHORED - desktop fixture checks; Android layout NOT RUN',
        'actualScaffoldAndDeviceInfoBanner':'NOT AUTHORED',
        'preferencesAndActualControls':'NOT AUTHORED',
        'dialogsImportAndIllustrations':'NOT AUTHORED',
        'remainingGlyphAndNativeResourceBridges':'NOT AUTHORED',
        'fullPinnedNativeBuild':'NOT RUN','fullWorkflowComplete':False,
        'wholeGoalComplete':False})
    technical={**checks,'date':'2026-10-27','components':4,
        'checkpointScope':'Partial W04 updater card foundation: explicit native phase transport, four reused layered material families, actual card/action/progress source bindings and desktop state fixtures. Not a completed updater or full corpus release.',
        'v1Scope':'All 13 source operation phases and 14 action types are recorded. Native phase, not status text, non-null progress or isInstalling, controls lighting. Original callbacks/enablement/data are preserved. Four workflow groups, the complete 10926-family baseline and final whole-goal check remain required.',
        'v2Method':'83 pinned source hashes; clean combined patch parity; exact owner reverse edits; 112 unchanged resource configs, 96 neutral masks, resource-derived fixed-cap minimums; SDK37 resource compile/link and three Java rendering classes; four whole Kotlin files plus verbatim native enum declaration with recorded compatibility libraries; 234 host phase cases, 128 actual policy cases, 18 strict-XML desktop fixtures and 472 earlier master hashes.',
        'actualPrivateOwnersCompiled':False,'nativeLayoutOrInputExecuted':False,
        'targetV3':'NOT RUN - pinned Soong, native rendering/input/accessibility and device acceptance remain open.',
        'wholeGoalComplete':False}
    write_json(OUT/'verification/evidence/technical.json',technical)
    shutil.copy2(BASE/'signing-public-key.pem',OUT/'signing-public-key.pem')
    (OUT/'README.md').write_text('''# Forge 24 — updater card foundation

Actual updater cards, action buttons and progress rails now use cold steel and
separate neutral light masks. Native operation phase reaches the presentation
model explicitly: paused and suspended operations stay cold even when they
retain progress. Running operations glow; ready/reboot states stay cold.
Momentary press is separate from cool focus/hover. Native labels stay live.

This is a partial W04 checkpoint. The complete semantic/artwork goal remains
active: **9,630 open family decisions and four incomplete workflow groups**.
No corpus family decisions are closed here. Actual scaffold/banner, preferences,
dialogs/import/checking/zero/error illustrations and remaining glyph/resource
bridges are still required for the updater. W03 setup, W05 gallery and W07
boot/charger/recovery remain unauthored. Additional artwork/owner work and the
final independent whole-goal double-check remain required.

## Usable outputs

- Updater-forge-source.patch: combined text changes against the exact pinned
  Updater revision 6d50e0bf1b16fe7bca818375a3e734f4959e2e57.
- native-patch/packages/apps/Updater: copy the hash-listed binary resources to
  the same source paths; binaries are outside the text patch.
- masters: four unchanged editable SVG aliases with their exact texture inputs
  in separate portable folders. No newly authored drawings are claimed.
- workflow-previews and previews: 18 editable card fixtures and two sheets.
  Sample values, fonts, glyphs and progress rendering are desktop approximations,
  not Android screenshots or installed-build evidence.
- verification/evidence: source, compile, state, mask, bounds and preserved-source
  checks. Resource banks/JARs are verification-only and are not installable apps.

Use git -c core.autocrlf=false apply --check, then apply the text patch against
the pinned module root. Preserve the separate masks and their runtime colors.
All 112 resource configurations and four SVG masters are exact reuses; the
resource-derived intrinsic minimums protect fixed corners, and native padding
reserves label space. Native click/enablement callbacks and real data stay in
their original owners. No updater/controller/installer operation is executed.

## Evidence and limits

83 original/dependency source files match their pinned Git blob and SHA-256
identities. The nine-file patch applies byte-for-byte; four modified source files
reverse to their originals. Three actual Java rendering classes, four whole
Kotlin files and the verbatim native phase enum declaration compile. The
compatibility classpath uses Kotlin/Compose compiler 2.3.21 and cached Material3
1.4.0; this is not the official pinned Soong dependency resolution. The actual
mapper, UpdateItem and ActionBar are not compiled.

234 phase combinations and 128 actual compiled policy cases pass. Host fixtures
execute presentation data/enum/policy types only. All 96 neutral mask configs,
112 fixed-cap metadata checks, English desktop text/control bounds and the
472 earlier master hashes pass. Default authored language is English/en-US;
labels are source resources and live controls, not lettering baked into skins.

V1/V2 pass only for this bounded source/art/compatibility/desktop scope.
Full pinned Soong, Android rendering/input/accessibility/performance, physical
Thor acceptance and V3 remain NOT RUN. No hardware was installed, changed or
flashed. Artifact signing is a source identity, separate from APK/OTA/AVB trust.

Existing upstream code remains under Apache-2.0 with original headers/notices
and the included full license. CC0 material additions do not relicense upstream
code or geometry. The source archive, hashes, public key and signature preserve
this checkpoint; restore distribution parts with Restore-Archive.ps1.

## Reproduction

Use tools/fetch_updater_owners.py, fetch_updater_ui_dependencies.py,
review_updater_sources.py, prepare_updater_phase_binding.py,
build_updater_material_bindings.py, check_updater_phase_binding.py,
compile_updater_material_sources.py, render_updater_card_fixtures.py and
verify_updater_card_stage.py in that order in a fresh scratch checkout.
Set CRAFTAGEDDON_RENDERLIB to the installed rendering library directory.
Use the recorded Python/Pillow/resvg, JDK and SDK37. The Windows SDK compiler
runs outside this sandbox. Builders guard packaged checkpoints; preserve frozen
outputs and use a new iteration for further work.
''',encoding='utf8')
    (OUT/'REVIEW.md').write_text('''# Review — bounded updater card foundation

Multiple source/visual passes checked source activation, fixed-corner sizing,
cold/active/disabled controls, retained progress, native English strings,
compact large text and both SPA spacing branches. Cards use actual operation
phase. Paused/suspended values are preserved without an active ember housing.
Errors keep distinct messages and a separate runtime error indicator color.

An initial minimum smaller than fixed caps was corrected to resource-derived
intrinsic dimensions. Padding comes from the actual native nine-patch. The
indicator is centered in its rail, and action/progress-detail rows wrap. Source
SHA checks and exact patch/reverse parity confine changes to phase transport
and the recorded presentation/layout changes. Original controller, action,
enablement, installer and callback bodies are retained.

The two final sheets and the standalone compact sample were inspected after
iteration. Desktop font/glyph/progress approximations are explicit. This does
not prove Android pixel parity, native input, accessibility or performance.
The host tests run presentation data/enum/policy types; updater/controller/
installer operations and Android/hardware execution remain unrun.

W04 and the whole goal are incomplete. All 9,630 open corpus decisions, the
remaining updater owners/illustrations/glyph bridges, W03/W05/W07, additional
discovered art/owners and the final independent whole-goal check stay required.
No partial source check is promoted to full workflow or device acceptance.
''',encoding='utf8')
    (OUT/'WORK-IN-PROGRESS.md').write_text('''# Full updater workflow remains in progress

The phase/card/action/rail foundation is saved as signed checkpoint 24. It
reuses four material families and retains the complete corpus ledger unchanged.
See README.md and the bounded verification evidence for this checkpoint.

Continue in a new iteration with the actual scaffold/device-info banner,
preferences and controls, dialogs/import/checking/zero/error illustrations,
and remaining glyph/resource bridges. The current private mapper/UpdateItem/
ActionBar compilation, full pinned Soong, Android rendering/input/accessibility
and device acceptance remain unrun.

The full goal remains active: 9,630 open family decisions, incomplete W03/W04/
W05/W07, additional artwork/owner work and a final independent whole-goal check.
No hardware or updater/controller/installer operation has executed.
''',encoding='utf8')
    print(json.dumps({'checkpoint':'24-updater','newDrawings':0,'reusedNativeConfigurations':112,
                      'openFamilyDecisions':9630,'fullW04Complete':False,'wholeGoalComplete':False}))
if __name__=='__main__':main()
