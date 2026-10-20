# AYN Thor Gaming and LineageOS Rework - Revision 1.1

2026-10-19. This extends the ember/dark-steel art direction into a complete controller-first Thor OS plan. All features below are planned; a current hardware/firmware audit determines the supported backend for each one.

## Starting point and evidence

The earlier project records contain a built LineageOS 23.2 / Android 16 Craftageddon product for odin2thor and the user's August 27 report that the installed baseline booted. The current local scaffold contains vendor/craftageddon, a lineage_craftageddon_odin2thor product, and a Thor manifest targeting lineage-23.2. These are historical build and boot records, not a new inspection of the currently installed device.

Current upstream inspection confirms a Thor device tree, Thor display/lid/touch configuration, and an AYN hardware repository with AynParts, hardware services and policy. The inspected lineage-23.2 AynParts settings declare layout/trigger configuration, two mappable controls, calibration and RGB settings. Their existence in source does not establish that every function works in the user's installed build. The public repositories currently show lineage-24.0 as their default branch; do not silently migrate this Android 16 project to that branch. First reproduce the pinned working baseline, inspect the current device, and evaluate compatible changes deliberately.

Read display IDs, dimensions, densities, supported modes and input descriptors from the actual Thor during the baseline audit. Old documentation contains display/refresh assumptions; do not copy those into new code without verification. Do not substitute another AYN device tree based only on a similar chipset.

## Track A - Gaming controls and artwork

### Controller identity and prompts

Create a complete ember/steel prompt family for the Thor's verified physical controls: face buttons, D-pad and diagonals, shoulders, triggers, stick clicks, Start/Select and system/AYN/mappable controls actually reported by the device. Include tap, hold, chord, disabled and capture states. Provide a selectable prompt convention where useful, keeping displayed button names and the underlying Android key mapping as separate settings.

Build consistent focus rings, selected markers, directional hints and confirm/back behavior throughout the launcher, Settings and the Thor control center. All important controls must be usable with a gamepad as well as touch. A local test screen should visualize live buttons, axes, hats, trigger values and controller identity.

### Calibration, modes and mapping

Design and implement stick-center/range checks, calibration guidance, reset-to-baseline, and supported deadzone/sensitivity settings. Integrate the device's available analog/digital trigger modes, trigger thresholds and controller layout settings through their verified owner. Support the actual mappable controls and virtual mouse mode where the installed firmware exposes them.

Use device-specific input mappings when a low-level correction is needed. Never alter Generic.kl to fix this one handheld. System shortcuts must not swallow ordinary game input. Make controller capture explicit while a system panel is active, release captured input on dismissal and test held-button/axis cleanup across app switches and sleep.

Touch-to-gamepad or gamepad-to-touch mapping is a separately scoped feature with its own owner, permissions, compatibility tests and input lifecycle. Audit existing support first; do not assume the stock mapper can be redistributed or dropped into LineageOS. If it is unavailable, specify a maintained implementation before promising parity. Gyro, rumble and additional controls are exposed only if the actual hardware/driver stack supports them.

### Per-game and emulator profiles

Plan profiles for controller convention/mappings, supported trigger mode, allowed performance/fan settings, screen preferences, lighting, brightness and overlay behavior. Preserve a global default and provide a clear restore action. Profile application must read back the effective state and report partial failures.

A package identifies an app; it does not uniquely identify each game inside an emulator. Start with per-app profiles. Individual ROM/game profiles require an explicit emulator integration or a manual game selector, with a stable game ID. Do not infer a game identity from an arbitrary app title.

When apps are active on both screens, controller focus determines the input profile. Define shared hardware-resource arbitration separately; a foreground profile must not undo a safety limit or produce oscillating fan/performance settings. Apply manual temporary overrides consistently and restore the intended default on exit.

## Track B - Thor dual-screen experience

Build a lower-screen control center in the same sculpted steel and ember language. It should have readable live values, predictable controller traversal and clear indication of which screen/app currently owns input. Provide touch-only mode for a panel when the player wants the game to retain controller input, and explicit controller-capture mode when navigating the panel.

Cover app launching to each display, screen swap/move, app-pair launching where supported, independent brightness and supported refresh modes, lower-screen dim/off actions, per-screen rotation/keyboard targeting, focus handoff and notification ownership. A lower-screen keyboard, touchpad or game deck is an optional mode with an explicit input owner, not an assumed capability of every app.

