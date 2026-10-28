'''Save the bounded setup glyph foundation, preserving all unfinished workflow scope.'''
from pathlib import Path
import shutil
from audit_os_resource_coverage import ROOT,read_json,write_json
import prepare_gallery_contract_checkpoint as patches
OUT=ROOT/'iterations/28-setup-workflows';BASE=ROOT/'iterations/27-gallery-contracts';UP=OUT/'upstream/packages/apps/SetupWizard';PATCH=OUT/'native-patch/packages/apps/SetupWizard'
def main():
 assert not (OUT/'complete-assets.zip').exists()
 patches.OUT=OUT;patches.UP=UP;clean,proof=patches.makepatch(patches.files(UP),patches.files(UP)|patches.files(PATCH),'SetupWizard-forge-glyphs.patch')
 write_json(OUT/'changed-files.json',clean);write_json(OUT/'verification/evidence/clean-patch-application.json',proof)
 native=[{'path':rel,'sha256':patches.sha(p),'bytes':p.stat().st_size,'binary':p.suffix=='.png'} for rel,p in sorted(patches.files(PATCH).items())];write_json(OUT/'current-native-files.json',native);assert sum(r['binary'] for r in native)==630
 for name in ['semantic-family-ledger.json','semantic-family-ledger.json.gz','signing-public-key.pem']:shutil.copy2(BASE/name,OUT/name)
 write_json(OUT/'semantic-review-delta.json',[]);progress=read_json(BASE/'semantic-review-progress.json');progress.update(date='2026-10-28',previousOpenFamilyDecisions=9575,newContentBackedDecisions=0,openFamilyDecisions=9575,partiallyAuthoredWorkflowGroups=['W-03','W-04','W-05'],unauthoredWorkflowGroups=['W-07'],remainingSetupFamilyReviews=56,wholeSemanticReviewFinished=False,wholeGoalComplete=False);write_json(OUT/'semantic-review-progress.json',progress)
 write_json(OUT/'asset-inventory.json',{'date':'2026-10-28','editableGlyphMasters':18,'sourceGeometryTreatments':17,'newLetteringFreeLanguageGlobe':1,'densityPngConfigs':504,'highResolutionNodpiPngConfigs':126,'uniqueProductionPngConfigs':630,'coldPngConfigs':90,'neutralMaskPngConfigs':540,'nativePatchPngCopies':630,'totalPhysicalPngExportAndNativeCopies':1260,'positiveGlyphResourceBridges':16,'unboundGlyphsPending':2,'originalIntrinsicDpMetadata':18,'actualJavaCoreClasses':3,'actualKotlinAppOwnersUnmodifiedAndUncompiled':39,'textPatchFiles':len(clean),'pinnedAppSources':130,'pinnedTemplateInputs':52,'desktopGlyphReviewSheets':1,'baselineFamilies':10926,'baselineVariants':16559,'baselineOpenDecisions':9575,'newSemanticClosures':0,'fullWorkflow':'INCOMPLETE','nativeAcceptance':'NOT RUN','wholeGoalComplete':False})
 readme=(OUT/'README-WIP.md').read_text(encoding='utf8');readme='# Forge 28 — Setup glyph foundation\n\n'+readme.removeprefix('# Setup workflow rework in progress\n\n')
 readme=readme.replace('First artwork','First artwork').replace('contain18','contain 18').replace(':17',': 17').replace('symbol.90','symbol. 90').replace('and540','and 540').replace('including126','including 126').replace('SDK37','SDK 37').replace('1536 state cases/14076','1,536 state cases / 14,076').replace('assertions,18','assertions, 18').replace('and126','and 126').replace('pass.130','pass. 130').replace('and52','and 52').replace('All39','All 39').replace('original63','original 63').replace('with56','with 56').replace('wider9575','wider 9,575').replace('LineageOS24','LineageOS 24').replace('Forge27','Forge 27').replace('revision691','revision 691')
 readme+='''
## Complete assets and source

The signed complete-assets.zip contains every individual export, native resource,
editable master, original source, manifest and verification record. Git transports
that complete ZIP through distribution/Restore-Archive.ps1. The PNG banks are
inside the archive; the repository keeps editable masters and the visual review
sheet directly visible. Restore the ZIP, then extract into an empty review folder.

For a source checkout, verify the pinned SetupWizard revision above, run
git apply --check and git apply with SetupWizard-forge-glyphs.patch, then copy
every binary=true entry in current-native-files.json from the archive's
native-patch/packages/apps/SetupWizard to its module-relative path and verify
SHA256. Do not install the resource bank: its minimal manifest is only a public
compatibility test, not the privileged app configuration.

Rollback uses the untouched upstream snapshot and reverse text patch. New
prefixed PNGs are listed with hashes; preserve any file with different contents.
No app/platform certificate, permission or manifest change is part of this pass.

## Reproduce the source/glyph checks

Repository tools fetch_setup_workflow_sources.py and
fetch_setup_template_contracts.py preserve exact inputs. map_setup_workflow_contracts.py
records source/resource/acceptance scope. build_setup_glyph_art.py,
bind_setup_glyph_resources.py, compile_setup_glyph_core.py and
verify_setup_glyph_pass.py produce and check this bounded pass. Source scripts
may refuse to change a signed checkpoint; work in a new review copy. Rendering
uses the existing local Pillow/resvg environment via CRAFTAGEDDON_RENDERLIB.

Full workflow templates and the rest of the objective remain open. See
REMAINING.md and source-owner-resource-map.json. This is a signed source/art
checkpoint, with V1/V2 limited to this scope and V3 pending.
'''
 (OUT/'README.md').write_text(readme,encoding='utf8')
 (OUT/'REVIEW.md').write_text('''# Setup glyph review — 28 October 2026

Reviewed the 18 cold/light-mask specimens. The language symbol uses an original
globe with no lettering. Restore and swipe cues retain the native rectangular
aspect ratios. Higher-resolution native layers support the actual Glif header
upscaling contract; original intrinsic dp values are separate from pixel sizes.
Density cache invalidation is declared in the renderer.

The preview's illuminated column is a mask/material demonstration. Native
header/cue glyphs remain cold; the source checked-button helper assigns the
on-state check glyph, and three source-backed actions allow momentary feedback.
Two glyphs with no positive local consumer stay unbound, not approved by absence.

All 630 unique production PNGs and native copies have current hashes; neutral
masks remain grayscale, and no glow or caption is painted into cold assets.
The 17 retained source path sets and one new globe are explicit. Source callbacks,
original Kotlin owners, permissions and manifest remain unchanged.

The three actual public Java rendering classes and resource bank compile.
State probes, native intrinsic-size oracle checks and real linked layer IDs
pass. This does not execute Android inflation, private setup owners or a device.
The complete privileged build, native layout, accessibility/performance,
partner/effective overlays and Thor display/input acceptance remain NOT RUN.
No Inkscape roundtrip or independent whole-goal review is claimed.
''',encoding='utf8')
 (OUT/'REMAINING.md').write_text('''# Remaining work after the setup glyph foundation

The goal remains ACTIVE. All 10,926 families / 16,559 variants are retained,
and 9,575 baseline semantic decisions remain OPEN. This pass closes none; its
new artwork is distinct from native acceptance or whole workflow completion.

W03 remains partial. All 56 previously open SetupWizard families remain open
until their complete content/owner disposition is recorded. Still required:
footer/switch/selection controls and screen frames, Glif/partner light/dark
styles, original adaptive/brand identity, live-English theme preview and
wallpaper composition, all three Lottie animations, finish/reveal/punch-through
composition, TV/wide variants, dialogs/popups and further dependency visuals.
Two prepared glyphs remain unbound pending a positive source-owner decision.

Full privileged platform/Soong/ABI/dex/R8, all 39 original Kotlin app owners,
native XML inflation/text/accessibility, effective overlays and Thor display/
input/performance acceptance are unrun. Public core/bank compilation does not
establish those gates. Preserve native footer disabled-button behavior and
wizard callbacks/settings in their real source classes. Device is deferred.

Continue partial W04/W05, unauthored W07, the complete unassigned/tentative reuse
corpus, all 16 named gaps and 20 original component roles, additional discovered
scope and final fresh independent whole-goal review. W01/W02/W06 source/art
handoffs do not establish final native acceptance. No hardware operation.
''',encoding='utf8')
 (OUT/'THIRD_PARTY_SOURCES.md').write_text('''# Source attribution

Craftageddon artwork/code is CC0. Exact LineageOS/AOSP/Google setup source,
Lottie inputs and other retained dependencies keep original licenses/notices,
including Apache-2.0 source headers. They are not relicensed CC0. Provenance
records give URLs, revisions, Git object identities and SHA256. Public SDK/JDK
compatibility tools and caches are not bundled. No private signing material is
included. Source-artifact signing is separate from Android/platform signing.
''',encoding='utf8')
 checks=read_json(OUT/'verification/evidence/current-glyph-source-checks.json');technical=dict(checks,components=18,date='2026-10-28',checkpointScope='First setup glyph source/art foundation only; full W03, wider semantics and native/device acceptance incomplete.',v1Scope='18 layered glyphs, explicit nonlettering language icon, original aspect/intrinsic dimensions,16 positive consumer bridges,2 unbound leaves retained, unchanged native operations and explicit remaining scope.',v2Method='Pinned source hashes,630 unique PNG/mask and native-copy checks, real public renderer/resource compilation,1536 state cases,18 original intrinsic-size oracles/126 real linked IDs, clean patch byte parity, desktop material review and prior canonical/archive preservation.')
 write_json(OUT/'verification/evidence/technical.json',technical)
 print({'textPatchFiles':len(clean),'uniqueProductionPngs':630,'nativeCopyPngs':630,'sourceGlyphMasters':18,'newSemanticClosures':0,'remainingOpenBaselineFamilies':9575,'wholeGoalComplete':False})
if __name__=='__main__':main()
