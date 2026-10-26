"""Single source of truth for WishCode's Android release identity.

Temporary debug-signed builds use a NEW Android application ID for each trial
so they can coexist with previous builds without uninstalling user data.
A stable signing key is required before changing to an in-place upgrade path.
"""
APP_ID = "app.wishcode.harnessmobile.v05trial7"
VERSION_CODE = 197
VERSION_NAME = "0.5-preview-007-lexicalinput-dsh0.2.1-rc.2"
APK_NAME = "WishCode-v0.5-preview-007-lexicalinput-no-glm-arm64-debug.apk"
ARTIFACT_NAME = "WishCode-V0.5-Preview-007-LexicalInput-Android-APK"
