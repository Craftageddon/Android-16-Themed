# Style consistency check and scrollbar correction — 0.2.1

The repeat check found one additional material omission in the older catalog: the scrollbar thumb used a smooth edge gradient without the forged texture. This checkpoint restores the original material on that surface. Its path geometry, canvas, bounds, six neutral masks and earlier source file are unchanged.

The final source-level audit passes for833 authored source/alias records representing652 distinct effective SVG contents. These counts include functional variants, copies and examples; they are not833 unrelated drawings. No further confirmed material mismatch was found within the checks below. This is not a claim of final Android or device acceptance.

## Exact scope and evidence

| Requirement | Current evidence | Result |
|---|---|---|
| Cover the authored catalog, not only the latest99 fixes | `audit/active-source-index.json`:472 canonical records; later masters;16 app identities;16 semantic-review correction glyphs;112 approved reuse copies; explicit recovery30 and correction31 precedence | Checked |
| Keep steel dark and textured | All20 canonical master sheets and all9 recovery group sheets inspected against the original reference;751 used cold gradients checked for known and additional pale neutral surfaces; missing-texture surface check | One scrollbar omission corrected; final checks pass |
| Preserve the ember palette | Nine existing style files inspected; exact main colors are reflection `#dc5920`, spill `#ff4908`, seam `#ff5b0b`, core `#ffd083`, focus `#d5e7f2`, symbol `#ffe5bc` | Pass |
| Keep lighting separate and cold defaults unlit | Mask groups hidden by default; direct paints and1,306 resolved gradient/filter/clip references checked for neutral paint | Pass |
| Preserve neutral status/value indicators | Compact-symbol roles are documented in prior source contracts; small Wi-Fi/battery symbols explicitly omit texture at status size; progress/focus/readout colors are semantic indicators, not broad metal faces | Preserved; not miscounted as silver-metal failures |
| Preserve meaningful off/focus/disabled and reduced-motion behavior |18 existing pure motion/semantic tests run against all114 original recipes; tests cover off/focus-only nonemission, selected-channel ownership, English wording and static reduced motion | Pass; host sampler only |
| English presentation | No visible text nodes in production masters;189 earlier editable compositions checked for non-English alphabets;114 motion recipes/labels checked by the existing tests; recovery30's unchanged evidence records753 English nodes across71 refreshed specimens | Pass within those source checks |
| Preserve prior work |472 original/portable canonical masters and10 linked reference images verified;189 earlier composition source/portable pairs verified; all4,695 listed recovery30 artifacts freshly rehashed | Pass |
| Validate the additional correction |14 PNG layers at the original32/64px widths; all six masks pixel-identical to fresh before renders; cold changes confined to the thumb; same path data, image size and occupied bounds | Pass |
| Real native/Thor appearance | No device connected; no native resource adoption, inflation, tint, actual-screen contrast, input or performance exercise | NOT RUN; remains a separate gate |

Full audit records and the actual motion test output are in `audit/`. The mask checks resolve referenced definitions; they do not merely search for orange strings. The steel scan checks gradients actually referenced from cold material. Functional compact masks and archived superseded masters are identified explicitly.

## Visual review

Reviewed the20 canonical current-master sheets, the9 recovery30 group sheets, the2 semantic-gap sheets, both app-identity sheets and the semantic-correction sheet. Scene checks included Gallery selection, updater checking and the magnification owner-state sheet. The prior189 composition records were hash/English checked; this does not imply every layout received a new visual or native measurement pass.

The original sculpted heroes remain the detailed reference. Tiny native symbols, neutral tint masks and live value indicators intentionally have different optical roles. Their placement and contrast on the Thor remain unverified. This check does not approve every future generator, every uncreated OS asset, or any release for installation.

## Files

- `masters/control-scrollbar.svg`: corrected editable specimen; keep the adjacent `source/` folder for its original texture.
- `layers/`: seven individual editable layers.
- `exports/`:14 transparent PNG layers at the original1x/2x widths. These are fixed-aspect specimens, not newly declared native nine-patches.
- `previews/scrollbar-before-cold-on.png`: actual rendered before/cold/on comparison, including actual-size specimens.
- `correction.json`: source/corrected hashes and exact changed scope.
- `audit/summary.json`: final machine-check result.
- `audit/active-source-index.json`: effective source selection, including recovery30 and correction31 overrides.
- `audit/indicator-role-exceptions.json`: pale semantic/value marks requiring role-aware treatment.
- `source/control-scrollbar.before.svg`: unchanged original source bytes.

The archived canonical contact sheet14 still shows its historical before version; this checkpoint's comparison is authoritative for the corrected scrollbar. None of the189 earlier compositions embeds the old scrollbar path, so no existing screen-composition geometry was silently left pointing to that path.

Legacy generators and checkpoints are retained for historical reproduction. Future artwork should use the recovery material policy and run this audit; unchanged legacy generator defaults are not approval to reintroduce the brightening helper. No earlier checkpoint, native owner, semantic ledger, latest pointer, main branch or device was modified.

## Reproduce

Use the existing Pillow/resvg environment with `CRAFTAGEDDON_RENDERLIB` pointing at the installed render library, then run:

1. `tools/build_consistency_scrollbar_correction.py`
2. `tools/audit_style_consistency.py`
3. Set `FORGE_MOTION_CATALOG=iterations/16-forge-motion/source/retained-catalog.json` and run Node's test runner with `tools/forge_motion_v3.test.cjs` and `tools/forge_motion_semantics.test.cjs`.

Builders refuse to rewrite a packaged checkpoint. The original source base is recovery30 commit `2e8404ead85637d4cd950afc9addddd918278ecb`. User visual acceptance, actual native/Thor acceptance and independent final release validation are still separate from this completed source-artwork check. No new AI image generation was used.
