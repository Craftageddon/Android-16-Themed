# Native implementation review - 23 October 2026

V1 scope: begin native integration after consolidating the current authored visual handoff. Five Java source classes compile against API37. Android widgets own checked, selected, pressed and focused states; no artwork label is rasterized. Neutral light masks tint independently. No timer, idle glow, hardware setter, installer, bootloader or firmware operation is present.

V2 evidence: a fresh separate build preserves all 119 executable/resource members and the stable application certificate. Sixty-four exhaustive state combinations pass. Seven compiled Java state samples match the approved desktop style JSON exactly; disabled/explicit-off rules hold. 115 reused visual source resources match their original hashes; 25 native strings use English. The built manifest targets37/min33, requests no permissions, and protects the real exported Quick Settings tile service. Signature, alignment and tamper-rejection checks pass.

Actual behavior implemented: app selection and system tile share local state; battery listens only while the activity is started; display/controller details are read on start and refresh; actual controller events are reported without suppressing normal Android dispatch. The package changes only its own preference when its control is used.

Limits: clean compilation and unit checks do not establish Android execution or visual parity. No emulator image or physical device was used. Native rendering, text scaling, lifecycle restoration, focus navigation, TalkBack, actual Thor axes, upper/lower display routing, memory/GPU/battery budgets and V3 remain NOT RUN. The system tile surface is still platform-rendered. No patched SystemUI or ROM was compiled.

The pinned upstream Compose sources retain their original notices and are reference inputs, not CC0-authored application code. Future platform work must target those owners rather than removed legacy tile-view classes.
