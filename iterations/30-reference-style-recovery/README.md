# Reference style recovery 0.2.0 — review checkpoint

This extends the four-sample correction pilot to all 98 confirmed material-drift masters, plus the bright AYN live-position ring. The visual anchor remains the original sculpted nine-motif sheet and the isolated iteration29 pilot. This is a reviewable artwork bank, not an installed Android theme or a final style approval.

Open `index.html` for all corrected artwork, or `previews/recovery-overview.png` for representative before/cold/on comparisons. Nine group sheets cover every corrected master. `workflow-review/` contains71 refreshed English offline screen specimens; these are not Android screenshots.

## Corrected scope

| Group | Masters | Separate PNG configurations |
|---|---:|---:|
| Magnification |16|448|
| Updater |11|312|
| Gallery |53|1,484|
| Setup |18|630|
| AYN position marker |1|21|
| Total |99|2,895|

The PNG count consists of413 cold configurations and2,482 neutral light/focus/selection/motion masks. These are density/layer variants, not2,895 separate drawings. Gallery27's53 identical masters are mapped to the same corrections without being counted again.

Three additional magnification border parameter examples have corrected bevel colors. A source proposal changes exactly six color literals in `ForgeMagnificationBorderDrawable.java`; all path calculations, bounds, states, alpha behavior, callbacks and shader operations are unchanged. That proposal has not been compiled, installed or applied to a ROM.

## What the correction does

- Restores dark forged edge colors and the texture fills removed by the later brightening helper.
- Restores full texture coats while retaining original per-path opacity roles and source silhouettes.
- Sizes texture grain to the local geometry instead of magnifying a coarse patch over small symbols.
- Narrows inherited glyph spill/reflection blur toward the original reference proportions. Cold material, reflection, spill, seam, core, focus, selection and updater motion remain separate.
- Reuses all four prior pilot treatments, including the inset location channels and reinforced Gallery housing.
- Preserves resource dimensions, setup aspect ratios, higher-resolution header exports and all28 nine-patch metadata borders.
- Keeps native English labels live in the source workflow. Standalone production artwork contains no painted captions. Existing semantic error colors, RGB data, synthetic photo samples and native feature-state owners are unchanged.

The original detailed hero artwork is still more sculpted and ornate than tiny native symbols. This pass corrects the confirmed material and bloom drift; it does not claim to reproduce every hero detail at24px or close the broader OS artwork roadmap.

## Compact symbols

`compact-mask-role-audit.json` records183 compact files, representing181 distinct contents, and their183 detailed counterparts. The compact branch explicitly supplies neutral/tintable geometry. Those masks remain unchanged. The detailed counterpart is the intended forged presentation reference; this structural pairing does not approve every installed owner/tint placement. Do not blanket-darken neutral status or adaptive-monochrome masks.

## Using the files

- `masters/<group>/`:99 editable SVGs, plus three border parameter examples. The shared material texture is in `source/steel-material.png`; keep the folder structure when opening a master in Inkscape.
- `layers/<group>/`: separate editable SVG layer files. Only cold artwork references the material texture; neutral masks contain no material-image payload.
- `resources/<group>/drawable-*/`: individual transparent production-format PNGs with the existing resource filenames and dimensions. No native resources were overwritten.
- `components.json`: source hashes, corrected hashes, dimensions and explicit old-resource-to-new-resource mappings.
- `gallery27-alias-map.json`: the equivalent Gallery27 master mappings. For Gallery27 resource aliases, substitute its iteration directory in the Gallery26 source entries and verify the prior resource hash.
- Setup28's `nativeHighResolution` exports are represented under `drawable-nodpi`. Its duplicate native-patch PNG locations use the corresponding identical artwork replacement; copies are not extra designs.
- `native-appearance-proposal/`: the proposed magnification drawing-color patch and exact source/resource/remaining-acceptance inventory.
- `source/provenance-inputs/`: the referenced available original masters/geometry and their material image dependencies, copied without editing. `source/provenance-inputs.json` records hashes.

Adopting the bank into the source builds remains a distinct step: review the material first, verify each old hash, replace only the mapped resources, and repeat compile/inflation/device checks. Do not infer current build acceptance from earlier iteration reports.

## Validation and remaining work

The saved-output checker reopens all2,895 PNGs, verifies all2,482 masks are grayscale, compares source/corrected dimensions and all28 nine-patch metadata borders, tests each nine-patch at three expanded sizes, checks unchanged generic path data, verifies reduced-motion parity, rehashes3,659 earlier sources and checks753 English text nodes across71 refreshed specimens. All pass.

All99 masters were inspected through the nine group sheets, with additional scene checks for Gallery selection, updater checking, magnification selection and AYN calibration. This is an internal correction review. User visual acceptance remains PENDING. Small inactive symbols need final contrast/optical checks on the Thor. Full Android typography, tint ownership, privileged compilation, effective overlays, inflation, input, dual-screen behavior and device performance remain NOT RUN. The six-color native border proposal is uncompiled. Independent final validation remains PENDING; the checkpoint is not FINALIZED.

Earlier checkpoints, main, native bindings, semantic ledgers and latest pointers remain unchanged. Rollback is to retain the prior bank and not adopt this separate iteration. No device or hardware operations occurred.

## Reproduce

Use the existing Pillow/resvg environment and run repository tools in this order:

1. `tools/build_style_recovery.py`
2. `tools/render_style_recovery_workflows.py`
3. `tools/verify_style_recovery.py`
4. `tools/package_style_recovery.py`

`CRAFTAGEDDON_RENDERLIB` points to the existing rendering-library folder. The first tools refuse to overwrite a packaged checkpoint. All authoring tools used here are included in `source/tools/`; their imports and pinned prior inputs remain in the repository baseline. The source base for this iteration is published pilot commit `b085fbc64b77b3fd7da775edf1f050e4c6d6c6fb`.
