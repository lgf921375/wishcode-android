#!/usr/bin/env python3
"""Fail-closed 005 source overlay: route authorized self-composer input through Lexical."""
import argparse, hashlib, json
from pathlib import Path

NATIVE = "app/src/main/java/com/deepseekharness/app/screen/ScreenActionExecutor.java"
WEB = "app/src/main/java/com/deepseekharness/app/ui/WebPreviewActivity.java"
CLIENT = "app/src/main/assets/app-integration/client.js"

def change(s,old,new,name):
    if s.count(old)!=1:
        raise ValueError("PINNED_SOURCE_ANCHOR_DRIFT:"+name+":"+str(s.count(old)))
    return s.replace(old,new,1)

def native(s):
    old='''        if (!context.claimDispatch()) return ScreenReply.refused("SCREEN_RUN_CHANGED");
        return semanticOutcome(context, target.performAction(action, bundle), action);'''
    new='''        if (!context.claimDispatch()) return ScreenReply.refused("SCREEN_RUN_CHANGED");
        // Screen authority, current window and focused editor were validated above.
        // All other applications/fields keep their existing Accessibility route.
        if (operation.equals("input")
            && com.deepseekharness.app.BuildConfig.APPLICATION_ID.equals(context.target().packageName)) {
          JSONObject lexical =
              com.deepseekharness.app.ui.WebPreviewActivity.wishcodeLexicalType(
                  args.getString("text"), context);
          if (lexical != null) return lexical;
        }
        return semanticOutcome(context, target.performAction(action, bundle), action);'''
    return change(s,old,new,"native.input")

