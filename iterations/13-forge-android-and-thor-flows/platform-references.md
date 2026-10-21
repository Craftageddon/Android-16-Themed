# Platform owner references

Consulted 21 October 2026 for concept boundaries, not proof of Thor integration:

- [Android runtime permissions](https://developer.android.com/training/permissions/requesting): request access in context and retain a denial path. Camera prompt artwork here is a visual concept; remaining permission/outcome variants are open.
- [Android photo picker](https://developer.android.com/training/data-storage/shared/photo-picker): selected-media access and provider behavior remain platform-owned. The grid contains original vector placeholders, not user photos.
- [Biometric authentication](https://developer.android.com/identity/sign-in/biometric-auth): platform authentication and credential fallback are authoritative. The socket is decorative artwork; no biometric capability or hardware enrollment was tested.

No privileged service, firmware API, key code, exact display metric or AYN capability is inferred from these general references.
