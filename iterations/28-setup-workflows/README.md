# Forge 28 — Setup glyph foundation

This is the local working pass for W03, based on published Forge 27 and the exact
LineageOS 24 SetupWizard revision 69174527a30bc72a28a5d55acdec8ce5edaba9e0.
The complete workflow is still being developed; this folder is not a finalized
or installed app.

The first artwork passes contain 18 editable glyph masters: 17 retain the actual
native path geometry, and one newly drawn globe replaces lettering in the
language symbol. 90 cold PNGs and 540 neutral masks remain separate, including 126
higher-resolution layers for enlarged native headers. Original intrinsic icon
dimensions are retained independently of texture resolution, with density cache
invalidation declared. Larger source glyphs keep their original proportions.

16 source-backed drawable bridges and three real Java rendering classes are
authored. The actual checked-button helper owns the glowing check mark;
momentary actions and cold header/cue symbols have explicit distinct modes.
The unbound eye/dialer glyphs are retained as artwork, with no native override
or approval inferred from missing local references.

The public renderer/resource bank compiles with SDK 37 compatibility checks.
1,536 state cases / 14,076 assertions, 18 original intrinsic-size checks and 126 actual
linked layer IDs pass. 130 exact app source/build/permission inputs and 52 exact
template sources/resources are preserved. All 39 original Kotlin owners, original
manifest, permissions and setup/settings actions remain unchanged. No source
activity or hardware operation is executed.

Remaining work includes the screen templates and native footer/switch/selection
controls; actual light/dark/partner styles; the full adaptive and brand identity;
theme preview/wallpaper composition with live English labels; all three Lottie
resources and their motion; finish/reveal/punch-through composition; TV/wide
variants, dialogs/popups and further dependency visuals; full privileged Soong,
native inflation/text/accessibility, effective overlays and Thor display/input
acceptance. The footer's native disabled-button and callback behavior must remain
in its original classes.

The original 63 SetupWizard families remain conserved, with 56 still OPEN; this
working pass has not recorded new semantic closures. The wider 9,575-family review
and final independent whole-goal double-check remain unfinished.

See source-owner-resource-map.json, setup-art-components.json,
setup-glyph-bindings.json, source/setup-template-contracts.json and
verification/evidence. The current preview is
previews/setup-source-glyphs-pass1.preview.png; it demonstrates independent
material/light layers and is not a native Android screenshot. All captions remain
live English text in the eventual native presentation, not painted lettering.


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
