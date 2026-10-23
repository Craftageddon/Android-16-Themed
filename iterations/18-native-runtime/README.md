# Forge native runtime 0.1.0 - API 37 integration checkpoint

This is the first current-style native implementation for the selected AYN Thor / LineageOS 24.0 target. The signed application uses actual Android Button/ToggleButton state, compiled scalable nine-patches and independently tinted neutral masks. Off/unselected and explicit-off controls stay cold. Selected/checked turns on ember; focus alone is cool. Native labels and readouts are English (en-US).

The application contains:
- Native steel toggle, explicit cold-only toggle and unavailable control, with live labels and checked-state semantics.
- Actual OS Quick Settings TileService sharing the selected state with the app. Add Ember control through the system tile editor during a separately chosen test session.
- A battery readout using the real system battery broadcast, read-only display modes/controller discovery, and controller key/axis event inspection. Unknown data stays unavailable; no fixture is presented as a hardware reading.
- 112 unchanged compiled nine-patch sources in four density sets, one cold adaptive launcher icon, 25 English strings and a 64-combination state test.

The Quick Settings service is a real SystemUI extension. Its tile uses the operating system's tile surface; this package does not replace protected SystemUI surfaces with the new material. The steel controls render inside the application. Full SystemUI/Settings/launcher/IME/lockscreen integration, all 472 visual masters, 114 native motion recipes, dual-screen routing and hardware profile/calibration backends remain subsequent work.

The exact official Thor source build manifest and Compose tile-owner revisions are recorded under upstream/ and the repository research folder. The pinned Android 17 owner is qs/panels/ui/compose/infinitegrid/Tile.kt and CommonTile.kt. The older QSTileViewImpl hook is absent. A future platform patch must preserve existing tile semantics, dual-target clicks, expansion, haptics, focus and squish behavior. No platform patch or full ROM was built here.

Build from the full repository root with its documented installed SDK/JDK:
    python tools/build_native37.py
Verify a separate clean build and state/style parity:
    python tools/verify_native37.py

SDK platform android-37.0 and build-tools 37.0.0, JDK from Android Studio, Python and the existing signing helper are required. source-tools/ preserves exact helper sources; the full repository supplies paths/provenance inputs. Each build uses a fresh ignored build-work folder. There is no install/flash step.

package/Craftageddon-Thor-Native-0.1.0.apk is signed and aligned. APK certificate DER SHA256:
24426da343edf38e344e9109f995ae353b5a2da9e3c351cf321368951e3541da

This stable Craftageddon application identity is distinct from the source ZIP RSA-PSS identity and from AYN/LineageOS platform keys. The encrypted PKCS12 key and Windows-user DPAPI password stay under ignored local-secrets/apk-signing; private material is not included. Preserve that private identity securely for update continuity. Do not replace upstream system packages with this unrelated signer.

Two clean builds match all 119 executable/resource members; the complete APK byte hash can differ with ZIP timestamps. apksigner verifies the actual final APK, the expected stable certificate matches, zip alignment passes, and a tampered APK is rejected. The application requests no permissions; its exported tile service is guarded by Android's BIND_QUICK_SETTINGS_TILE permission.

V1/V2 pass the bounded source/build/signing checks. Android execution, native pixel/blend comparison, controller mappings, lifecycle, accessibility, display behavior and physical V3 are NOT RUN. The user chose to continue without a connected device. No hardware was installed, modified or flashed. This is a signed integration checkpoint, not a production ROM or device-accepted release.
