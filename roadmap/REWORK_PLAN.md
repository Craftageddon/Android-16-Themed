# Craftageddon Ember and Dark Steel - Whole Rework Plan

Prepared 2026-10-19. Revision 1.1 adds explicit AYN Thor gaming, hardware, dual-display and LineageOS source work. Planning deliverable only.

The Thor is the primary hardware target. Shared phone artwork remains part of the visual library; Thor integration is a dedicated device product. See THOR_AND_LINEAGEOS_PLAN.md for the detailed implementation roadmap, ownership map and device acceptance requirements.

## Intended outcome

Rebuild the complete Craftageddon Android visual system around the earlier artwork's sculpted dark steel, structural copper, ember-filled seams and concentrated hot cores. The result should feel like one functioning forged instrument across launcher, SystemUI, controls, dialogs, keyboard, lockscreen, motion and sound. Carry that identity through Thor upper/lower layouts and the phone layouts already represented in the project.

This is a substantial appearance rework. Preserve the current asset inventory, useful silhouettes, component dimensions, working interaction patterns and accessibility semantics as input. The latest pale outline icon pass becomes a legibility reference; its appearance is provisional for this new direction.

The retained catalog represents 3,422 distinct valid files through 2,830 visual entries. Those figures include masks, densities, formats, historical versions and references; they are not counts of independent design tasks. The rework queue tracks component families and system surfaces instead.

## Art direction references

- References/Earlier_Ember_Steel_Connectivity.png: dark metal bodies, dimensional bevels, internally lit seams, recognizable symbols and bright focal cores.
- References/Earlier_Steel_Notification_Frame.png: layered steel construction, copper insets, flared corners, physical thickness and a quiet content well.
- References/Earlier_Steel_Button.png: a clear forged object silhouette and strong edge construction.
- References/Earlier_Animation_Design_System.png: the earlier boot, charging, control and motion language.

Use these as appearance anchors. Rebuild individual production masters with clean transparency, controllable light and consistent geometry. Historical atlas art and screenshots remain references; avoid turning a screenshot crop into an unverified production master.

## Visual specification

### Material and geometry

Dark gunmetal is the dominant material. Use blue-black cavities, graphite faces, restrained steel edge highlights, subtle surface wear and copper/brass at structural joints. Establish a consistent imagined light direction, bevel vocabulary, corner treatment, rim depth and texture scale. Detailed pieces may have pointed finials and layered plates where space permits. Keep central reading areas quiet and dark.

The warmth should come from ember channels and reflected light on nearby metal. Broad cream outlines should cease to be the dominant visual language. Plain component wells should still look substantial when emission is off. Use the existing clean silhouettes where they support recognition, then rebuild their material treatment.

Use three related levels of detail:

1. Hero art: boot marks, charging chambers, large app icons and lockscreen ornaments can carry rich texture and depth.
2. Everyday controls: clear metal rims, limited ornament, strong state separation and reusable scalable construction.
3. Compact status/navigation glyphs: broad, recognizable contours and a small amount of steel/ember detail that survives at actual display size. Simplify the large artwork deliberately for small slots.

### Palette - starting values to tune against the references

| Role | Initial direction |
|---|---|
| Deep cavities | Near-black, with a slight blue cast |
| Steel faces | Dark graphite and gunmetal |
| Steel highlights | Cool gray, narrowly placed |
| Structural trim | Dark copper and oxidized brass |
| Ember body | Deep red-orange through saturated orange |
| Hot core | Small amber/yellow-white centers |
| Primary text | Warm pale neutral, with clear contrast |
| Warning / success / error | Distinct semantic treatments with an icon or label |

Lock exact color values after viewing the pilot on both dark and bright display settings. Do not recolor every state orange and erase its meaning.

### Layer construction

A. Cold material/base: the actual unlit steel object, with clean transparency and no bloom.
B. Emission masks: separate neutral masks for seam light and, where useful, hot cores or a local light spill region.
C. Live symbol/value/text: crisp semantic geometry, accessible labels and live content.
D. Runtime lighting and state: tint, opacity, bloom, reflected warmth, selection and focus indicators.

Allow a hybrid workflow. Rich steel is often best represented by a carefully authored raster master; masks, trim paths, semantic shapes and scalable frames belong in editable vectors where appropriate. Inkscape is useful for geometry, mask alignment, corner guides, scalable frames and exports. It is not the renderer for native Android glow or platform state ownership.

### Idle glow and interaction

