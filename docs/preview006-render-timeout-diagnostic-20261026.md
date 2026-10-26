# WishCode 006: isolated trial renderer diagnosis — 2026-10-26

## Evidence from user's two 2026-10-26 reports
- First input `DSHA-diagnostic-20261026-151408.txt` contains 212 lines; second `151322.txt` contains only an empty reproduction-notes section.
- OnePlus PLK110, Android 16 (API 36), Google System WebView 155.0.8059.43, 4 KB memory pages.
- Default and actual mode: proot; cold `CONFIGURED_TOOLS_CHECK_PROOT exit=0`, disk available around 280 GiB.
- Isolated DSH emitted `DSHA_TRIAL_NATIVE_CHECK_READY`, storage, fresh, session, `plugin-ready` around 15,831 ms from trial process start, and a localhost DSH auth URL.
- Screenshot error `TRIAL_TIMEOUT:RENDERING`; exported detail says `trialState=CLOSED`, `runtimeMode=proot`, `error=IO_FAILURE`, `exitCode=running-or-not-started`.
- Existing `RuntimeTrial.latestFailure()` includes raw output and an opaque error code only; the normal GZ summary explicitly does **not** include full trial state or JS/WebView events.
- This is not evidence of failure in the user's opt-in Flash or DNF workflow plugins: the trial uses a separate dsha-runtime-check profile. APK built and signed successfully in Actions #16, but no phone acceptance has passed.

## Mechanism and uncertainty
- `RuntimeTrial.verifyOnce` requires native trial ready; real web auth; per-record filesystem/session reopen; and `renderer === true` from a local trial status endpoint.
- The guest page marks renderer true only after a page-ready signal and the real `/api/remote.mux` WebSocket open + matching ready frame and a successful authenticated POST.
- At least one piece of that chain did not confirm. The uploaded report does NOT reveal which; avoid assigning blame to the Android browser, VPN, Flash plugin, cookie, or WebSocket without additional evidence.

## Source-level diagnostic patch (not an unverified workaround)
- Branch: `work/wishcode-runtime-render-diagnostics-20261026`, based on exact successful build SHA `457adbdf75fc62a5c05bca4323f0188cea1e5663`.
- `scripts/instrument_runtime_trial.py` targets exactly two files from the pinned DSHA source ZIP:
  `RuntimeTrial.java` captures whether the status endpoint responded, whether it ever reported renderer success, and whether the hidden WebView open attempt/attachment happened. This state is saved into trial `failure.json` and surfaced through **最近隔离运行试验**.
  `RuntimeBrowserProbe.java` records non-sensitive cookie accepted/rejected and main-frame finished/network/HTTP errors to host `DiagnosticLog`. Cookie rejection and main-frame failures now return an explicit failure rather than a silent 300 s timeout.
- Keeps the actual auth, nonce, read/write, WebSocket and renderer gates intact. Does not log raw URLs, cookie values, token, user messages or file content.
- No claim of fixing the underlying rendering failure without another phone diagnostic.

## Preview 006 independent identity
- App ID `app.wishcode.harnessmobile.v05trial6`, versionCode `196`, versionName `0.5-preview-006-renderdiag-dsh0.2.1-rc.2`.
- New debug signature means new app cannot transparently replace 005; side-by-side installation retains the original application's data for inspection.
- Manual-only GitHub Actions; no automatically triggered build or retries. No Unity/Godot/other repositories modified.
- Before any user-authorized single build: verify Python and Node tests, exact patch anchors, signing, Gradle, APK identity. Then compare host GZ `TRIAL_WEBVIEW` events and TXT `renderTrace` on the same phone.

## Current status
- Source diagnostics are a **candidate**, not an Android runtime fix.
- No new APK build or real-device test yet; do not present the instrumented code as a successful repair.
