"""Record W06 source/artwork authoring while retaining every full-goal obligation."""
from pathlib import Path
import collections, hashlib, json, shutil
from audit_os_resource_coverage import ROOT, read_json, write_json

OUT=ROOT/'iterations/23-magnification'
BASE=ROOT/'iterations/22-native-contract-review'


def main():
    assert not (OUT/'complete-assets.zip').exists()
    checks=read_json(OUT/'verification/evidence/source-art-checks.json');assert checks['result']=='PASS'
    ledger=read_json(BASE/'semantic-family-ledger.json');bindings=[];delta=[]
    for row in ledger:
        b=row['baselineFamily']
        if b['project']!='frameworks/base' or b['resourceRoot']!='packages/SystemUI/res' or 'magnif' not in b['name']:continue
        assert len(row['evidence'])==1
        if b['kind']=='color':
            bindings.append({'familyId':row['familyId'],'source':b,'decisionKept':row['decision'],
                 'role':'Old palette selector bypassed by the patched magnification widgets; other consumers and global token treatment still require review.','wholeFamilyAuthoredHere':False});continue
        binding={'familyId':row['familyId'],'source':b,'sourceEvidence':row['evidence'],
                 'role':'Actual magnification layout/glyph/material binding or precise native procedural border geometry.',
                 'sourcePatch':'SystemUI-magnification-forge.patch','checks':'verification/evidence/source-art-checks.json',
                 'stateOwner':'Original selected presets, checked switches, settings-panel visibility and native gesture lifecycle. Fullscreen/window borders exist only in the active owner lifecycle.',
                 'wholeFamilyAuthoredHere':True,'nativeDropInApproval':False,'fullSoongOrDeviceAcceptance':'NOT RUN'}
        if row['decision']=='OPEN':
            old=row['decision'];row['decision']='OWNER_PRESENTATION_ADAPTATION_AUTHORED'
            row['requiredAction']='Use the23 owner-specific source/art handoff; full pinned SystemUI build, actual inflation, per-display/device rendering, input and accessibility acceptance remain separate.'
            row['rationale']='Exact source geometry, labels, owner state/callbacks and data surface reviewed; new steel/mask resources and procedural native border bridge are authored with bounded checks.'
            delta.append({'familyId':row['familyId'],'previousDecision':old,'decision':row['decision'],
                          'source':b,'sourceEvidence':row['evidence'],'ownerBinding':binding,
                          'runtimeValidationComplete':False})
        binding['decisionKept']=row['decision'];bindings.append(binding)
    assert len(bindings)==29 and len(delta)==25
    assert len(ledger)==10926 and sum(len(r['evidence']) for r in ledger)==16559
    counts=collections.Counter(r['decision'] for r in ledger);assert counts['OPEN']==9630
    write_json(OUT/'owner-binding-review.json',bindings);write_json(OUT/'semantic-review-delta.json',delta)
    write_json(OUT/'semantic-family-ledger.json',ledger)
    progress={'date':'2026-10-26','familyRecords':10926,'sourceFileVariants':16559,'previousOpenFamilyDecisions':9655,
              'newContentBackedOwnerDecisions':25,'preservedReferenceContractsWithNewOwnerBinding':2,
              'legacyPaletteSelectorsStillOpen':2,'openFamilyDecisions':9630,'decisions':dict(counts),
              'workflowAdaptationsAuthoredPreviously':['W-01','W-02'],'workflowAdaptationsAuthoredHere':['W-06'],
              'workflowAdaptationsStillUnauthored':['W-03','W-04','W-05','W-07'],
              'sourceArtAuthoringDoesNotEstablishNativeAcceptance':True,
              'wholeSemanticReviewFinished':False,'fullGoalComplete':False,
              'finalWholeGoalDoubleCheck':'NOT RUN - full corpus/art/owner scope remains unfinished',
              'unclosedScope':'Other source families, shared/global resource and token roles, source-specific artwork, native app/glyph owner bridges, W03/W04/W05/W07, further discovered artwork, full target gates and the final independent whole-goal check remain.'}
    write_json(OUT/'semantic-review-progress.json',progress)
    inventory={'date':'2026-10-26','newAuthoredTreatments':23,'nativeSourceGeometryTreatments':16,
               'newControlGeometry':7,'exactReusedPanelMasters':1,'proceduralBorderParameterExamples':3,
               'proceduralBorderRuntimeImplementations':1,'newNativePngConfigurations':644,
               'reusedPanelPngConfigurations':28,'coldMaterialTiles':1,'layerNames':['cold','reflection','spill','seam','core','focus','symbol'],
               'sourceBackedSvgPngWorkflowFixtures':9,'newJavaRenderingSupportClasses':3,'actualSourceOwnersModified':5,
               'nativeLayoutsModified':3,'productionBakedEmberRasters':0,'productionBakedLabels':0,
               'scope':'Counts distinguish source geometry/material treatments, new control drawings, exact reuse, procedural parameter snapshots, density exports and workflow previews.'}
    write_json(OUT/'asset-inventory.json',inventory)
    technical={**checks,'checkpointScope':'W06 magnification source/artwork handoff: cold steel and neutral masks, precise procedural border geometry, actual owner states, live English labels, responsive header and48dp declared input targets. Not a finished full-corpus or Android release.',
               'v1Scope':'Actual fullscreen/window/edit/preset/switch/zoom/legacy-control roles traced; source state, input deltas/timing, mirrored-data surface, native corner/dash values and real scale-property path retained. Global shared glyph resources are not overridden. Full10926-family baseline and remaining work are explicit.',
               'v2Method':'Clean actual patch application and byte parity;68 pinned source hashes;644 new neutral/cold configurations and28 exact panel resource aliases; native compile/link of rendering bank and three real Java classes;10164 native-geometry method cases,384 color-state cases,140 nine-patch size checks,521 density cases for disjoint48dp directional targets, unchanged SurfaceView subtree, contrast/source English checks and9 strict-XML source-backed fixtures.',
               'fullGoalComplete':False,'targetV3':'NOT RUN - full pinned SystemUI build, native layout inflation/rendering/input/accessibility and device comparison remain open.'}
    write_json(OUT/'verification/evidence/technical.json',technical)
    shutil.copy2(BASE/'signing-public-key.pem',OUT/'signing-public-key.pem')
    shutil.copy2(ROOT/'iterations/21-native-workflows/source/LICENSE-APACHE-2.0.txt',OUT/'source/LICENSE-APACHE-2.0.txt')
    write_json(OUT/'source/reference-baseline.json',{'repository':'LineageOS/android_frameworks_base','revision':'7f6de40b6429462d47ba9ba351b99943269c8067',
               'officialManifest':'integration/research/2026-10-23/official-20261019-build-manifest.xml',
               'manifestSha256':'4bf203ee7ab8b663d0bf6c83d3e35bd349222d3ca228940df191e2aff50d2364',
               'lineageTarget':'24.0 / Android17 / API37 / AYN odin2thor',
               'referenceGraph':'iterations/22-native-contract-review/resource-reference-graph.json.gz',
               'deviceFacts':'No connected-device facts or physical radius/density are invented; runtime owners/resources retain those inputs.'})
    (OUT/'README.md').write_text('''# Forge23 magnification artwork and native source handoff

W06 now has actual-owner artwork/source adaptations for fullscreen and window magnification, dashed size editing, resize/drag/Done controls, preset/switch/zoom settings and the retained directional controller. Off controls are cold steel; actual checked/selected/pressed or settings-panel state drives separate neutral masks and runtime color. Native English labels remain live.

## Inventory and evidence

-23 authored treatments:16 source-geometry material treatments and7 new control drawings. The27 master-directory SVGs also include one exact panel alias and three procedural-border parameter examples; those are not27 unrelated new drawings.
-644 new native PNG configurations,28 exact panel resource aliases and one cold material tile. Production color/glow stays separate; previews may show composed ember.
-Three actual new Java rendering/support classes, five modified actual SystemUI owners and three modified native layouts. Skin resources compile/link against API37. The private-platform owners and full layouts are not claimed as a full SystemUI build or executed Android UI.
-Nine editable SVG/PNG workflow fixtures show actual source English strings and state/visibility roles. They use desktop font/measurement approximations and are not Android screenshots. The fullscreen radius shown is illustrative; the unchanged owner supplies actual display radius at runtime.

The native border renderer preserves half-stroke inset/radius clamping from pinned GradientDrawable, normal28/30dp and edit16/18dp resource radii,20/20dp edit dashes, fullscreen12dp total stroke and6dp visible stroke/offset defaults, and actual context resources/density. Its light rail stays within the original shell. No mirrored image content is tinted or replaced. Fullscreen remains a GradientDrawable subtype for the original corner updater; custom/Wear backgrounds keep their existing exception.

Resize handles declare48dp targets around26dp visible housings. The optional directional controller has four separate48dp targets in a window sized to three measured target widths, with native short/long movement and100ms repeat unchanged. Hidden control rectangles are excluded from the window's touch region, preventing invisible enlarged handles from intercepting underlying content. The48dp Done editing target adds an accessibility click for the existing touch action. Native nonfocusable overlay/window flags and input routing stay intact; no game input capture or device/controller execution is claimed.

The settings header stacks using actual native text measurement when space is tight. Done grows with native text height and stays outside the original scroll body. Switch-track padding is zero to retain the full20dp declared thumb travel. Six shared global glyph resources remain untouched; magnification binds its own treatments instead. The misleading ic_open_in_new_window source contains a settings gear and is treated accordingly. Native scale data still reads ro.config.max_magnification_scale; fixtures use its8.0 default without asserting the product property.

## Apply and reproduce

Use SystemUI-magnification-forge.patch against the pinned frameworks/base/packages/SystemUI source. Copy the hash-listed PNG entries from native-patch to the same module resource paths; binaries are intentionally outside the text patch. Existing source/license files are preserved under upstream; derivative glyph geometry keeps its original Apache-2.0 provenance and notices. Project material/control additions use the repository terms; CC0 does not relicense upstream geometry/code.

Run fetch_magnification_owners.py, build_magnification_art.py, prepare_magnification_patch.py, compile_magnification_resources.py, render_magnification_fixtures.py, verify_magnification_checkpoint.py, then prepare_magnification_checkpoint.py from the repository tools. Builders refuse to rewrite a packaged checkpoint. Set CRAFTAGEDDON_RENDERLIB to the already installed rendering-library directory; use the recorded existing Python/Pillow/resvg, JDK and SDK37. The Windows SDK compiler requires host execution outside this sandbox. No installation, upstream code execution on hardware, flashing or settings change occurs. Verification JARs/resource banks are not runtime packages and their generated IDs are compile-only.

V1/V2 pass only for the stated source/art/compile scope: source and clean-patch byte parity, masks/alpha, source geometry, state selectors, native rendering-class compilation, host geometry and target calculations, real resource compile/link, source labels and inspected fixtures. Full pinned Soong, native layout inflation, actual Android/device/input/accessibility/performance acceptance and V3 remain NOT RUN.

The complete10926-family/16559-variant goal remains active. This checkpoint records25 new owner decisions and retains two already-preserved inset contracts with their actual owner bindings.9630 family decisions, W03 setup, W04 updater, W05 gallery, W07 boot/charger/recovery, other required art/owner work and the final independent whole-goal double-check remain open.
''',encoding='utf8')
    (OUT/'REVIEW.md').write_text('''# Review scope

Multiple passes inspected the cold and active glyph sheet, owner panels, compact large-text scrolling, size editing and fullscreen border fixtures. Cold glyphs were brightened after pixel inspection; every source-glyph xhdpi opaque-pixel median is at least3:1 against the declared well. This statistic and nominal text contrast do not prove blanket WCAG or Android/device acceptance. PNG masks are neutral; all authored visible text is English, and production skins contain no labels.

Five actual owners carry explicit change notices: FullscreenMagnificationController, WindowMagnificationController, WindowMagnificationSettings, MagnificationModeSwitch and SimpleMirrorWindowControl. Exact reverse-edit and clean Git patch application checks prove the source changes are confined to the recorded bindings, responsive header, press presentation, accessibility close action, control target size and visible-target gating. Gesture accumulation, source crop, movement/scale callback bodies, repeat task and lifecycle/rotation/window flags are retained; the untouched source classes are preserved separately. Full hidden-platform owner compilation remains unrun.

The legacy palette selectors remain OPEN because other/global uses are not approved from this owner handoff. Shared add/remove/fullscreen/resize/gear resources are not globally overridden. The old magnification-prefixed sources receive explicit owner roles; exact wrapper preservation is retained where already reviewed. Frozen earlier checkpoints and all472 earlier canonical masters remain intact.

The final full-goal double-check is NOT RUN. Remaining9630 family decisions, four workflow groups, additional artwork and owner bridges stay required. No source/desktop check is promoted to physical Thor validation or a production ROM release.
''',encoding='utf8')
    # Keep human documentation readable without altering source identifiers or dimensions.
    replacements={'-23 ':'- 23 ','-644 ':'- 644 ','-Three ':'- Three ','-Nine ':'- Nine ',
        'treatments:16 ':'treatments: 16 ','and7 ':'and 7 ','The27 ':'The 27 ','not27 ':'not 27 ',
        'configurations,28 ':'configurations, 28 ','normal28/30dp':'normal 28/30dp',
        'edit16/18dp':'edit 16/18dp',',20/20dp':', 20/20dp','fullscreen12dp':'fullscreen 12dp',
        'and6dp':'and 6dp','declare48dp':'declare 48dp','around26dp':'around 26dp',
        'separate48dp':'separate 48dp','and100ms':'and 100ms','The48dp':'The 48dp',
        'full20dp':'full 20dp','its8.0':'its 8.0','complete10926-family/16559-variant':'complete 10,926-family/16,559-variant',
        'records25 ':'records 25 ','bindings.9630':'bindings. 9,630','at least3:1':'at least 3:1',
        'all472 ':'all 472 ','Remaining9630 ':'Remaining 9,630 '}
    for name in ['README.md','REVIEW.md']:
        file=OUT/name;text=file.read_text(encoding='utf8')
        for old,new in replacements.items():text=text.replace(old,new)
        file.write_text(text,encoding='utf8')
    print(json.dumps({'newOwnerDecisions':len(delta),'openFamilyDecisions':counts['OPEN'],'authoredWorkflowGroup':'W-06','remainingWorkflowGroups':['W-03','W-04','W-05','W-07'],'fullGoalComplete':False}))


if __name__=='__main__':main()