The new brief changes the earlier zero-emission idle recipe. Normal idle appearance should have a low, steady ember presence in selected seams or cores. A separate Cold/Unlit review mode remains available to inspect material quality and isolate masks.

Suggested starting ranges for the pilot, to be tuned visually rather than treated as fixed platform requirements:

| State | Intended appearance |
|---|---|
| Cold inspection | Emission fully off; steel remains readable |
| Idle | Low, steady seam/core warmth; approximately 0.08-0.16 mask opacity |
| Selected/active | Clearer steady or restrained breathing emission; approximately 0.28-0.45, with a persistent non-color selection cue |
| Focused | Clear focus boundary plus steady illumination; focus must coexist with selection |
| Pressed | Brief hot-core flare and a small physical response; settle back to the underlying state |
| Disabled | Reduced material contrast, no active emission or decorative movement |
| Warning | Distinct warning cue; one event pulse followed by a steady indication |
| Reduced motion | Static lighting, no breathing, sweeps, travel or compression |

Keep status indicators steady. Restrict particles, long sweeps and cinematic effects to scenes such as boot or charging where they add meaning. Pause hidden/obscured animation. Keep text and small glyphs clear of bloom. Revise the shared state contract once and propagate it to every preview and native consumer.

### Typography and layout

Use Cinzel for short identity labels and occasional headings. Use Noto Sans for settings, notifications, values, input and longer reading. Text, time, percentages and labels remain live. Adapt ornament to the screen and content; long labels and enlarged text must fit without forcing the forged frame to cover information.

## Ordered production plan

### Phase 0 - Lock scope and sort the collection

Create a family-level source-of-truth register from the full catalog. Mark each family Reuse, Rebuild material, Redraw geometry, Historical reference or Unresolved. Record its target surfaces and component owner. Separate current masters from old versions, captures and density exports. Keep every earlier release intact.

Deliverable: rework coverage register, selected reference board and stable asset IDs. Completion: every required family has a named action and every retained source has a role; counts are not inflated by export variants.

### Phase 1 - Establish the material system with a pilot family

Make one coherent sheet with 18 representative specimens: primary button, icon button/socket, toggle, slider, notification card, dialog/panel, quick-settings tile, settings symbol, Wi-Fi status, battery status, back/home navigation and a lock/charging ring. Add six Thor specimens: controller button prompts, stick/trigger calibration controls, gaming quick-menu/focus capture, dual-screen routing, a per-game profile card, and a fan/performance/RGB control cluster.

Show cold, idle, selected, focused, pressed, disabled and reduced-motion behavior. Compare the pilot directly with the earlier references and place the components together in a dense quick-settings/notification context. Show the detailed and compact treatments side by side. Explore idle/active brightness within this chosen direction rather than changing the whole theme between samples.

Completion: steel reads as metal when unlit; idle reads as ember and dark steel; glow stays localized; a sheet of unrelated specimens still looks like one set; compact glyphs remain identifiable. Use this sheet as the visual contract for bulk production.

### Phase 2 - Rebuild the reusable component system

Apply the pilot to buttons, sockets, toggles, checks/radios, sliders, progress, tabs, text fields, lists, menus, scrollbars, cards, notifications, dialogs, tooltips and toasts. Establish stretch regions and fixed decorative corners. Produce optical variants and shared spacing rules. Keep live content independent of frames.

Completion: state, density and resize comparisons pass; no stretched metal texture, repeated seams, clipped finials or baked text. All surfaces use the same material and state specification.

### Phase 3 - Rebuild identity and system symbol coverage

Cover settings categories, launcher/navigation, power actions, battery/charging, connectivity, privacy, audio, input, transfers, displays, fan/performance and thermal states. Produce consistent holders and app-icon treatment, then use an explicit installed-app list for app-specific coverage. Keep signal levels, warning marks and accessibility semantics intact.

Completion: a family sheet covers every defined state; small-size renders and actual control contexts remain legible; no unreviewed stock fallback is silently counted as themed.

### Phase 4 - Recompose complete everyday screens

Build launcher, drawer, folders/widgets, shade/quick settings, notifications, settings, power menu, secure-unlock visual treatments, recents, sharing, permissions, file/photo pickers, clipboard, screenshot tools, keyboard, volume/output and Thor device controls. Compose upper, lower and phone arrangements from shared components; adapt density and ornament to the actual layout.

Completion: complete journeys have consistent materials, lighting and typography. Check normal/enlarged text, long labels, empty/error states, touch/controller focus, safe areas and display changes. A good component sheet alone does not complete this phase.