HELPER=r'''
  private static volatile java.lang.ref.WeakReference<WebPreviewActivity> wishcodeTypingOwner =
      new java.lang.ref.WeakReference<>(null);

  private boolean wishcodeTypingCurrent() {
    return browserResumed && retained != null && retained.ready && !pageFailed
        && !conversationHidden() && webView != null && isCurrentPage(webView)
        && WebPreviewPolicy.sameService(baseUrl, webView.getUrl());
  }

  private static org.json.JSONObject wishcodeDecoded(String raw) {
    try {
      Object decoded = new org.json.JSONTokener(raw).nextValue();
      return decoded instanceof String ? new org.json.JSONObject((String)decoded) : null;
    } catch (Exception failed) { return null; }
  }

  private static org.json.JSONObject wishcodeAnswer(String code, boolean verified) {
    try {
      if (verified)
        return com.deepseekharness.app.screen.ScreenReply.completed()
            .put("code", code).put("executionMechanism", "LEXICAL_SESSION_ACTION")
            .put("effectVerified", true).put("automaticRetry", false);
      return com.deepseekharness.app.screen.ScreenReply.of(
              com.deepseekharness.app.capabilities.CapabilityResult.unknown(code, ""))
          .put("effectVerified", false).put("automaticRetry", false);
    } catch (Exception unexpected) {
      return com.deepseekharness.app.screen.ScreenReply.refused("LEXICAL_RESULT_UNAVAILABLE");
    }
  }

  /** Existing device screen grant must be claimed before calling this method. */
  public static org.json.JSONObject wishcodeLexicalType(
      String value, com.deepseekharness.app.screen.ScreenRequestContext grant) {
    WebPreviewActivity owner = wishcodeTypingOwner.get();
    if (owner == null) return null;
    if (android.os.Looper.myLooper() == android.os.Looper.getMainLooper())
      return com.deepseekharness.app.screen.ScreenReply.refused("LEXICAL_UI_THREAD");
    java.util.concurrent.CountDownLatch done = new java.util.concurrent.CountDownLatch(1);
    java.util.concurrent.atomic.AtomicReference<org.json.JSONObject> answer =
        new java.util.concurrent.atomic.AtomicReference<>();
    final class Request {
      int attempts = 0;
      void finish(org.json.JSONObject response) {
        if (done.getCount() != 0) { answer.set(response); done.countDown(); }
      }
      boolean current() {
        return done.getCount() != 0 && grant.current()
            && wishcodeTypingOwner.get() == owner
            && owner.wishcodeTypingCurrent();
      }
      void fail() { finish(wishcodeAnswer("LEXICAL_INPUT_RESULT_UNKNOWN", false)); }
      void evaluate(String js, java.util.function.Consumer<org.json.JSONObject> next) {
        if (!current()) { fail(); return; }
        try {
          owner.webView.evaluateJavascript(js, data -> {
            if (!current()) { fail(); return; }
            org.json.JSONObject obj = wishcodeDecoded(data);
            if (obj == null) { fail(); return; }
            next.accept(obj);
          });
        } catch (Exception error) { fail(); }
      }
      void poll(String id) {
        if (attempts++ > 10) { fail(); return; }
        owner.webView.postDelayed(() -> evaluate(
            "(function(){var b=window.__wishcodeLexicalInput;return JSON.stringify("
                + "b?b.status(" + org.json.JSONObject.quote(id)
                + "):{kind:'UNKNOWN'});})()", obj -> {
              String kind = obj.optString("kind");
              if ("PENDING".equals(kind)) poll(id);
              else if ("VERIFIED".equals(kind)) finish(wishcodeAnswer("LEXICAL_INPUT_VERIFIED", true));
              else fail();
            }), 120);
      }
      void begin() {
        if (!current()) { fail(); return; }
        evaluate("(function(){var b=window.__wishcodeLexicalInput;return JSON.stringify("
                + "b?b.insert(" + org.json.JSONObject.quote(value)
                + "):{kind:'NO_BRIDGE'});})()", obj -> {
              String kind = obj.optString("kind");
              if ("NO_BRIDGE".equals(kind) || "NOT_COMPOSER".equals(kind)) {
                finish(null); // No draft mutation: keep original Accessibility behavior.
              } else if ("REJECTED".equals(kind)) {
                finish(com.deepseekharness.app.screen.ScreenReply.refused("LEXICAL_INPUT_REJECTED"));
              } else if ("PENDING".equals(kind) && !obj.optString("id").isEmpty()) {
                poll(obj.optString("id"));
              } else fail();
            });
      }
    }
    Request request = new Request();
    new android.os.Handler(android.os.Looper.getMainLooper()).post(request::begin);
    long budget = Math.max(0, Math.min(
        3000L, grant.request().deadlineElapsedRealtimeMillis-grant.nowMillis()));
    try {
      if (!done.await(budget, java.util.concurrent.TimeUnit.MILLISECONDS))
        request.fail();
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      request.fail();
    }
    return done.getCount() == 0 ? answer.get()
        : wishcodeAnswer("LEXICAL_INPUT_RESULT_UNKNOWN", false);
  }
'''

def browser(s):
    s=change(s,"  private boolean browserResumed;\n",
        "  private boolean browserResumed;\n"+HELPER,"browser.fields")
    s=change(s,"  protected void onResume() {\n    super.onResume();\n    browserResumed = true;",
       "  protected void onResume() {\n    super.onResume();\n    browserResumed = true;\n"
       "    wishcodeTypingOwner = new java.lang.ref.WeakReference<>(this);","browser.resume")
    return change(s,"  protected void onPause() {\n    WebFullscreenUi.cancelIme(this);\n    browserResumed = false;",
       "  protected void onPause() {\n    WebFullscreenUi.cancelIme(this);\n    browserResumed = false;\n"
       "    if (wishcodeTypingOwner.get() == this)\n"
       "      wishcodeTypingOwner = new java.lang.ref.WeakReference<>(null);",
       "browser.pause")

