# Reference Forge 15 — additional journey states

22 October 2026. Work-in-progress artwork for **LineageOS 24.0 / AYN odin2thor**. This pass adds 120 editable state scenes: 63 Android and 57 Thor, across 24 declared journey families. It reuses 18 unchanged layered component masters from iteration 13; these are not 18 newly designed assets.

Android additions cover permissions and revocation; photo/document empty, selected, unavailable and cancelled states; PIN errors and lockout; pattern and biometric fallbacks; sharing, clipboard and storage failures; audio routing and disconnect; power confirmations; multiwindow availability; shift, caps, secondary symbols, English email/website keyboard examples and suggestion outcomes. Thor additions cover mapping conflicts/apply/errors/restore, profile partial/failed apply and restore, capture consent/denial/record/pause/storage failure, controller capture release/resume, unsupported touch mapping, display routing and separate cooling/charging/lighting availability and readback outcomes.

## Usable output

Open `index.html` locally for the offline journey viewer. Choose a journey/state or follow one of its 263 sample transitions. The controls change artwork only: they do not authenticate, grant permissions, share files, record, power off or invoke hardware. Outcome branches labelled Preview stay in the viewer rather than appearing as product buttons. These are explicit fixtures, not service implementations or test results from an attached Thor.

`screens/` contains editable SVG compositions and their PNG previews. `inspections/` contains corresponding compositions with emission hidden, keeping content and focus unchanged. `masters/` retains 18 unlabelled layered SVG sources with cold steel and separate neutral reflection/spill/seam/core/focus/symbol layers. `source/` holds unchanged texture inputs and hash provenance. Individual production component layer exports remain in iteration 13's complete archive; this archive supplies reused sources, scene exports and the new journey graph.

`english-text-catalog.json` lists approved English labels, with corresponding Android resources under `native-text/res/values/strings.xml`. `flow-definitions.json` lists all states and targets; `journey-index.json` groups them. `screens/layout-metadata.json` records live text bounds, artwork states and which actions are viewer-only. `previews/` holds fourteen review sheets (seven Android, seven Thor). Full ZIP, detached RSA-PSS signature and pinned public key are retained locally; checksum-verified transport parts restore the same ZIP from GitHub. This source signature does not confer APK, OTA, AVB or manufacturer trust.

## State and scope

Off/unselected/focused-off/disabled artwork remains cold. Active or confirmed selections use separate light layers. Partial apply lights only the confirmed display/input settings; the unavailable fan row stays cold. Unavailable capability views stay cold. All authored labels are English (en-US), including native string resources. Keyboard examples use English QWERTY, shift/caps, symbols, email and website layouts. Text remains live rather than painted into the steel. These examples do not establish native IME behavior or device-font parity.

`REVIEW.md` records layout/material corrections. `verification/evidence/technical.json` records bounded graph, source, pixel, geometry and script checks. V3, browser rendering, target behavior, hardware services and native integration remain NOT RUN. Logical 600×1000 / 800×800 layouts are design grids, not measured device dp/insets. No device was attached at the read-only inventory check.

Remaining visual scope is explicit in `coverage-map.json`: actual motion and all 114 legacy recipes, historical canonical-source dispositions, exact application-icon targets and final scale/readability review. Native integration follows that work. No flashing occurred.

## Rebuild

From repository root with the configured Pillow/resvg environment:

```powershell
python tools/build_forge_state_flows.py build-work/journeys-rebuild
python tools/verify_forge_state_flows.py build-work/journeys-rebuild --node node
```

Keep relative source links when opening SVGs in Inkscape. Packaged checkpoints are immutable; draft repair requires `--resume-draft`. An exact SVG source match permits reusing its existing PNG render during a draft rebuild.
