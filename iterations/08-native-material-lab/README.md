# Ember Steel Material Lab 0.1.0

A standalone native Android preview APK for the four scalable frames from iteration 07. Package: `com.craftageddon.materiallab`, minimum API 26, target API 36. It has no requested permissions, services, network access, hardware-control backend or privileged integration. It is separate from the earlier `com.craftageddon.preview` application.

The application source provides native NinePatchDrawable resizing, live text, full/240dp target widths, 100/130/160/200 percent specimen text, LTR/RTL with an Arabic target label, cold inspection and disabled state. Focus and selection are independent layers and survive a held press. Material lighting is static and schedules no animation callbacks; button elevation animators and ripple backgrounds are removed. Native input widgets can still blink their cursor. Native text/layout and inset handling require runtime inspection.

D-pad traverses the app's own controls. Generic Android BUTTON_A is translated to DPAD_CENTER within this foreground window; BUTTON_B exits the preview. This is a test convention, not a verified mapping for the Thor's physical buttons. There is no global controller capture and no game/profile service. The app reports its actual current display ID without assuming upper/lower device IDs.

## Saved output and verification

`release/EmberSteel-MaterialLab-0.1.0.apk` is locally signed for development, not production. It verifies with APK v2/v3 signatures and installs through the normal package installer without an incremental-install sidecar. No keystore, signing key or idsig file is included. The source ZIP includes Java, manifest, all 80 density resources, four editable SVG masters and an offline build script. The builder disables optional v4 sidecar generation.

Resource compile/link, Java compile, DEX build, all 80 compiled nine-patch chunks, package identity, absence of requested permissions, signature and ZIP alignment were checked. A fresh build with the same local development key reproduced every executable/resource ZIP member. Signed APK bytes differ because archive/signing containers are not normalized; a bit-reproducible APK is not claimed. Logs and hashes are under verification/evidence.

**No installation or runtime rendering test has been performed.** No emulator system image was present in the inspected SDK. Physical Thor V3, input behavior, rotation restoration, insets, RTL/large text, actual rendering, accessibility and performance remain unverified. This is a built application checkpoint, not a completed native theme or ROM.

## Build offline

Requirements: Python 3.10+, installed JDK 21, Android SDK platform android-36.1 and build-tools 36.1.0. No Gradle, downloaded dependencies or network are needed. Extract the archive, then run from its folder (replace tool paths):

```powershell
python build/build_material_lab.py --root . --work rebuild --release-dir rebuild/release --report-dir rebuild/evidence --sdk 'C:/Users/you/AppData/Local/Android/Sdk' --java-home 'C:/Program Files/Android/Android Studio/jbr'
```

The builder refuses to overwrite a work/release directory. Use a new work folder per rebuild. It creates a local debug keystore inside that work folder. `--keystore path/to/existing-debug.keystore` can reuse the standard `androiddebugkey` alias/password for local preview updates; keep that private file out of published source. A different key cannot update an already-installed package without removing the earlier preview.

The Windows linker crashed with access violation inside this session's sandbox, even for an empty package. Normal local execution outside that instrumentation succeeded; see iteration 07's environment evidence. The delivered APK was built successfully there.

## Optional local test and removal

After choosing a test device and confirming its identity, the user can install this ordinary application with Android's package installer or `adb -s SERIAL install release/EmberSteel-MaterialLab-0.1.0.apk`. The build never installs automatically. Remove it through Android Settings or `adb -s SERIAL uninstall com.craftageddon.materiallab`. It does not replace SystemUI, launcher, keyboard or firmware. The unrun test matrix lists the required review cases.
