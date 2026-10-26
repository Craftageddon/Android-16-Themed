# Forge23 magnification artwork and native source handoff

W06 now has actual-owner artwork/source adaptations for fullscreen and window magnification, dashed size editing, resize/drag/Done controls, preset/switch/zoom settings and the retained directional controller. Off controls are cold steel; actual checked/selected/pressed or settings-panel state drives separate neutral masks and runtime color. Native English labels remain live.

## Inventory and evidence

- 23 authored treatments: 16 source-geometry material treatments and 7 new control drawings. The 27 master-directory SVGs also include one exact panel alias and three procedural-border parameter examples; those are not 27 unrelated new drawings.
- 644 new native PNG configurations, 28 exact panel resource aliases and one cold material tile. Production color/glow stays separate; previews may show composed ember.
- Three actual new Java rendering/support classes, five modified actual SystemUI owners and three modified native layouts. Skin resources compile/link against API37. The private-platform owners and full layouts are not claimed as a full SystemUI build or executed Android UI.
- Nine editable SVG/PNG workflow fixtures show actual source English strings and state/visibility roles. They use desktop font/measurement approximations and are not Android screenshots. The fullscreen radius shown is illustrative; the unchanged owner supplies actual display radius at runtime.

The native border renderer preserves half-stroke inset/radius clamping from pinned GradientDrawable, normal 28/30dp and edit 16/18dp resource radii, 20/20dp edit dashes, fullscreen 12dp total stroke and 6dp visible stroke/offset defaults, and actual context resources/density. Its light rail stays within the original shell. No mirrored image content is tinted or replaced. Fullscreen remains a GradientDrawable subtype for the original corner updater; custom/Wear backgrounds keep their existing exception.

Resize handles declare 48dp targets around 26dp visible housings. The optional directional controller has four separate 48dp targets in a window sized to three measured target widths, with native short/long movement and 100ms repeat unchanged. Hidden control rectangles are excluded from the window's touch region, preventing invisible enlarged handles from intercepting underlying content. The 48dp Done editing target adds an accessibility click for the existing touch action. Native nonfocusable overlay/window flags and input routing stay intact; no game input capture or device/controller execution is claimed.

The settings header stacks using actual native text measurement when space is tight. Done grows with native text height and stays outside the original scroll body. Switch-track padding is zero to retain the full 20dp declared thumb travel. Six shared global glyph resources remain untouched; magnification binds its own treatments instead. The misleading ic_open_in_new_window source contains a settings gear and is treated accordingly. Native scale data still reads ro.config.max_magnification_scale; fixtures use its 8.0 default without asserting the product property.

## Apply and reproduce

Use SystemUI-magnification-forge.patch against the pinned frameworks/base/packages/SystemUI source. Copy the hash-listed PNG entries from native-patch to the same module resource paths; binaries are intentionally outside the text patch. Existing source/license files are preserved under upstream; derivative glyph geometry keeps its original Apache-2.0 provenance and notices. Project material/control additions use the repository terms; CC0 does not relicense upstream geometry/code.

Run fetch_magnification_owners.py, build_magnification_art.py, prepare_magnification_patch.py, compile_magnification_resources.py, render_magnification_fixtures.py, verify_magnification_checkpoint.py, then prepare_magnification_checkpoint.py from the repository tools. Builders refuse to rewrite a packaged checkpoint. Set CRAFTAGEDDON_RENDERLIB to the already installed rendering-library directory; use the recorded existing Python/Pillow/resvg, JDK and SDK37. The Windows SDK compiler requires host execution outside this sandbox. No installation, upstream code execution on hardware, flashing or settings change occurs. Verification JARs/resource banks are not runtime packages and their generated IDs are compile-only.

V1/V2 pass only for the stated source/art/compile scope: source and clean-patch byte parity, masks/alpha, source geometry, state selectors, native rendering-class compilation, host geometry and target calculations, real resource compile/link, source labels and inspected fixtures. Full pinned Soong, native layout inflation, actual Android/device/input/accessibility/performance acceptance and V3 remain NOT RUN.

The complete 10,926-family/16,559-variant goal remains active. This checkpoint records 25 new owner decisions and retains two already-preserved inset contracts with their actual owner bindings. 9,630 family decisions, W03 setup, W04 updater, W05 gallery, W07 boot/charger/recovery, other required art/owner work and the final independent whole-goal double-check remain open.
