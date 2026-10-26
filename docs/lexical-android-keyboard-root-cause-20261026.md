# WISHCODE-LEXICAL-INPUT-001 — confirmed Android text insertion gap (2026-10-26)

## Status
SOURCE-DIAGNOSED / PHONE-REPRODUCED by user. **NOT FIXED**, **NO BUILD**.

Base: WishCode Preview 005 successful APK source SHA `457adbdf75fc62a5c05bca4323f0188cea1e5663`.
Isolated branch: `work/wishcode-lexical-input-20261026`.
User has verified on OnePlus PLK110 / Android 16 that Standard APK with Shizuku and accessibility can type Unicode into the OS Settings search box, but not the DSH session's Lexical composer.

## User-device receipts (provided verbatim or summarized)
- `/app/ui/tree`: 34 nodes; sole editable `text=""`, not focused, bounds `[62,2373,1189,2485]`.
- `/app/ui/node?action=focus`: `SCREEN_ACTION_SUBMITTED`, `accessibilityAction=1`; new tree has editor bounds `[62,1291,1189,1404]` with IME expanded and visible caret.
- `/app/ui/input` and MCP `android_type`: `accessibilityAction=2097152` (`ACTION_SET_TEXT`), `actionAccepted=true`, `effectVerified=false`, but screenshot remains placeholder and repeated tree reads show `text=""`.
- Physical screenshot-coordinate `android_click`: `STALE_FRAME/OBSERVED_REGION_PIXELS_CHANGED` on streaming transcript (user reports ~40 attempts); script must never bypass this safety check.
- ADB `input tap` via device shell: `[POLICY_BLOCKED]` (126); do NOT retry via other interpreter or channel.
- OS Settings search field focus + text: `ACTION_SET_TEXT` accepted and `/app/ui/dump` confirmed literal `你好，测试123`; so the device input capability is operational.
- Attached `verify-input.webp` is a user-described relative link, **not** a verified file accessible to this GitHub branch.

## Verified source mechanisms
1. Pinned DSHA `v0.2.1-rc.2` `app/src/main/java/com/deepseekharness/app/screen/ScreenActionExecutor.java`: operation `input` uses `AccessibilityNodeInfo.FOCUS_INPUT` and `ACTION_SET_TEXT`; `semanticOutcome` explicitly tags `SCREEN_ACTION_SUBMITTED` and `effectVerified:false`. This is the correct report for Android accepting an action.
2. Same file exposes semantics `/app/ui/tree` plus leased `/app/ui/node?action=focus|click|set_text`; coordinates require a fresh observed screenshot, with per-frame pixel consistency. These invariants must remain.
3. Pinned DSHA browser file `app/src/main/assets/app-integration/client.js` already locates per-session shell using `ctx.conversation.input.for(binding.ctx)` and checks retained main-view session identity.
4. Public DeepSeek Harness source `packages/client/ui-conversation/src/client/input/facade.ts` documents `InputActions.captureInsertion()` and `InputActions.insertText(text,span)` with per-revision guard. `SessionInputShell` has `actions` and `state.getSnapshot().draft`. DSH editor is Lexical, not a plain textarea.
5. Pinned DSHA standard WebView is hosted in `WebPreviewActivity.java`; it enforces current page, same-service origin and active-generation checks. Mobile CSS file `scripts/wishcode-mobile.js` is presentation-only and must not be repurposed into unguarded phone automation.
6. GitHub public master source is not necessarily byte-identical to the installed `@deepseek-ai/dsh-client-ui-conversation` NPM bundle in 005; DO NOT search-and-replace minified guest `client.js` without exact input hash/diff and recovery plan.

## Recommended implementation design
Implement a minimal **authorized, focused-only** route for the current native app WebView, without weakening device policy:
- Keep current `/app/ui/input` authorization, target identity, policy, Android accessibility path for ordinary apps.
- Only when target is the exact current WishCode own WebView editor and its editable root is already focused, resolve the **current retained** Session and its `SessionInputShell` through `app-integration/client.js` (not DOM mutation).
- Capture insertion revision then use `shell.actions.insertText(text, shell.actions.captureInsertion())`, respecting locked/submitting states and user edits. Do NOT call `setDraft` on an existing draft as it destroys chips or quotes. Do NOT auto-submit.
- Re-read `shell.state.getSnapshot().draft` after commit. Report `INPUT_VERIFIED` only when actual draft state reflects the inserted text, not because the browser/native method returned true. Return NOT_FOCUSED or RESULT_UNKNOWN honestly.
- If page/current Session changes, the operation is uncertain; never replay blindly. No arbitrary JS execution endpoint, no embedding a bridge token in URLs, no unguarded public WebView methods. Keep session grants, origin and page identity.
- `focusDraftEditor` is a useful real-user-gesture focus utility but does NOT alone repair `ACTION_SET_TEXT` on Lexical; user's focus experiment already succeeded. Do not force keyboard on every new session or steal focus from overlays.
- Optional: expose a user-initiated native action for focusing the composer; preserve input/editability and current Session checks.

## Acceptance
1. Test 005 baseline: accessibility focus opens IME; `ACTION_SET_TEXT` erroneously returns accepted without content; preserve evidence.
2. On new independent APK identity, with user confirmation, invoke an authorized tool; verify existing draft is preserved, test Chinese+ASCII and newline, focus-loss refusal, session switch, concurrent user edit, app background, lifecycle cancellation and 2000-character limit.
3. Standard physical screen and third-party apps must continue using existing accessibility `ACTION_SET_TEXT`. Never relax `STALE_FRAME`, scope, per-session authorizations, or blocked device shell policy.
4. Publish exact branch SHA, static tests, Gradle logs, real APK and phone screenshots/dump. Until real phone test, mark FIX-CANDIDATE only.
5. Build policy: workflow_dispatch only, do NOT change `main`, no automatic builds/retries/cloud fees.
