# Preview 005 Mobile Plugins + DNF Toolkit — 2026-10-26

Branch: work/wishcode-plugin-mobile-dnf-20261026; base d1f8d49c66ea49da3b82fbc91c7c1cd1ce484c56.
Main, Unity, Godot and other project repositories are untouched.

## Scope

1. Authenticated internal DSH WebView mobile CSS for portaled plugin configuration forms: narrowed fields, long labels, ColorOS/Pinyin-friendly line height, grid-to-column under 560px and bounded tables/code. Unknown cross-origin iframe content and custom native screens are not universally transformable.
2. dsh-purge-flash v1.4.0 opt-in bundled compatibility archive: fixed source:string in armor-playbook registration. Real Android plugin loading remains UNVERIFIED. Use genuine /armor status, not an AI-generated status narrative.
3. Original DSH plugin dsh-wishcode-dnf-dev v0.1.0: three on-demand skills wishcode-dnf-combat / wishcode-dnf-art / wishcode-dnf-release for Unity combat, original animation assets and Android manual-build acceptance.
4. Existing GitHub search/read-only plugin installation with version and SHA pin, plus native Git/file/terminal, remains available. Third-party plugins require the user's installation review; neither new archive is automatically activated.
5. No bundled copyrighted DNF assets, Unity Editor or dotnet runtime. Skills improve process instructions but do not create missing build tools.

## Build identity

- APP ID: app.wishcode.harnessmobile.v05trial5
- versionCode 195, versionName 0.5-preview-005-mobileplugins-dsh0.2.1-rc.2
- APK: WishCode-v0.5-preview-005-mobileplugins-no-glm-arm64-debug.apk
- Actions artifact: WishCode-V0.5-Preview-005-MobilePlugins-Android-APK
- Workflow: .github/workflows/build-custom-apk.yml; workflow_dispatch only; no automatic build, retry or push trigger.
- Build outputs include both plugin TAR.GZ packages, individual SHA256 reports, signed APK checks and source SHA.

## Verification gate

Run Python test_dnf_dev.py and previous tests, node mobile CSS smoke, both plugin runtime skill contract smoke checks and Android assembleStandardDebug. Confirm artifact signature, package and version. On phone, check plugin setting modals at 320/360/390/600 CSS pixels and large font sizes. Export both bundled archives, manually import and explicitly confirm. Run /armor status and skill loading. Ensure main and other repositories are never mutated.

## Current state

Source modified and committed to branch. No Preview 005 GitHub Actions build was started; APK compilation, on-device layout and plugin installation are not verified. Do not claim success or provide an invented APK link. Keep existing APK installed because the new debug-signed, separate-ID app cannot automatically migrate its private data.
