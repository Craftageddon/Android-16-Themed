# Forge 19 - actual OS resource audit

The source comparison found 16 confirmed semantic symbol-coverage gaps, 20 additional source app/component binding targets, and 7 groups of exact-owner layout/output adaptation. Read VISUAL_GAPS.md for the prioritized work and exact upstream references. The preview sheet shows the missing upstream glyph families; no new Forge artwork was designed in this audit.

This is a source audit pinned to the official 2026-10-19 LineageOS 24.0 odin2thor build manifest. It covers 31 projects and five complete framework sections, 16,559 candidate visual/UI source files and 10,926 qualified source families. Every included tree is untruncated; the initial oversized framework response was rejected. 554 selected source files were downloaded and verified against their Git blob hash and saved SHA256.

Only 16 semantic families are confirmed missing. The 7,048 unassigned source families are an explicit review queue, not 7,048 asserted missing drawings. Name-based reuse candidates, native layout/token work, native motion and test/demo resources are separated. A source file, candidate icon name or product declaration does not establish visibility on a built Thor image.

The additional app list contains component/home roles as well as seven manifests with launcher declarations. It does not assert 20 new installed launcher icons. Exact package IDs refer to platform manifests; development variants and merged manifests can differ.

Full raw JSON/CSV, source bytes, tree evidence, donor references and reports are in the signed complete-assets.zip. Git stores compressed equivalents of the largest inventories to avoid duplicate text storage. Standard gzip tools recover those files; the audit scripts read compressed equivalents directly. Compressed JSON/CSV contain identical bytes.

Regenerate source inventory, selected evidence, conservative comparison and independent verification from the repository root:
- python tools/audit_os_resource_coverage.py
- python tools/inspect_os_resource_evidence.py
- python tools/report_os_resource_coverage.py
- python tools/verify_os_resource_audit.py

The builders refuse to rewrite a packaged checkpoint. Preserve this checkpoint and use an explicit new output location/iteration for new research. source-tools/ contains the saved audit tool sources; the full repository supplies the pinned baseline and existing artwork inputs. Network reads retrieve primary public source only; upstream code was not executed.

This audit is signed with the existing pinned Craftageddon RSA-PSS source-artifact identity. It is not an APK, OTA or firmware package. Existing 472 master hashes remain unchanged. No Android/device execution, OS edit, hardware setting, install or flashing occurred. Built-ROM reachability, overlay precedence, private/vendor/GMS content and the actual installed-app list remain unresolved. Upstream notices remain with their reference sources.
