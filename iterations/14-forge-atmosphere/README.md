# Reference Forge 14 — wallpapers and system atmosphere

22 October 2026. Work-in-progress visual checkpoint extending the accepted cold steel and separate ember system into the remaining atmosphere surfaces. Native integration is now authorized, and the user selected **official LineageOS 24.0 / AYN odin2thor** as its baseline. This artwork checkpoint does not claim that native integration has started or that the whole visual roadmap is complete.

## Artwork

- Six layered wallpaper surfaces: upper 1920×1080, lower 1240×1080, and shared phone 1080×2400, each in standard/quiet variants. Upper/lower pixel sizes are grounded in official device wiki data; they do not establish dp, insets, measured brightness, or fixed display IDs. Phone is a design canvas.
- Three editable, transparent atmosphere components: an original forged-anvil crest, sculpted charging chamber and loading aperture. The chamber reuses the previous accepted power-core cold raster unchanged, embedded for reliable rendering and retained separately with its source hash.
- Seventeen editable scene concepts: boot cold/assembly/ready/error; charging disconnected/connected/25/50/limit/full/thermal/unavailable; recovery menu/update/rejected update; loading active/error.
- Seven separate layers per component and wallpaper: cold, reflection, spill, seam, core, focus and symbol. The three components have 1x/2x transparent layer exports and eight state previews. Wallpaper layers export at their declared pixel sizes. Cold wallpaper PNGs are directly usable backgrounds; dynamic ember compositing still requires a native wallpaper/rendering owner.
- `index.html` presents scene and wallpaper previews. `masters/` contains layered SVGs; `exports/` contains production layers; `scenes/` holds SVG/PNG compositions; `previews/` contains review sheets and labelled lit wallpaper previews.

All scene text and percentages remain editable SVG text. Their values are visual fixtures, not actual boot progress, installed firmware values, charging measurements or recovery operations. Recovery artwork does not approve installation of a package whose signatures fail.

## Cold and selected rules

Production cold bases contain no baked orange light. Neutral light masks are tinted only for the labelled state/scene previews. Off/hover remain identical to cold. Focus alone stays cold. Limit/thermal/unavailable charging examples remain unlit; active charging and selected boot scenes light separate layers. Reduced motion stays static. Wallpaper focus/selection markers are owned by the launcher rather than painted into the background.

This pass supplies static production artwork and scene variants. Actual boot animation, charging timeline, transition behavior, the earlier 114-recipe reconciliation and lifecycle/performance acceptance remain separate pending work. A rendered scene or static atlas is not claimed as a completed animation.

## Review and verification

`REVIEW.md` records material/layout passes; `verification/evidence/technical.json` records bounded source/export checks. V1/V2 apply only to the declared desktop artwork. Device V3, controller/touch behavior, native layer parity, text scaling/RTL and performance remain NOT RUN. The source builder refuses to overwrite a packaged iteration; `--resume-draft` only permits repair of an unpackaged draft.

Factory ROM and signing research is kept separately in `integration/research/2026-10-22/` at repository root. Factory firmware bytes and private signing material are not included in this artwork package. SVG/PNG source ZIPs are not Android install packages and do not acquire APK/OTA trust from a checksum.

## Rebuild

From the repository root, using the pinned requirements and a configured `CRAFTAGEDDON_RENDERLIB` where needed:

```powershell
python tools/build_forge_atmosphere.py build-work/atmosphere-rebuild
python tools/verify_forge_atmosphere.py build-work/atmosphere-rebuild --node node
```

Keep the folder structure when opening SVGs in Inkscape. Cold texture links remain relative; the sculpted chamber image is embedded and its unchanged original is retained under source/. Generated exports are inside the complete ZIP rather than the Git checkout. GitHub transport parts, when present, reconstruct that exact ZIP with checksums.