Plan top/bottom/both screenshot capture and supported recording options. Observe actual display IDs instead of hardcoding a screen as display 0 or 1. Include external-display/USB hotplug behavior only after verifying the device's actual capabilities.

Test two-display emulators and two separate apps, permission prompts, keyboard opening, overlays, orientation changes, controller focus and lid close/open. Respect application lifecycle and resizing limitations; do not promise that every game keeps running unchanged while a panel or second app takes focus. Verify the desired behavior with actual games.

Lid and sleep policy must restore display power, brightness, audio, input ownership, profiles and lighting coherently. Include locked/unlocked states, charging, reopened games and reboot persistence. Keep static overlay brightness, dimming and timeout behavior configurable for comfortable long sessions.

## Track C - AYN hardware features

A verified capability register must name the owner, read path/API, write path/API, allowed values, persistence, permission and tested fallback for every hardware control. Reuse existing HALs/services and AynParts integrations where suitable. The renderer never writes hardware nodes directly.

Include fan/automatic cooling modes, available performance profiles and thermal telemetry; controller and lighting controls; charging/bypass/charge-limit options only where supported; audio output, rumble and battery status; device/display/controller diagnostics. Unsupported controls should be omitted or explicitly unavailable, never represented by a working-looking fake toggle.

Keep hardware thermal and charging limits authoritative. Theme lighting on screen and physical stick RGB are separate systems with separate brightness/enable settings. A synchronized ember preset is an option; physical lighting must respect the user's off setting and suspend policy. No invented sysfs paths or guessed register values enter the implementation.

## Track D - Modify and build LineageOS

### 1. Reproduce the hardware baseline

Recover the pinned source manifest and local patch state for the earlier successful product, record firmware/blob/kernel dependencies, and compare them with the installed build. Reproduce a clean build on the Linux build filesystem, recording commit IDs, toolchain, target product and artifact hashes. Keep the working image set and matching recovery/restore procedure as an immutable checkpoint.

Run a fresh hardware matrix: both display/touch devices, every gamepad control/axis, lid, suspend/resume, fan/thermal, charging, RGB, audio, storage, networking and available peripherals. Separate inherited upstream gaps from rework regressions. A full successful boot alone does not close this matrix.

### 2. Own a maintainable Craftageddon product

Continue the existing vendor/craftageddon and lineage_craftageddon_odin2thor product structure after verifying its current build compatibility. Keep a pinned upstream baseline and separate patch groups for visual resources, app/SystemUI behavior, Thor features and device support. Store artwork/state tokens with reproducible export steps and document which consumers must be rebuilt when tokens change.

Use supported static/build-time or runtime overlays for existing target resources and configuration. RROs cannot add DEX behavior; custom glowing controls, new controller flows and hardware actions require actual code. Patch the owning component instead of treating every feature as a drawable replacement. Respect overlayability and signing rules.

### 3. Map component ownership

| Work | Intended owner / implementation approach |
|---|---|
| Shared colors, typography, frames and configuration | Craftageddon product resources/overlays, plus component-owned drawing code as needed |
| Shade, quick settings, notifications, volume, navigation, keyguard | SystemUI and its framework dependencies |
| Settings and Thor device pages | Settings integration and maintained AynParts/Craftageddon Thor modules |
| Game library, launch destinations and app pairs | Launcher/Trebuchet extension or a maintained Craftageddon launcher component |
| Gaming quick panel and controller-first navigation | A native Thor control center with explicit focus/input ownership; integrate through supported system entry points |
| Profile selection and persistence | Profile component/service with validated settings, readback, restoration and migration |
| Device-specific buttons/axes and genuine mapping defects | Correct device-specific keylayout/configuration and the relevant input/device code |
| Fan, charging, RGB and hardware control | Existing hardware HAL/service adapters, or a narrowly privileged maintained service when needed |
| Display/lid/touch routing | Thor device configuration plus verified framework/window/display changes where necessary |
| IME, permission and file/photo flows | The real owning system apps; platform behavior remains authoritative |
| Boot, offline charging and recovery presentation | The appropriate boot/charger/recovery process, with a readable functional recovery UI |
| Kernel, vendor blobs and MCU interfaces | Preserve the validated device stack; change only for a demonstrated device-support need |

These are planning ownership boundaries. Final class names and resource maps come from the chosen pinned source revision. A shared drawing library is useful only where each owning process can safely consume it; do not assume one new app can recolor or replace every system process.

### 4. Implement privilege boundaries and hardware adapters

