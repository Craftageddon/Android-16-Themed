# Signing and trust gates

The user requires signed packages. Signature checks are specific to each artifact type; do not substitute a SHA-256 manifest for a signature or a valid signature for an independently trusted manufacturer.

## Source/design archives

New complete source ZIPs have a detached RSA-PSS-3072/SHA-256 signature, a public key and a public-key fingerprint pinned in the versioned checkpoint. `tools/sign_artifact.py verify` checks the complete bytes and caller-supplied expected key fingerprint. The private key is encrypted with a random password protected by Windows current-user DPAPI, under ignored `local-secrets/artifact-signing/`; neither key nor password is included in Git or archives. Existing complete identity is reused and an incomplete identity is rejected rather than silently replaced. Back up the private identity and its Windows-user recovery access securely before relying on it for long-term release continuity.

This is a Craftageddon artifact-signing identity, not an Android package, OTA, AVB, OEM or upstream LineageOS release certificate. A standalone signature only proves possession of that key; establish trust in the expected fingerprint through the pinned project checkpoint. Signature metadata is alongside the ZIP and excluded from ZIP input to avoid recursive signing.

## Android APKs

All distributable APKs must be aligned before signing, pass `apksigner verify --verbose --print-certs`, and match their documented expected certificate fingerprint. Reject altered packages and unexpected signers. Keep development identities explicitly labelled development. A development key is not promoted to production release eligibility by a successful cryptographic check.

The three retained preview APKs were verified on 22 October 2026. They have valid signatures using existing development identities, not platform privilege or completed production trust. The audit uses actual installed Android build-tools 37 output, including its newer V3.0 Signer label. Tampered-APK and wrong-certificate tests were run; development packages stayed ineligible for release.

Future LineageOS 24 native integration must provide its own stable project application signing identity and actual owner/privilege integration evidence. Do not overwrite upstream system APKs with an unrelated key, silently rotate installed-package identity, use public AOSP test keys for production, or claim access to AYN/LineageOS private keys.

## ROM / OTA / AVB

Use the upstream target-files signing flow with explicit APK/APEX, OTA and AVB key mappings. Recovery trust and update continuity must be checked independently. Downloaded upstream ROMs are inspected without re-signing them. An original factory candidate's embedded signatures are not authenticated to AYN until their keys/provenance have an independent trusted comparison.

See research/2026-10-22/ for current evidence. No package is marked production/device accepted merely because a source checkpoint passed desktop QA. No flashing is performed by these tools.