### Phase 5 - Reconcile atmosphere, motion and audio

Rebuild boot, charging and transitions with the accepted material/light model. Reconcile the earlier 114 motion demonstrations with the newer state contract rather than carrying two competing systems forward. Coordinate wallpapers, wordmark treatments, sound families and optional haptic timing. Keep cinematic art from competing with everyday reading.

Completion: motion has a defined trigger, duration, stop condition, reduced-motion equivalent and visibility/lifecycle rule; sounds have a consistent identity and sensible level. Device resource cost still requires measurement.

### Phase 6 - Integrate with the real Android owners

Inspect the exact Thor Android build and phone environment before assigning resource names or choosing an installation mechanism. Map framework/SystemUI, launcher, Settings, IME, permission/picker, lockscreen and OEM surfaces to their actual owners. Integrate in reversible batches and retain rollback checkpoints.

Completion: each integrated batch renders and behaves in the target component on hardware. Secure unlock, permissions, controls, battery/radio values and other system behavior continue to be owned by the real platform logic. Visual mockups are not installation evidence.

### Phase 7 - Validate and release a unified checkpoint

Check visual parity with the pilot, export/reimport integrity, mask alignment, alpha edges, nine-patch behavior, actual-size legibility, dark/bright display conditions, contrast, text scaling, RTL/long strings, controller/touch focus, reduced motion and hidden-screen suspension. Measure frame timing, memory and battery impact on the actual targets.

Publish a new versioned pack with editable sources, exports, contact sheets, coverage register, test evidence, source attribution, hashes, installation notes and rollback instructions. Distinguish Designed, Previewed, Integrated and Device verified for every family. Archive superseded appearance variants without deleting them.

## Work order and checkpoints

The attached Rework_Coverage_Queue.csv is an initial family/surface queue. Every row starts Planned. It is a planning register rather than a claim that these families have been redrawn.

Sequence: reference/material contract -> pilot -> core controls -> symbols -> complete screens -> atmosphere -> native integration -> device acceptance. Do not finish thousands of exports before the pilot establishes the material language. Reuse accepted geometry, masks and native behavior where they fit the new direction; spend drawing effort on the material and shape differences that matter.

Track progress through: Inventoried, Reference selected, Designed, Cold master ready, Masks ready, State previewed, Export checked, Screen checked, Native integrated, Device verified. Keep design completion separate from integration completion.

## Proposed working package

Craftageddon_Ember_Steel_Rework_v2/
  00_Art_Direction/
  01_Material_and_State_Tokens/
  02_Editable_Masters/
  03_Cold_Bases/
  04_Emission_Masks/
  05_Android_and_Density_Exports/
  06_Component_and_Screen_Previews/
  07_Motion_and_Audio/
  08_Integration/
  09_Validation_and_Coverage/
  Releases/

Keep source geometry, mask bounds, naming and versions linked through a manifest. Use sibling releases for major iterations. This folder structure is proposed; it was not created as an implementation in this planning pass.

## First concrete milestone

Produce the 18-specimen pilot sheet using the earlier steel notification frame, button and connectivity artwork as the fidelity anchors. Show the specimens together on a quiet dark-steel panel, with a second cold/unlit comparison and compact-size strip. That is the reference to establish before expanding the whole collection.

## Added primary workstream - Thor and LineageOS

The visual rework explicitly includes controller prompts and controller-first navigation, gamepad testing and calibration, trigger/layout modes, mappings and shortcut ownership, per-game settings, lower-screen gaming tools, dual-display app routing, lid/sleep behavior, fan/performance/charging controls, stick lighting, capture, and hardware diagnostics. Each backend capability is verified against the exact installed build before being exposed.

The source work is a Craftageddon OS product derived from the validated LineageOS baseline: pinned manifests, device/common/hardware integration, shared visual resources, SystemUI/Settings/launcher source patches where needed, a Thor control center and narrowly privileged hardware adapters. Resource overlays cover existing replaceable resources; behavioral changes require actual application/framework/service code. Device/kernel/vendor changes are isolated and justified by hardware tests.

Implementation order is now: reproduce and audit the Thor baseline in parallel with the 18-specimen material pilot; build one working controller-first lower-screen control-center slice; then extend controls, profiles and device services through the whole UI. Validate real games/emulators, both displays, controller focus, sleep/resume, thermal behavior and updates before a device-verified release. The additional queue entries are in Rework_Coverage_Queue.csv; the full details are in THOR_AND_LINEAGEOS_PLAN.md.
