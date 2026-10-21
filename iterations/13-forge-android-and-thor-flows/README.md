# Reference Forge 13 — Android flows and Thor panels

Work-in-progress art checkpoint, 21 October 2026. **42 new editable screen concepts and 18 new layered control masters.** This extends the accepted blackened-steel material into missing everyday Android flows and Thor panels. It does not mark the full visual roadmap complete.

Open `index.html` for the searchable offline gallery, `screens/*.svg` for editable compositions, or `masters/*.svg` in Inkscape for individual controls. Screen PNGs are labelled concept previews. Sources use one relative cold texture link; keep the folder structure intact. All labels and values in the SVG scenes remain editable text. Font metrics were checked with Windows Segoe UI; font fallback and Android rendering remain separate work.

## Included

- **25 Android scenes:** app drawer; open folder; widget picker; search results/empty; Settings home/display; recents/empty; power menu; camera permission; privacy dashboard; photo picker; file picker/error; share sheet; clipboard; screenshot editor; volume/output; PIN; pattern; biometric; symbol and number keyboards; split-layout chooser.
- **17 Thor scenes:** trigger modes; button mapping; virtual mouse; touch mapping; game profiles; mixed profile readback; independent displays; keyboard destination; lid/resume; capture selection; performance/cooling; thermal warning; charging preferences; lighting zones; controller diagnostics; unavailable hardware fallback; eight-direction/tap/hold/chord prompt sheet.
- **18 unlabelled components:** PIN key, pattern node, biometric socket, volume rail, app socket, folder socket, task card, media cell, suggestion cap, chord link, stick gate, trigger gauge, mapping slot, display pair, thermal gauge, charge limit, lighting zone, unavailable plaque. Some are reusable supporting specimens rather than placed scene elements.
- Every component has **seven layers**, 1x/2x transparent exports and **eight state previews**. Component PNG exports live in the complete ZIP; generated export directories are excluded from the Git checkout.
- Every scene has a separate cold-material inspection render. These inspections hide emission without changing the illustrated selected values; they are **not off-value state variants**.

## Material and states

Cold is the unchanged previous material sampled through new original SVG geometry: deeply dark steel, carved channels, copper joints and restrained bevel highlights. No new raster was generated or repainted in this pass. This continues the scalable interface treatment; it does not claim every small symbol now has the same sculpted depth as the nine large hero motifs.

`cold` stays visible in masters. `reflection`, `spill`, `seam`, `core`, `focus` and `symbol` are separate hidden neutral-white layers. The state driver tints them only for previews/runtime handoff. Off and hover remain byte-identical to cold; focus brackets alone do not ignite. Selected/checked/on emit; active press uses stronger gains; disabled dims the base; reduced motion is static. The unavailable plaque is explicitly locked cold even when selected, while retaining neutral focus/selection cues. No timers or motion were added.

Scene PNGs intentionally show the composited selected appearance. **Do not ship a scene/state preview as a production cold base.** Use individual masters/layer exports. Production text, hit targets, accessibility semantics and physical input mapping belong to the native owner. Fixed-aspect decorated components must not be stretched non-uniformly; previous iteration 12 nine-patches remain the scalable production handoff.

## Capability and owner boundaries

All labels, media illustrations, input values, temperatures and hardware availability are explicit sample fixtures. Logical canvases are 600×1000 (Android) and 800×800 (Thor), not measured display sizes or dp. No actual device capability, permission approval, profile apply/readback or input measurement occurred. Supported-case panels are paired with an all-cold unavailable-hardware view; full per-feature failure/pending/restore variants remain open.

Permission, picker and biometric scenes are visual concepts for their platform-owned surfaces. They are not replacement authentication or access-control implementations. A launcher theme alone cannot restyle those owners. The older Material Lab APK is unchanged. No LineageOS build, device write, installation or flashing took place.

## Verification and remaining work

See `REVIEW.md`, `coverage-map.json`, and `verification/evidence/technical.json` for the actual bounded checks and gaps. V1/V2 cover desktop art/source checks. V3 device rendering, text scaling, RTL, input semantics, native blending and performance are **NOT RUN**. This is a saved design checkpoint, not a finalized Android release.

Next artwork includes permission denial/revocation, picker empty states, authentication errors/lockout, richer keyboard variants, full Thor unavailable/error/apply/restore/recording sequences, wallpapers, boot/recovery/loading, charging variants and motion. Installed-app icons and historical canonical-source reconciliation also remain open.

## Rebuild and archive

From the repository root, with pinned dependencies in `requirements.txt` and Node available:

```powershell
python tools/build_forge_flows.py build-work/forge-flows-rebuild
python tools/verify_forge_flows.py build-work/forge-flows-rebuild --node node
```

On this workstation the render library is supplied through `CRAFTAGEDDON_RENDERLIB`. The scene builder refuses to overwrite a packaged checkpoint. `--resume-scenes` is only for reviewing an unpackaged draft.

`complete-assets.zip` includes all editable sources, layer exports, scene previews, gallery and evidence. The local ZIP is directly usable. GitHub uses `distribution/` byte parts plus a checksum-verifying `Restore-Archive.ps1`; reconstruct them before unzipping. The final verification tracker is alongside the ZIP and deliberately leaves V3 pending.