CLIENT_HELPER=r'''
  function installWishcodeLexicalInput(ctx) {
    let active = true, sequence = 0;
    const pending = new Map();
    const focused = () => document.activeElement instanceof HTMLElement
      && document.activeElement.matches('[data-composer-input][contenteditable="true"]');
    const current = () => {
      const rows = Object.values(ctx.sessions.list.getSnapshot().byId || {})
        .filter(row => (row.retainedBy?.mainView ?? 0) > 0);
      if (rows.length !== 1) return null;
      const binding = ctx.sessions.binding(rows[0].id);
      if (!binding) return null;
      try { return {id:rows[0].id, shell:ctx.conversation.input.for(binding.ctx)}; }
      catch { return null; }
    };
    const bridge = {
      insert(value) {
        if (!active || document.hidden || !focused()) return {kind:'NOT_COMPOSER'};
        if (typeof value !== 'string' || !value || value.length > 2000)
          return {kind:'REJECTED'};
        const target = current();
        const shell = target?.shell;
        if (!shell?.actions?.captureInsertion || !shell?.actions?.insertText)
          return {kind:'REJECTED'};
        const before = shell.state.getSnapshot();
        if (before.phase !== 'plain') return {kind:'REJECTED'};
        const span = shell.actions.captureInsertion();
        if (span.draftRev !== before.draftRev) return {kind:'REJECTED'};
        if (!shell.actions.insertText(value, span)) return {kind:'REJECTED'};
        // One insertion, then only observe the model-owned draft revision.
        const id = String(++sequence) + '-' + Date.now().toString(36);
        const entry = {kind:'PENDING'};
        pending.set(id,entry);
        const check = pass => {
          const now = current();
          if (!active || document.hidden || !focused() || now?.id !== target.id
              || now.shell !== shell) { entry.kind='UNKNOWN'; return; }
          const after = shell.state.getSnapshot();
          if (after.draftRev !== before.draftRev && after.draft !== before.draft
              && after.draft.includes(value)) { entry.kind='VERIFIED'; return; }
          if (pass === 9) { entry.kind='UNKNOWN'; return; }
          setTimeout(() => check(pass+1), 70);
        };
        setTimeout(() => check(0),0);
        setTimeout(() => pending.delete(id),8000);
        if (pending.size > 12) pending.delete(pending.keys().next().value);
        return {kind:'PENDING',id};
      },
      status(id) {
        return {kind:active && typeof id==='string'
          ? pending.get(id)?.kind || 'UNKNOWN' : 'UNKNOWN'};
      }
    };
    if (window.__wishcodeLexicalInput !== undefined) return () => {};
    Object.defineProperty(window,'__wishcodeLexicalInput',
      {value:bridge,configurable:true,enumerable:false,writable:false});
    return () => { active=false; pending.clear();
      if (window.__wishcodeLexicalInput===bridge) delete window.__wishcodeLexicalInput; };
  }
'''

def client(s):
    return change(s,"  function apply(ctx) {\n",
        CLIENT_HELPER+"  function apply(ctx) {\n"
        "    ctx.effect(() => installWishcodeLexicalInput(ctx), 'wishcode-lexical-input');\n",
        "client.apply")

def apply(root):
    edits=[]
    for rel,fn in [(NATIVE,native),(WEB,browser),(CLIENT,client)]:
        path=root/rel
        if not path.is_file() or path.is_symlink(): raise ValueError("missing source: "+rel)
        original=path.read_text(encoding="utf-8")
        modified=fn(original)
        edits.append((path,rel,original,modified))
    for path,_,_,modified in edits: path.write_text(modified,encoding="utf-8",newline="")
    return {"patches":[{"path":rel,"before":hashlib.sha256(orig.encode()).hexdigest(),
            "after":hashlib.sha256(mod.encode()).hexdigest()} for _,rel,orig,mod in edits],
            "authorizedOnly":True,"upstreamScreenSafetyPreserved":True,"phoneVerified":False}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("--report",type=Path)
    a=p.parse_args();result=apply(a.source);data=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.report:a.report.write_text(data,encoding="utf-8")
    print(data)
