# Forge 24 — updater card foundation

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
