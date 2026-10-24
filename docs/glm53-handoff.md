# GLM-5.3 integration / WISHCODE-ANDROID-PREVIEW-001

Built preview baseline: `3f2054fd77d3aa5f704f34963405f7900077d013`, Actions run 40055903973 succeeded once. Its APK does **not** contain GLM. APK SHA-256: `a19bed29af0e9c0b21e96c65a92566d7254270098fb75fc7d04479d2690d1de5`.

## User flow

After initializing the runtime, open the WishCode home screen → **GLM-5.3 · API / 套餐设置**. Choose ordinary API or Coding Plan and paste that channel's API key. Blank input preserves the old key; the checkbox removes it. Keys are masked and never loaded into chat or included in diagnostics. Return to chat and select **智谱 GLM-5.3 · 普通 API** or **智谱 GLM-5.3 · Coding Plan 套餐** in the model menu. Each request reads the selected route's saved key. No automatic fallback between channels.

Ordinary API: `https://open.bigmodel.cn/api/paas/v4/chat/completions`.
Coding Plan: `https://open.bigmodel.cn/api/coding/paas/v4/chat/completions`.
Only mainland official endpoints are included. A subscription must actually be valid for the account; this integration does not grant quota.

Model `glm-5.3`, text only, thinking always enabled, efforts low/high/max (default max). Advertised context 1,000,000; default per-request output 16,384 (validated upper cap 128,000). Native DSH approval/tool execution remains responsible for accepting and executing tool calls.

## Implementation

`plugins/dsh-wishcode-glm` implements the pinned DSH LlmAdapter contract. It translates streaming reasoning/text/tool fragments and replays assistant reasoning and tool call/result IDs. Truncated streams, invalid tool JSON, images, unexpected models and unsupported efforts fail explicitly. Transport performs one POST, refuses redirects, accepts cancellation, and applies a five-minute request deadline. Errors contain fixed diagnostic codes / HTTP status, never response bodies or keys.

Native credential editor uses AtomicFile and mode 0600 in the app-private guest home, suppresses screenshot capture on its dialog, and disables autofill/view-state saving for its password field. Separate channel keys coexist. Builtin registry and managed runtime install manifest include all four plugin files; the original registration script repairs peer dependency links. Build version increases to 192, without changing main or the preview package identity. ColorOS system font is retained.

## Verification / limits

- 24 Python/Java host tests pass, including 45 existing Java URL/HTTP assertions and Java syntax parsing. This is not Android type checking.
- 5 Node protocol tests pass: UTF-8/SSE fragmentation, interleaved tool calls, reasoning/tool-result replay, usage accounting, truncated/invalid responses, forced thinking, route separation, HTTP errors without retries, cancellation.
- Plugin imported with actual `@deepseek-ai/dsh-llm@0.2.1-rc.2`; both route registration and model metadata succeed.
- Applied source patches to clean pinned upstream; generated builtin Java registry verifies; runtime install manifest validates all four plugin files.
- Full local runtime descriptor is blocked by omitted `glibc-python.tar.gz` in the Git checkout; the existing authorized-build workflow downloads the full checksum-pinned upstream source release. This check is still required in the next authorized build.
- GLM changes are **not yet APK compiled**, called against a real account, or tested on a phone. Test credentials used in mocks are synthetic. No model billing was incurred by these tests.
- Debug APK builds use runner-generated signing keys. Do not assume the next APK can update an already installed preview: compare signing certificates first; back up user projects before any uninstall.

## Required device acceptance

Configure each channel independently; verify model menu labels, one conversation and a user-approved tool call followed by a response. Cancel during thinking. Try wrong key/exhausted quota and verify no channel switch. Ask the model to create a static page, start a local server, open native preview, click/type, return to chat, modify and refresh. Verify pinyin font layout, rotation, scroll, back navigation and existing DeepSeek selection on the target ColorOS device. Never publish device compatibility without this evidence.

Official references checked 2026-10-24:
- https://docs.bigmodel.cn/cn/guide/models/text/glm-5.3
- https://docs.bigmodel.cn/cn/coding-plan/latest-model
