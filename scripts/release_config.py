"""Single source of truth for WishCode's Android release identity.

Temporary debug-signed builds use a NEW Android application ID for each trial
so they can coexist with previous builds without uninstalling user data.
A stable signing key is required before changing to an in-place upgrade path.
"""
APP_ID = "app.wishcode.harnessmobile.v05trial4"
VERSION_CODE = 194
VERSION_NAME = "0.5-preview-004-armorcompat-dsh0.2.1-rc.2"
APK_NAME = "WishCode-v0.5-preview-004-armorcompat-no-glm-arm64-debug.apk"
ARTIFACT_NAME = "WishCode-V0.5-Preview-004-ArmorCompat-Android-APK"
