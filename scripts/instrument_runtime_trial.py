#!/usr/bin/env python3
"""Add narrowly scoped diagnostics for an isolated DSHA runtime renderer timeout.

The trial's renderer, authentication, storage and WebSocket acceptance gates
remain unchanged. On failure we only record process-independent booleans
and native WebView lifecycle events, never session cookies or URLs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

TRIAL = "app/src/main/java/com/deepseekharness/app/runtime/RuntimeTrial.java"
BROWSER = "app/src/main/java/com/deepseekharness/app/ui/RuntimeBrowserProbe.java"


def swap(text: str, before: str, after: str, key: str) -> str:
    count = text.count(before)
    if count != 1:
        raise ValueError(f"upstream renderer diagnostic anchor drift: {key}: {count}")
    return text.replace(before, after, 1)


def patch_trial(value: str) -> str:
    value = swap(
        value,
        "    Throwable primaryFailure = null;\n",
        "    Throwable primaryFailure = null;\n"
        "    // Contains only finite, non-sensitive phase/status flags; never an auth URL.\n"
        "    Map<String, Object> renderTrace = new LinkedHashMap<>();\n"
        "    renderTrace.put(\"stage\", \"not-started\");\n",
        "trace declaration",
    )
    value = swap(
        value,
        '      markHost(hostTimings, "rendererStart", hostStarted);\n',
        '      markHost(hostTimings, "rendererStart", hostStarted);\n'
        '      renderTrace.put("stage", "status-poll");\n',
        "renderer start",
    )
    value = swap(
        value,
        '        status = status(url.loopbackBaseUrl + "dsha-runtime-trial/" + nonce, exchange.cookie);\n',
        '        status = status(url.loopbackBaseUrl + "dsha-runtime-trial/" + nonce, exchange.cookie);\n'
        '        renderTrace.put("statusSeen", status != null);\n'
        '        if (status != null) {\n'
        '          renderTrace.put("statusRendererTrue", Boolean.TRUE.equals(status.get("renderer")));\n'
        '          renderTrace.put("statusFailurePresent",\n'
        '              !BackupJson.string(status, "failure").isEmpty());\n'
        '        }\n',
        "GET poll status",
    )
    value = swap(
        value,
        '              markHost(hostTimings, "browserOpenStart", hostStarted);\n',
        '              renderTrace.put("browserOpenAttempted", true);\n'
        '              markHost(hostTimings, "browserOpenStart", hostStarted);\n',
        "browser open attempted",
    )
    value = swap(
        value,
        '              markHost(hostTimings, "browserOpenEnd", hostStarted);\n',
        '              markHost(hostTimings, "browserOpenEnd", hostStarted);\n'
        '              renderTrace.put("browserAttached", true);\n',
        "browser attached",
    )
    value = swap(
        value,
        '      detail.put("runtimeMode", runtimeMode);\n',
        '      detail.put("runtimeMode", runtimeMode);\n'
        '      detail.put("renderTrace", renderTrace);\n',
        "failure renderTrace",
    )
    value = swap(
        value,
        '              + (output.isEmpty() ? "" : "\\n" + output));',
        '              + (value.get("renderTrace") == null\n'
        '                  ? "" : "\\nrenderTrace=" + String.valueOf(value.get("renderTrace")))\n'
        '              + (output.isEmpty() ? "" : "\\n" + output));',
        "surface trace in diagnostic report",
    )
    return value


def patch_browser(value: str) -> str:
    value = swap(
        value,
        '          new WebViewClient() {\n'
        '            @Override\n'
        '            public boolean onRenderProcessGone(WebView gone, RenderProcessGoneDetail detail) {\n',
        '          new WebViewClient() {\n'
        '            @Override\n'
        '            public void onPageFinished(WebView view, String ignoredUrl) {\n'
        '              com.deepseekharness.app.core.DiagnosticLog.record(\n'
        '                  activity, "TRIAL_WEBVIEW", "main-frame-finished");\n'
        '            }\n'
        '            @Override\n'
        '            public void onReceivedError(\n'
        '                WebView view, WebResourceRequest request, WebResourceError error) {\n'
        '              if (!request.isForMainFrame()) return;\n'
        '              com.deepseekharness.app.core.DiagnosticLog.record(\n'
        '                  activity, "TRIAL_WEBVIEW", "main-frame-network-error");\n'
        '              failed.accept("TRIAL_BROWSER_MAINFRAME_NETWORK_ERROR");\n'
        '            }\n'
        '            @Override\n'
        '            public void onReceivedHttpError(\n'
        '                WebView view, WebResourceRequest request, WebResourceResponse response) {\n'
        '              if (!request.isForMainFrame()) return;\n'
        '              if (response.getStatusCode() < 400) return;\n'
        '              com.deepseekharness.app.core.DiagnosticLog.record(\n'
        '                  activity, "TRIAL_WEBVIEW", "main-frame-http-error");\n'
        '              failed.accept("TRIAL_BROWSER_MAINFRAME_HTTP_ERROR");\n'
        '            }\n'
        '            @Override\n'
        '            public boolean onRenderProcessGone(WebView gone, RenderProcessGoneDetail detail) {\n',
        "webview client callbacks",
    )
    value = swap(
        value,
        '          ok -> {\n'
        '            if (alive.get() && Boolean.TRUE.equals(ok)) view.loadUrl(url);\n'
        '          });',
        '          ok -> {\n'
        '            if (!alive.get()) return;\n'
        '            if (Boolean.TRUE.equals(ok)) {\n'
        '              com.deepseekharness.app.core.DiagnosticLog.record(\n'
        '                  activity, "TRIAL_WEBVIEW", "cookie-accepted;load-start");\n'
        '              view.loadUrl(url);\n'
        '            } else {\n'
        '              com.deepseekharness.app.core.DiagnosticLog.record(\n'
        '                  activity, "TRIAL_WEBVIEW", "cookie-rejected");\n'
        '              failed.accept("TRIAL_BROWSER_COOKIE_REJECTED");\n'
        '            }\n'
        '          });',
        "cookie acceptance and explicit failure",
    )
    return value


def apply(source: Path) -> dict:
    source = source.resolve()
    original = {}
    updated = {}
    for rel, transform in [(TRIAL, patch_trial), (BROWSER, patch_browser)]:
        file = source / rel
        if not file.is_file() or file.is_symlink():
            raise ValueError("missing strict renderer probe source: " + rel)
        before = file.read_text(encoding="utf-8")
        after = transform(before)
        if before == after:
            raise ValueError("renderer instrumentation produced no change")
        original[rel] = before
        updated[rel] = after
    for rel, value in updated.items():
        (source / rel).write_text(value, encoding="utf-8", newline="")
    return {
        "description": "renderer trial diagnostics only: no readiness bypass",
        "patched": [{
            "path": rel,
            "beforeSha256": hashlib.sha256(original[rel].encode()).hexdigest(),
            "afterSha256": hashlib.sha256(updated[rel].encode()).hexdigest(),
        } for rel in (TRIAL, BROWSER)],
        "guestRuntimeChanged": False,
        "checkpointsChanged": False,
        "containsSensitiveData": False,
        "deviceVerified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = apply(args.source)
    content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.write_text(content, encoding="utf-8")
    print(content)


if __name__ == "__main__":
    main()
