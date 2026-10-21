# Publication adjustment

Automatic approval review rejected upload of the optional `.apk.idsig` sidecar, classifying that payload as a private signing keystore. The upload was not retried through another encoding or archive. The sidecar was removed from the published file set and source archive, v4 sidecar generation was disabled, and the ordinary v2/v3-signed APK was rebuilt and verified twice. The actual local development keystore remains in ignored build-work only and is never packaged.

Android's [v4 documentation](https://source.android.com/docs/security/features/apksigning/v4) describes `.idsig` as a separate incremental-install signature and documents normal installation fallback when it is absent. This checkpoint supplies the normal APK without that optional sidecar.
