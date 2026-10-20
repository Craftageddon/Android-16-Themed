# Craftageddon Android 16 — Ember Steel

An iterative redesign of the Craftageddon Android interface for AYN Thor, based on the earlier dark forged steel and ember artwork.

## Iterations

| Checkpoint | Scope | State |
|---|---|---|
| [01 — Material pilot](iterations/01-material-pilot/) | 18 layered component specimens, cold bases, neutral emission masks, seven state previews | Desktop design checkpoint |

![Material direction](art-direction/ember-steel-study.png)

The material study above is AI-generated reference art. It defines the intended richness of larger artwork; it is not a production atlas and must not be sliced into controls. The editable pilot deliberately simplifies detail for everyday controls. Each later iteration records what improved and what remains unresolved.

![Component pilot](iterations/01-material-pilot/previews/pilot-sheet.png)

## Use the assets

Open any `masters/*.svg` in Inkscape. The named layers are `cold`, `seam`, `core`, and `symbol`. Seam/core layers are hidden in the master, white in the separate mask exports, and tinted only for state previews. Text in contact sheets is illustrative; production text stays live in Android. Both 1x and 2x PNG layers have real alpha.

Every iteration includes `complete-assets.zip` containing its full folder, including the transparent PNG exports. Individual editable SVGs and preview sheets are also browsable in the repository. Extract the archive into an empty folder to use the full pack or run its checksum audit.

```powershell
python -m pip install -r requirements.txt
python tools/build_pilot.py --iteration 1 --out build-work/01-material-pilot
python tools/verify_pilot.py build-work/01-material-pilot
```

Build into a new folder; the builder refuses to overwrite archived iterations. The geometry/export build is portable; contact-sheet font rasterization can differ when Segoe UI is unavailable.

## Scope and integration

The [103-package roadmap](roadmap/REWORK_PLAN.md) covers the whole library and [Thor/LineageOS](roadmap/THOR_AND_LINEAGEOS_PLAN.md). These commits begin its design phases. They do not claim native SystemUI integration, actual gamepad mapping, working hardware controls, or completed ROM work. No device has been modified or flashed. Device verification remains blocked until an exact firmware/hardware baseline and test access exist.

Cold bases must remain free of baked emission. Compact status glyphs use simpler, steady geometry. Selected controls have a geometric cue; focus remains visible alongside selection. Reduced motion is static. Touch targets need native padding to at least 48dp even when the visible glyph is smaller.

## License and provenance

The repository's original [CC0 1.0 license](LICENSE) is retained. New geometry, tooling and generated study art are supplied under that repository license. Historical local references inform the design but are not bundled as production assets. No third-party font binaries, application logos, vendor firmware or proprietary mapping tools are included. See [art direction](art-direction/README.md).
