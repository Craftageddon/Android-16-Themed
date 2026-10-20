# Native Android / Thor handoff — design checkpoint

This is an implementer handoff and a small independently compilable resource sample. It is not a SystemUI patch, installable APK, overlay package or device image.

## Rendering contract

1. Draw the cold base using its unmodified alpha. Never scale a decorated frame non-uniformly. Pilot frames have fixed aspect ratios; adapt with a procedural native frame or an explicitly authored stretch-safe nine-patch later.
2. Tint the neutral seam mask with the ember token and the core mask with the hot-core token. Apply the state opacity and the current 2.8 preview gain. Clamp after multiplication. Native color-space and bloom output must be compared on hardware before locking that gain.
3. Draw semantic symbols and live platform text sharply above the material/light. Cache resized static rasters; do not decode the 2098px/1254px hero source on every frame. Author lower-density cached variants for the measured device density.
4. Draw selection and focus as separate geometry. Disabled suppresses illumination. Cold inspection suppresses illumination without changing the base. A press settles after 160ms; use the shared easing for interpolation. Reduced motion has no blur, breathing, movement or compression. Hidden surfaces schedule no animation.

`tools/state_driver.cjs` is the tested reference for state resolution. It does not consume controller events or modify hardware. SVG filters and gradients are not assumed to work in Android VectorDrawable; the SVG sources are art masters. Use PNG layers or explicitly port the geometry to a native renderer.

## Ownership and privileges

| Surface / behavior | Intended owner | Implementation status |
|---|---|---|
| Launcher and game library | Launcher application | Composed only |
| Shade, QS, notification, volume, keyguard | Actual SystemUI/framework owner in pinned ROM | Composed / mapped only |
| Thor calibration and device settings | Verified AynParts / Settings / device service | UI design only |
| Lower-screen control center | Native control-center application with explicit input capture | UI design only |
| Performance, fan, charging, RGB | Restricted validated hardware service | No backend assumed |
| Display routing, lid, touch and focus | Device/framework configuration after exact baseline audit | No guessed IDs or trees |

Resource overlays can replace resources exposed by their target; they cannot add executable service behavior. Retain the validated vendor/kernel/MCU stack unless a demonstrated defect requires a change. Do not modify Generic.kl to fix built-in controls. Preserve secure unlock and the platform's thermal/charging authority.

## Controller interaction

Focus traversal follows reading order within the active display. Do not capture the game's inputs merely because the lower panel appears. Capture only after an explicit user action; show capture state. On panel close, B/back, app focus loss, disconnect or lid suspend, release every held button/axis and restore game input ownership. Controller label convention and underlying Android event mapping are independent. The A/B/X/Y specimen is not a hardware mapping claim.

Use `controls/control-map-template.json` for device discovery. Record actual Android key codes, axis IDs, flat/fuzz ranges, dead zones and source display after measurement. External controllers need their own map. Per-ROM profiles require an explicit emulator game identifier/hook; a package name identifies an app, not an individual ROM.

## Display and lifecycle acceptance

AYN's [official Thor page](https://www.ayntec.com/products/ayn-thor), checked 2026-10-20, describes a 6-inch upper AMOLED touch display and 3.92-inch lower AMOLED touch display. The design canvases are **logical units**, not measured device pixels or dp. Before integration, record both displays' actual modes, densities, safe areas, orientation, touch transforms and current firmware. The page lists stock Android 13; that does not describe or validate the user's historical Android 16 / LineageOS build.

Test independently: top-only/bottom-only/dual display, game plus panel, controller focus versus touch, rotation/keyboard, app pairs, lid close/open, sleep/wake, unplug/reconnect, active profile restore, and thermal throttling. Hide unsupported backend controls or show an unavailable state rather than reporting fictitious telemetry.

## Resource sample

`res/values/` carries palette/geometry values and `res/drawable/` carries a focus boundary and selection marker. The sample uses a dedicated `cg_es_` resource prefix and no invented platform resource names. AAPT2 compilation establishes resource syntax only; owner linking, installation, runtime behavior, accessibility, performance, signing and rollback remain unverified.

See [device-test-matrix.csv](device-test-matrix.csv) and the original [LineageOS roadmap](../roadmap/THOR_AND_LINEAGEOS_PLAN.md) for remaining acceptance work. This checkpoint includes no flashable artifacts or signing material.
