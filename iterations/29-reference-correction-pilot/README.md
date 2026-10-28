# Reference correction pilot 0.1.0

Four editable correction samples, prepared after the material-drift audit. This is a bounded visual proposal for review, not a replacement of the full library or a native release. Source baseline: repository commit 201cf855b71a407bf1e314c654622a370e93f7b8.

## Compare the results

- `previews/correction-comparison.png`: previous cold finish, corrected cold finish, and corrected on-state. Small strips show cold, on, focus-only, and disabled samples. The 24px and 32px strips are rendered at 1x; the 96px and 128px strips are reduced to fit and their complete 1x files are in `previews/states/`.
- `previews/original-reference-strip.png`: original sculpted masters composed with the pilot's steady lighting recipe, for direct material comparison.
- `source/original-nine-motifs-reference.png`: unchanged original nine-motif reference sheet.

## What changed

1. Location: retain the native pin and hole, restore full forged texture at an appropriate scale, add two restrained copper fasteners and inset, interrupted ember channels. Original face silhouette retained; decorative details and light routing changed.
2. Close control: retain the original crossed paths and 32px canvas, replace the bright neutral stroke with dark textured steel. A local warm-gray bevel adjustment improves small-size visibility without restoring the silver/blue fill. Stroke treatment changed; centerline geometry retained.
3. Photo frame: preserve its 96px canvas and 84px chamfered transparent opening, restore textured steel, increase corner fastening detail and split the recessed channels before the corners. This remains a vector specimen: a replacement scalable Android nine-patch and stretch validation are not included.
4. Gallery badge: retain the central source image glyph, restore its rough steel surface, thicken the forged outer housing, enlarge copper braces and interrupt ember arcs at the braces. Existing app identity and source mappings are unchanged. Its glowing state is an artwork demonstration; it does not authorize permanent glow on an app icon.

The same original texture and ember colors are used. No AI image generation was used for this correction. Metal and neutral lighting layers remain separate. English labels on the sheets are preview annotations; no visible text is baked into the individual production layers.

## Files and behavior

- Four portable layered SVG masters, with the original texture embedded.
- Twenty-eight individual SVG layers.
- Eighty-four transparent PNG layers: four samples x seven layers x three scales (1x/2x/3x).
- Steady preview states: cold, on, focused off, selected and focused, pressed off, disabled, and reduced-motion on.
- Off, focus-only and pressed-off states do not activate ember. Disabled is cold and dimmed. Reduced motion is static.
- `runtime-style.json` documents illustrative composition; no Android renderer or state owner was changed.
- `source/before/` contains portable material-before SVGs. Their texture links were embedded for portability; the exact original files and hashes are recorded in `components.json`.

## Validation and limitations

Technical checks cover layer counts, transparency, grayscale neutral masks, artifact hashes, and off/reduced-motion composition. The comparison was visually inspected and refined for texture scale, cold visibility and recessed lighting. Luminance measurements are observations, not accessibility certification.

The original large sculpted motifs remain richer than small native glyphs. This pilot does not claim exact equivalence or user approval. V1 final visual acceptance is pending; V2 automated asset checks have run; V3 independent renderer/device validation is NOT RUN. The tracked release gate remains draft. Do not apply the treatment to the remaining assets or call the style correction complete based solely on the automated checks.

No earlier iteration, shared generator, native source, resource binding, device or latest pointer was changed. Rollback consists of not adopting this isolated pilot. The remainder of the 98-master material correction and the compact-variant usage audit remain open.

## Reproduce

Run `tools/build_reference_correction_pilot.py` from the repository with the existing Pillow and resvg_py environment (`CRAFTAGEDDON_RENDERLIB` points to the existing render-library folder). The builder refuses to rewrite a packaged pilot. The source script is included in `source/` for reference; run the repository copy because it uses the existing repository source inputs and authoring helpers.
