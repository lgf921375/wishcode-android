# WishCode Preview 005: manual build #15 failure and targeted fix

Date: 2026-10-26.
Failure URL: https://github.com/lgf921375/wishcode-android/actions/runs/40275902091
Build #15 ran on build/wishcode-v05-preview005-manual-20261026-83437b8, SHA 83437b8dc81dc457dad02cf252b2ed7e91cac1f8.
Build #15: 1m24s, failed at step 'Compile real Standard Debug APK' before Java compile or APK signing.

## Primary source evidence

All initial unit tests, Node checks, upstream source SHA, Android SDK, Flash archive smoke, DNF archive smoke, managed runtime descriptors and AAPT2 pin passed.
Task :app:prepareStandardAssets failed while tools/prepare-standard-assets.py invoked tools/asset_deployment.py.
Exception: ValueError: ASSET_DEPLOYMENT_UNREGISTERED:wishcode/dsh-purge-flash-v1.4.0-compat.tgz.
Second archive under wishcode/ was similarly missing from the upstream strict deployment allowlist.

## Repair

Created scripts/register_wishcode_assets.py. After generating the two exact opt-in .tgz archives, validate their report SHA256s, native reader literals and original manifest schema. Append precisely two new relative paths to tools/asset-deployment.json packagedFiles, and one explicitly scoped dynamicReaders entry for WishCodeHomeActivity.java. Do not exempt a directory, disable original guards or auto-install plugins.
The workflow now invokes this script before Gradle and runs the upstream verify_reader_contracts(source, load_manifest(), repository=...) directly.
Added scripts/test_asset_deployment.py for exact list preservation, idempotent fail-closed behavior, checksum mismatch refusal and reader anchor drift.
Added registration report to build artifact.

## Remaining work

Source-level static verification completed. CI/runtime verification of newly modified asset registration is NOT yet complete; no subsequent build was started. If the next manual run fails, inspect its first failing step before deciding on further changes. Do NOT rerun historical #15 on its old SHA.
Review separately on real phone: .tgz export and user-confirmed import, /armor status, DNF skills, plugin forms, ColorOS font, screens 320-600px.

Do not modify main, DNF Unity/Godot source branches or trigger an automatic build.
