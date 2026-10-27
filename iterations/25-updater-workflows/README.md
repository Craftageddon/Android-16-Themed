# Forge 25 — updater workflow artwork and source handoff

Actual updater main screens, device banner, preferences, interval picker,
operation dialogs, local import, checking/error/zero illustrations, action
glyphs and adaptive identity now have scoped steel presentation. Eight new
layered drawings and three optical material treatments extend the prior art.
Cold bases and neutral light masks stay separate. Native text stays live and
defaults to English; no lettering or ember is baked into production skins.

Running operations glow; paused/suspended/ready/reboot states stay cold.
AC-forced-on preferences stay on/glowing while interaction is locked.
Focus/hover stays cool; enabled pressing is momentary ember. Error light is
transient red, ending cold, rather than a selected/on state. Original Lottie
JSON provides timing; new geometry replaces the old visual/morph paths.

## Usable outputs

- Updater-forge-workflows.patch: combined text patch against exact Updater
  revision6d50e0bf1b16fe7bca818375a3e734f4959e2e57.
- native-patch/packages/apps/Updater:480 PNG configurations (68 cold/412 neutral
  masks), including168 exact prior reuses. Copy binaries to module-relative
  paths after applying text patch; current-native-files.json lists33 text files.
- masters:8 new editable SVGs,3 material-only optical derivatives, exact original
  aliases and portable texture inputs. Earlier canonical masters stay unchanged.
- workflow-previews:25 screen/control/dialog and18 operation-card fixtures,
  editable SVG plus PNG. previews contains7 comparison sheets.
- owner-binding-review.json, full semantic ledger and verification/evidence:
  explicit source decisions, checks and remaining target gates.

Fixture metadata is sample data. Segoe UI/layout/glyph/progress metrics are
desktop approximations, not Android screenshots or installed-device facts.
Large-font fixtures show full content; native viewport scrolling is untested.

The source600dp breakpoint/equal wide panes, native scroll/data/link owners,
A/B and recovery-presence branches, repository callbacks and original logging
wrappers stay in place. Interval selection closes before its original callback.
Import remains noncancelable with unchanged show/dismiss/success/error flow.
Shared notification silhouettes and native QR generation/payload stay exact.
The rich dialog badge is scoped separately; no notification raster substitution.

## Verification and limits

Bounded checks pass:90 pinned source/dependency identities;16 reverse-byte owner
chains;clean33-file patch parity;480 layer exports;168 exact reuses;17,720
assertions against actual compiled pure presentation classes;234 phase cases;
strict XML/English desktop bounds;472 earlier master hashes;unchanged signed24
ZIP. The cold badge fits the66/108 adaptive safe circle with18% foreground inset.

SDK37 compiles all patch resources and links a separate rendering bank.
Six actual Java classes,nine whole Kotlin files and a verbatim source enum
compile with recorded Kotlin/Compose2.3.21,cached Material3 1.4.0 compatibility
libraries. Actual Lottie6.5.2 artifacts match official Maven SHA512 sidecars.
Verification outputs are not installable apps or official pinned Soong builds.

Actual SPA public-model adapters and complete private Updater owners are NOT
compiled. Full pinned Soong,effective resources/overlays,Android rendering,
scroll/input/accessibility/lifecycle/animator behavior and physical Thor
acceptance remain NOT RUN. Static API/source review does not replace these gates.
TV QR output is not simulated as a working code. No updater/controller/installer
or hardware operation is executed. V1/V2 pass for bounded source/art/desktop
scope only;V3 is unrun.

The whole goal remains active:9,624 open family decisions;W03/W05/W07 still
unauthored;W04 consumer review/native gates incomplete;remaining app/glyph owners,
further discovered art and final independent whole-goal review still required.
Updater legacy launcher foreground/background and ic_system_update remain open.
Preserving them does not establish global unreachability or finished coverage.

Original code/geometry retains notices/Apache-2.0 terms;new art uses project
CC0 terms. Source artifact signing identifies a checkpoint,not APK/OTA/AVB trust.
Restore distribution parts with Restore-Archive.ps1.

## Reproduction

Preserve frozen24. In a scratch copy retain exact24 inputs,run
bind_updater_workflow_owners.py before recorded glyph-owner-edits.json operations.
Apply those glyph operations with exact occurrence/input/output hash checks.
Current editable helpers are authoritative;do not rerun earlier owner stages
over later edits. Run build_updater_workflow_art.py,snapshot_updater_workflow_patch.py,
compile_updater_workflow_sources.py,preview_updater_workflow_art.py,
render_updater_workflow_fixtures.py,render_updater_workflow_cards.py and
verify_updater_workflow_stage.py with recorded runtime/render library/SDK37/JDK.
Windows SDK compilation runs on host.Builders refuse to rewrite packaged outputs.
