package com.deepseekharness.app.ui;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.*;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import com.deepseekharness.app.util.WishCodePreviewPolicy;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;

/** 独立数据目录的 HTML 开发预览；不安装 DSH 桥，不执行 Shell。 */
public final class WishCodePreviewActivity extends AppCompatActivity implements WebFullscreenUi.Host {
  private WebView web;
  private EditText address;
  private TextView status;
  private android.view.View openButton;
  private FrameLayout viewport;
  private volatile String approved;
  private int chatPort;
  private int widthDp;
  private volatile int generation;
  private volatile boolean failed;
  private String lastError = "尚未加载页面";

  private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }

  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    chatPort = getIntent().getIntExtra("chat_port", -1);
    LinearLayout root = new LinearLayout(this);
    root.setOrientation(LinearLayout.VERTICAL);
    root.setBackgroundColor(getColor(com.deepseekharness.app.R.color.surface));
    HorizontalScrollView actions = new HorizontalScrollView(this);
    LinearLayout row = new LinearLayout(this);
    add(row, "返回聊天", this::finish);
    add(row, "刷新", this::refresh);
    add(row, "修改地址", () -> { address.setVisibility(android.view.View.VISIBLE); openButton.setVisibility(android.view.View.VISIBLE); });
    add(row, "视口", this::chooseWidth);
    add(row, "复制链接", () -> copy(approved));
    add(row, "复制错误", () -> copy(lastError));
    add(row, "浏览器打开", this::external);
    add(row, "使用说明", this::help);
    actions.addView(row);
    root.addView(actions);
    address = new EditText(this);
    address.setHint("输入本机 URL，例如 http://127.0.0.1:4181/");
    address.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_URI);
    address.setMaxLines(3);
    WishCodePreviewEntry.font(address);
    root.addView(address, new LinearLayout.LayoutParams(-1, -2));
    openButton = WishCodePreviewEntry.button(this, "确认此本机地址并打开", this::approve);
    root.addView(openButton);
    status = new TextView(this);
    WishCodePreviewEntry.font(status);
    status.setPadding(dp(8), 0, dp(8), dp(4));
    status.setMaxLines(2);
    status.setOnClickListener(v -> new DshaDialogBuilder(this).setTitle("预览状态")
        .setMessage(status.getText()).setPositiveButton("关闭", null).show());
    status.setText("来源：用户输入；工作区归属未核实。仅加载你正在开发的服务。");
    root.addView(status);
    viewport = new FrameLayout(this);
    HorizontalScrollView pageScroll = new HorizontalScrollView(this);
    pageScroll.setFillViewport(false);
    pageScroll.addOnLayoutChangeListener((v, l, t, r, b, oldL, oldT, oldR, oldB) -> {
      if (r - l != oldR - oldL) applyWidth();
    });
    pageScroll.addView(viewport, new android.widget.FrameLayout.LayoutParams(-1, -1));
    root.addView(pageScroll, new LinearLayout.LayoutParams(-1, 0, 1));
    setContentView(root);
    WebFullscreenUi.install(this);
    if (chatPort < 1) { status.setText("缺少当前工作台端口，请返回聊天重新打开预览。"); return; }
    createWeb();
    // 恢复输入，不在重建或进程恢复时自动重新请求页面。
    String candidate = state == null ? getIntent().getStringExtra("candidate")
        : state.getString("address", "");
    address.setText(candidate);
    widthDp = state == null ? 0 : state.getInt("width", 0);
    viewport.post(this::applyWidth);
    // A human-initiated tap on a chat link is explicit approval to preview.
    // Validate with the native policy again; a manual Home entry never auto-loads.
    if (state == null && getIntent().getBooleanExtra("from_chat_link", false)
        && WishCodePreviewPolicy.normalize(candidate, chatPort) != null) {
      approve();
    }
  }

  private void add(LinearLayout row, String title, Runnable run) {
    row.addView(WishCodePreviewEntry.button(this, title, run));
  }

  @SuppressWarnings("deprecation") private void createWeb() {
    web = new WebView(this);
    WebSettings s = web.getSettings();
    s.setJavaScriptEnabled(true);
    s.setDomStorageEnabled(true);
    s.setAllowFileAccess(false);
    s.setAllowContentAccess(false);
    s.setAllowFileAccessFromFileURLs(false);
    s.setAllowUniversalAccessFromFileURLs(false);
    s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    s.setSafeBrowsingEnabled(true);
    s.setJavaScriptCanOpenWindowsAutomatically(false);
    s.setSupportMultipleWindows(true);
    s.setGeolocationEnabled(false);
    s.setCacheMode(WebSettings.LOAD_NO_CACHE);
    s.setUseWideViewPort(true);
    s.setLoadWithOverviewMode(true);
    CookieManager.getInstance().setAcceptCookie(false);
    CookieManager.getInstance().setAcceptThirdPartyCookies(web, false);
    // Service Worker 不得绕过下方逐请求的本机边界。
    ServiceWorkerController.getInstance().getServiceWorkerWebSettings().setBlockNetworkLoads(true);
    web.setWebChromeClient(new WebChromeClient() {
      @Override public void onPermissionRequest(PermissionRequest request) { request.deny(); }
      @Override public boolean onConsoleMessage(ConsoleMessage message) {
        if (message.messageLevel() == ConsoleMessage.MessageLevel.ERROR)
          error("JavaScript 错误（第 " + message.lineNumber() + " 行）", generation);
        // 不把页面日志/输入/可能的秘密写到系统日志或剪贴板。
        return true;
      }
    });
    web.setWebViewClient(new WebViewClient() {
      @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
        return navigation(request.getUrl().toString(), request.isForMainFrame() && request.hasGesture());
      }
      @Override public boolean shouldOverrideUrlLoading(WebView view, String url) { return navigation(url, false); }
      @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
        return fetch(request);
      }
      @Override public void onPageStarted(WebView view, String url, Bitmap icon) {
        if (!WishCodePreviewPolicy.sameOrigin(approved, url)) { view.stopLoading(); error("已阻止非授权页面", generation); }
      }
      @Override public void onPageFinished(WebView view, String url) {
        if (!failed && WishCodePreviewPolicy.sameOrigin(approved, url))
          status.setText("页面加载回调完成 · 端口 " + WishCodePreviewPolicy.port(approved) + " · 请实际点击验收；不代表功能通过");
      }
      @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError failure) {
        if (request.isForMainFrame()) error("WebView 加载错误 " + failure.getErrorCode() + "；检查服务是否仍在运行", generation);
      }
      @Override public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
        error("网页渲染进程退出；请返回聊天后重新打开", generation);
        viewport.removeView(view); view.destroy(); web = null; return true;
      }
    });
    viewport.addView(web, new FrameLayout.LayoutParams(-1, -1));
  }

  private boolean navigation(String url, boolean gesture) {
    if (WishCodePreviewPolicy.sameOrigin(approved, url)) return false;
    error("已阻止离开当前本机端口的导航", generation);
    if (gesture && url.startsWith("https://") && Uri.parse(url).getHost() != null)
      new DshaDialogBuilder(this).setTitle("打开外部浏览器？")
          .setMessage(Uri.parse(url).getHost())
          .setPositiveButton("打开", (d, w) -> openExternal(url)).setNegativeButton("取消", null).show();
    return true;
  }

  private void approve() {
    String candidate = WishCodePreviewPolicy.normalize(address.getText().toString(), chatPort);
    if (candidate == null) { error("地址不合格：仅支持 localhost/127.0.0.1 的 HTTP 1024–65535 端口；不含查询串或片段，不可使用工作台、3081、3090 端口", generation); return; }
    approved = candidate;
    address.setText(candidate);
    address.setVisibility(android.view.View.GONE);
    openButton.setVisibility(android.view.View.GONE);
    getSystemService(android.view.inputmethod.InputMethodManager.class)
        .hideSoftInputFromWindow(address.getWindowToken(), 0);
    refresh();
  }

  private void refresh() {
    if (approved == null || web == null) return;
    generation++;
    web.stopLoading();
    failed = false;
    lastError = "本次暂无错误记录（不代表功能已验证）";
    status.setText("正在请求端口 " + WishCodePreviewPolicy.port(approved) + "；不自动重试");
    web.loadUrl(approved);
  }

  private WebResourceResponse fetch(WebResourceRequest request) {
    final int ticket = generation;
    final String origin = approved;
    String url = request.getUrl().toString();
    if (!WishCodePreviewPolicy.sameOrigin(origin, url) || !"GET".equals(request.getMethod())) {
      error("已阻止跨端口、外部资源或非 GET 请求；请使用本地静态资源", ticket);
      return blocked();
    }
    try {
      var response = com.deepseekharness.app.util.WishCodePreviewHttp.get(origin, url, request.getMethod());
      int code = response.code;
      if (code < 200 || code >= 400) error("HTTP " + code + "；检查文件路径和服务终端日志", ticket);
      else if (request.isForMainFrame()) runOnUiThread(() -> {
        if (ticket == generation && !failed) status.setText("HTTP " + code + " · 等待渲染；请实际交互验收");
      });
      HashMap<String, String> headers = new HashMap<>();
      headers.put("Content-Security-Policy", WishCodePreviewPolicy.csp(origin));
      headers.put("Cache-Control", "no-store");
      headers.put("X-Content-Type-Options", "nosniff");
      // 不转发 Cookie、认证头、Set-Cookie、Location 或上游任意头。
      return new WebResourceResponse(response.mime, response.encoding, code, "Local preview", headers, response.body);
    } catch (Exception unavailable) {
      String detail = unavailable.getMessage();
      String reason = detail != null && detail.startsWith("PREVIEW_REDIRECT_BLOCKED_HTTP_")
          ? "HTTP " + detail.substring("PREVIEW_REDIRECT_BLOCKED_HTTP_".length()) + " 重定向已阻止，请输入最终本机地址" : unavailable.getClass().getSimpleName();
      error("无法读取端口 " + WishCodePreviewPolicy.port(origin) + "：" + reason
          + "。确认服务已启动、端口正确；进程是否退出需查看终端。", ticket);
      return blocked();
    }
  }

  private WebResourceResponse blocked() {
    return new WebResourceResponse("text/plain", "UTF-8", 403, "Blocked", java.util.Collections.emptyMap(),
        new ByteArrayInputStream("请求被预览边界阻止，请查看上方状态。".getBytes(StandardCharsets.UTF_8)));
  }

  private void error(String message, int ticket) {
    runOnUiThread(() -> {
      if (ticket != generation || isDestroyed()) return;
      failed = true; lastError = message; status.setText(message);
    });
  }

  private void chooseWidth() {
    new DshaDialogBuilder(this).setTitle("页面宽度（dp；超出屏幕时横向查看）")
        .setItems(new String[]{"适应屏幕", "360", "390", "430"}, (d, index) -> {
          widthDp = new int[]{0, 360, 390, 430}[index]; applyWidth();
        }).setNegativeButton("取消", null).show();
  }

  private void applyWidth() {
    if (web == null) return;
    // 精确 dp 容器，不伪装 UA；大于当前屏幕时由外层横向滚动查看。
    android.view.ViewGroup.LayoutParams p = viewport.getLayoutParams();
    int width = widthDp == 0 ? ((android.view.View) viewport.getParent()).getWidth() : dp(widthDp);
    if (width > 0 && p.width != width) { p.width = width; viewport.setLayoutParams(p); }
  }

  private void copy(String text) {
    if (text == null) return;
    getSystemService(ClipboardManager.class).setPrimaryClip(ClipData.newPlainText("开发预览", text));
    Toast.makeText(this, "已复制，可返回聊天粘贴", Toast.LENGTH_SHORT).show();
  }

  private void external() {
    if (approved == null) return;
    new DshaDialogBuilder(this).setTitle("用浏览器打开本机页面？")
        .setMessage("外部浏览器使用自己的 Cookie 和访问规则。")
        .setPositiveButton("打开", (d, w) -> openExternal(approved)).setNegativeButton("取消", null).show();
  }

  private void openExternal(String url) {
    try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); }
    catch (android.content.ActivityNotFoundException absent) { error("没有可用浏览器", generation); }
  }

  private void help() {
    new DshaDialogBuilder(this).setTitle("创建 → 运行 → 预览 → 修改")
        .setMessage("1. 返回聊天，让 AI 在测试工作区创建 HTML/CSS/JS，并通过已有终端启动本地服务。\n"
            + "2. 使用实际返回的端口；监听地址应为 127.0.0.1，不要向局域网开放 0.0.0.0。\n"
            + "3. 确认 URL 后打开，修改文件后点刷新。\n"
            + "4. 服务停止需在原终端按 Ctrl+C；此页不猜 PID 或停止其他进程。\n\n"
            + "本版支持静态 HTML/JS 交互及本端口 GET；不支持跨站 CDN、iframe、WebSocket、提交 POST、文件上传。"
            + "加载失败不能单独证明进程退出。旋转保持预览；进程恢复后保留地址，需再次确认加载。")
        .setPositiveButton("知道了", null).show();
  }

  @Override protected void onSaveInstanceState(Bundle state) {
    state.putString("address", address.getText().toString()); state.putInt("width", widthDp);
    super.onSaveInstanceState(state);
  }
  @Override protected void onPause() { if (web != null) web.onPause(); super.onPause(); }
  @Override protected void onResume() { super.onResume(); if (web != null) web.onResume(); }
  @Override protected void onDestroy() {
    generation++;
    if (web != null) { web.stopLoading(); viewport.removeView(web); web.destroy(); web = null; }
    super.onDestroy();
  }
}
