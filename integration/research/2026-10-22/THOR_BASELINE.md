# Thor integration baseline research — 22 October 2026

The user selected **current official LineageOS 24.0** for native integration. Earlier Android 16 artwork remains shared design input; the new native baseline is Android 17. This record is research and acceptance criteria, not a claim that a ROM has been built or installed.

## Verified upstream identity

- Official target: `odin2thor`, product `lineage_odin2thor`, model `Thor`, vendor AYN.
- The current official wiki data lists branch 24.0, Android 13 stock-firmware prerequisite, A/B layout, recovery partition and QCS8550 common/kernel sources. Its listed display pixels are 1920×1080 upper and 1240×1080 lower; these are not application dp or fixed runtime display IDs.
- Upstream build-target configuration lists `odin2thor userdebug lineage-24.0 W`. A scheduled target is not proof that a particular downloadable build exists or has passed verification.
- Older `lineage-23.2` device sources also exist, but the user explicitly selected 24.0.
- **Do not select bare codename `thor`: official Xiaomi 12S Ultra sources use that codename.** AYN's stock `kalama` property from older local notes also does not substitute for current runtime verification or an upstream target name.

Primary sources consulted:

- https://raw.githubusercontent.com/LineageOS/lineage_wiki/main/_data/devices/odin2thor.yml
- https://raw.githubusercontent.com/LineageOS/android_device_ayn_odin2thor/lineage-24.0/lineage_odin2thor.mk
- https://raw.githubusercontent.com/LineageOS/hudson/main/lineage-build-targets
- https://github.com/LineageOS/android_device_ayn_odin2thor
- https://download.lineageos.org/devices/odin2thor/builds

The normal wiki/download HTML endpoints were inaccessible to the web reader in this pass. Do not infer a downloadable release artifact, exact build date, checksum or installed-device compatibility from that failure. Pin source revisions and inspect a real download manifest before building against it.

## Factory ROM search

Candidate: `Thor_20260112.7z`

https://drive.google.com/file/d/1juGydm1H_PF-ECImn-8t4tWWYSaW0oZ1/view

The Drive page title confirms that filename. A community discussion says the upload was supplied by AYN and linked in its Discord `thor-general-faq`; that statement is a lead, **not independently verified manufacturer provenance**:

https://www.reddit.com/r/AynThor/comments/1vghph7/could_anyone_point_me_to_the_original_thor/

AYN's public Firmware page was inspected. It lists older Loki/Odin packages, and no Thor package was present in the retrieved content:

https://www.ayntec.com/pages/software

The candidate was downloaded to the local `Firmware_Research_2026-10-22` folder: **1,932,656,353 bytes**, SHA-256 `a5421469ae42e40264d3475e25fcd9963ec81658f2081d66c4f7c901d2528029`. Its 97-member inventory contains boot/init_boot/vendor_boot/recovery, dtbo, vbmeta/vbmeta_system, split super/userdata images and rawprogram/patch XML: a full partition/EDL-style bundle rather than an OTA ZIP. Selected metadata/images were read using Windows bsdtar without executing any bundled utility. `DISK` references in patch XML refer to disk patch operations, not a missing downloadable image.

Both inspected standalone vbmeta images have valid RSA/SHA-256 signatures against their embedded public keys, with AVB disable flags clear. **Their signing keys are not yet established as trusted AYN keys**; valid signatures alone do not authenticate the manufacturer or prove device compatibility. The report records their public-key fingerprints. Full vendor APK/partition hash verification, exact firmware identity and independent manufacturer provenance remain pending. The local firmware bytes are excluded from Git/public artwork packages.

See `factory-candidate-inspection.json`, `factory-full-read.json` when available, and `apk-signature-audit.json` for separate evidence layers. Do not call an archive/hash alone an authentic factory ROM and do not execute bundled flash utilities.

## Signing requirements

Every produced APK must pass Android `apksigner verify --verbose --print-certs`, have its intended signer certificate fingerprint recorded and match the certificate required for updates. Align before signing and do not modify afterward. Development-signed previews remain clearly labelled development; public AOSP test keys are not production signing keys.

ROM target-files, embedded APKs/APEXes, OTA packages and AVB have different signing and trust requirements. A signed ordinary APK does not establish platform privileges or prove an OTA is accepted by recovery. A cryptographically valid signature does not establish OEM provenance without a trusted signer comparison. ZIPs containing SVG/PNG artwork are source archives, not Android install packages.

Keep private signing material, passwords and unlock data out of Git, source ZIPs, logs and uploads. Reuse a stable existing project signing identity where valid; do not silently rotate it or claim access to LineageOS/AYN private keys. New distributable native work must have a reproducible sign-and-verify gate before publication.

Primary guidance:

- https://developer.android.com/tools/apksigner
- https://source.android.com/docs/core/ota/sign_builds
- https://raw.githubusercontent.com/LineageOS/lineage_wiki/main/pages/signing_builds.md
- https://android.googlesource.com/platform/external/avb/+/refs/heads/main/libavb/avb_vbmeta_image.h

No device write, unlocking, installation or flashing is authorized by this research record. No native integration is counted complete on source/preview checks alone.
