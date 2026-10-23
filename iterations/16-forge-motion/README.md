# Reference Forge 16 - motion artwork checkpoint

This checkpoint supplies a runnable offline motion sampler and editable artwork for the retained 114-entry catalog. All authored wording is English (en-US), with 352 native Android string resources. This is a source/design checkpoint, not an installed application or ROM release.

- 30 new unlabelled SVG masters, alongside 58 unchanged mapped sources.
- 103 animated recipe dispositions and 11 deliberately steady status indicators. Original IDs, durations and repeat metadata are retained.
- 420 transparent production layer exports: cold, reflection, spill, seam, core, neutral focus and selection symbol, at 1x and 2x. Earlier bounded draft exports are retained separately in the exports folder.
- 1,140 SVG/PNG sampled desktop frames and 114 filmstrips. Six catalog sheets show every recipe at a representative pose.
- 32 sampler, clock, part and semantic tests; byte provenance, mask neutrality, live-text bounds and independent fixed-vessel/fan pixel checks.
- Default native English strings, a compiled resource handoff, source provenance and bounded verification evidence.

Open index.html manually to use the review controls, or inspect masters/ and source/portable-masters/ in Inkscape. Raw original-masters preserve their original byte contents and path references; use portable-masters for direct editing with the included unchanged rasters. The viewer runs locally and contains no hardware commands. Select a recipe, switch Selected / on, then replay. Off/unselected remains cold; focus is neutral. Reduced motion shows the settled state. Leaving or hiding the viewer cancels playback and returning does not resume it.

The complete-assets.zip archive contains all current sources, layer exports, sampled frames, review sheets, runtime and evidence. Its detached signature and public key authenticate the Craftageddon source-artifact identity. This is separate from APK, OTA or AVB signing. distribution/ contains transport parts and a checksum-verifying restore script for GitHub; local deliverables retain the full ZIP.

Regenerate from the repository root with the builders in tools/: build_forge_motion_composites.py, forge_motion_bindings.py via the retained catalog, build_forge_motion_viewer.py, build_forge_motion_text.py, export_forge_motion_frames.cjs and render_forge_motion_frames.py. The retained source catalog is hash-bound and original mapped masters and PNG bytes are preserved under source/. The archive is usable offline; full regeneration also uses the repository's earlier source iterations and local documented rendering tools.

Browser playback could not be reviewed because automated local-file access was rejected by the browser security policy. No alternate browser/network workaround was attempted. Native rendering, display routing, controller input, hardware services, performance, accessibility and target V3 remain NOT RUN. Fixture labels such as temperature, fan speed, touch mapping and trigger values are artwork examples rather than device readbacks. No device was installed, modified or flashed.

Historical family reconciliation, exact installed-app targets and the final target-scale review remain distinct work in the active roadmap. The native integration target selected by the user is official LineageOS 24.0 for AYN odin2thor.
