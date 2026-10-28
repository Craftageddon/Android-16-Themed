# Setup workflow rework in progress

This is the local working pass for W03, based on published Forge27 and the exact
LineageOS24 SetupWizard revision69174527a30bc72a28a5d55acdec8ce5edaba9e0.
The complete workflow is still being developed; this folder is not a finalized
or installed app.

The first artwork passes contain18 editable glyph masters:17 retain the actual
native path geometry, and one newly drawn globe replaces lettering in the
language symbol.90 cold PNGs and540 neutral masks remain separate, including126
higher-resolution layers for enlarged native headers. Original intrinsic icon
dimensions are retained independently of texture resolution, with density cache
invalidation declared. Larger source glyphs keep their original proportions.

16 source-backed drawable bridges and three real Java rendering classes are
authored. The actual checked-button helper owns the glowing check mark;
momentary actions and cold header/cue symbols have explicit distinct modes.
The unbound eye/dialer glyphs are retained as artwork, with no native override
or approval inferred from missing local references.

The public renderer/resource bank compiles with SDK37 compatibility checks.
1536 state cases/14076 assertions,18 original intrinsic-size checks and126 actual
linked layer IDs pass.130 exact app source/build/permission inputs and52 exact
template sources/resources are preserved. All39 original Kotlin owners, original
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

The original63 SetupWizard families remain conserved, with56 still OPEN; this
working pass has not recorded new semantic closures. The wider9575-family review
and final independent whole-goal double-check remain unfinished.

See source-owner-resource-map.json, setup-art-components.json,
setup-glyph-bindings.json, source/setup-template-contracts.json and
verification/evidence. The current preview is
previews/setup-source-glyphs-pass1.preview.png; it demonstrates independent
material/light layers and is not a native Android screenshot. All captions remain
live English text in the eventual native presentation, not painted lettering.

