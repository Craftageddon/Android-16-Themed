# Detached source archive signature

This complete source ZIP is signed by a persistent Craftageddon artifact key. Public-key SPKI SHA-256:

`efed639940a40e073b8c30f4f515eb7859d65fd03b660e179006798fc9c6ac9c`

Files alongside the complete archive: `complete-assets.zip.sig`, `complete-assets.zip.sig.json`, `signing-public-key.pem`. The signature covers the exact complete ZIP bytes. If restoring GitHub byte parts, reconstruct the ZIP first, then verify its signature. The signature and its metadata are excluded from ZIP inputs to avoid recursion. Public key and this document are included as source; private material is not.

From the repository root, with the Python cryptography package available:

```powershell
python tools/sign_artifact.py verify --artifact iterations/14-forge-atmosphere/complete-assets.zip --signature iterations/14-forge-atmosphere/complete-assets.zip.sig --public-key iterations/14-forge-atmosphere/signing-public-key.pem --expected-key-sha256 efed639940a40e073b8c30f4f515eb7859d65fd03b660e179006798fc9c6ac9c
```

Algorithm: RSA-PSS 3072-bit, SHA-256 prehash, MGF1-SHA256 and 32-byte salt. Verification does not need private keys or Windows DPAPI. This is source-artifact integrity/authorship under the pinned project identity; it does not turn the ZIP into an installable or OEM-signed Android update.