Keep UI, profiles and hardware adapters separate. Built-in OS components should use appropriately restricted system interfaces rather than requiring a root shell or Shizuku for normal operation. Validate callers, values and restore behavior. Add only the needed privileged permissions/SELinux rules; preserve SELinux enforcement and existing authentication, secure unlock and platform permission behavior.

Retain key mappings and gameplay behavior while reworking presentation. Functional additions, such as per-game automation and input capture, get their own tests and feature switches. Avoid a generic global input interception layer when a specific supported hook will do.

### 5. Deliver vertical slices

LOS-A: reproducible baseline and current hardware report.
LOS-B: themed launcher/Settings slice with controller navigation and shared material/light rules.
LOS-C: working lower-screen Thor control center with independent display controls and clean input handoff.
LOS-D: supported controller/calibration/trigger/RGB controls with effective-state readback.
LOS-E: profiles, gaming workflows and remaining framework/SystemUI visual coverage.
LOS-F: full device regression, update/rollback test and a release candidate with evidence.

The visual pilot can proceed while LOS-A is being established. Prove one live hardware action and one controller-focus handoff before scaling up a large set of device-control screens. Preserve a working checkpoint at each slice.

### 6. Build, update and release

Compile changed modules as well as the full Thor product; inspect resource overlays and permissions; run relevant platform/input tests and hardware regressions. Produce the exact image and update artifacts required by the chosen device build, then verify their metadata and hashes. Do not copy an old universal partition list into the new release procedure.

Plan signing identity, update compatibility, data/profile migrations, versioning and recovery/rollback as part of the product. Local reproducible update packages come before any hosted updater service. A base-version migration is a separate decision with a separate compatibility matrix; the art rework does not implicitly authorize moving from Android 16 to another major platform.

## Thor-specific acceptance matrix

- Input: all real buttons, sticks, hats, analog/digital triggers, calibration persistence, hotkeys, held-input release, controller reconnect and resume.
- Games: native Android games, controller-capable apps, a supported dual-display emulator and a single-app game on either display. Record exact app versions and relevant settings.
- Profiles: apply/readback, manual override, game exit/crash, two-screen arbitration, reboot and schema migration; no stuck hardware state after a failure.
- Displays: both touch devices, independent brightness/modes, screen routing, input focus, keyboard/permission dialogs, rotation, lower-screen off and lid transitions.
- Hardware: supported fan/performance/charging/RGB actions, permission boundaries, thermal override, unsupported-feature fallback and sane restoration.
- Runtime: live values, actual-size readability, reduced motion, no distracting status blinking, hidden-screen suspension, frame timing, thermals and battery cost measured on the Thor.
- Release: full build and module checks, enforced SELinux, matching recovery, persistent user data/settings where supported, tested update/rollback and clearly labeled remaining gaps.

## Revised first design milestone

Expand the material pilot to 18 specimens. Add controller prompt artwork, stick/trigger setup, the gaming quick-menu/focus treatment, dual-screen routing, a game profile card and the fan/performance/RGB control cluster. Pair that sheet with a two-screen layout showing the game on one display and the Thor control center on the other. The same cold steel, ember seams and restrained hot cores should carry through the real system controls.

## Sources checked 2026-10-19

- Local historical scaffold and the earlier Build Craftageddon OS for AYN Thor Max chat/build records.
- [LineageOS Thor device tree](https://github.com/LineageOS/android_device_ayn_odin2thor)
- [Thor lineage-23.2 device configuration](https://github.com/LineageOS/android_device_ayn_odin2thor/blob/lineage-23.2/device.mk)
- [AYN hardware support](https://github.com/LineageOS/android_hardware_ayn)
- [AynParts controller settings, lineage-23.2](https://github.com/LineageOS/android_hardware_ayn/blob/lineage-23.2/packages/AynParts/res/xml/ayn_panel.xml)
- [AynParts RGB settings, lineage-23.2](https://github.com/LineageOS/android_hardware_ayn/blob/lineage-23.2/packages/AynParts/res/xml/rgb_lighting_panel.xml)
- [AOSP runtime resource overlays](https://source.android.com/docs/core/runtime/rros)
- [AOSP device-specific key layouts](https://source.android.com/docs/core/interaction/input/key-layout-files)

The upstream wiki page could not be read in this run (HTTP 403); no current official-build availability or install instruction was inferred from that failure. Source repositories were used to ground this plan; the current physical Thor and mounted Linux source tree were not modified or freshly hardware-tested here.
