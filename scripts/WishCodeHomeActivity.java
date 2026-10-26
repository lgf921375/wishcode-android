package com.deepseekharness.app.ui;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import java.io.InputStream;
import java.io.OutputStream;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.AppCompatButton;

import com.deepseekharness.app.R;

/**
 * WishCode phone-first launcher. The existing DSH engine, account storage,
 * tools and permission prompts stay in their original upstream components.
 * Model credentials are managed by upstream DSH settings, not this launcher.
 */
public final class WishCodeHomeActivity extends AppCompatActivity {
  private static final String ARMOR_ARCHIVE_ASSET = "wishcode/dsh-purge-flash-v1.4.0-compat.tgz";
  private static final String ARMOR_ARCHIVE_FILE = "dsh-purge-flash-v1.4.0-wishcode-compat.tgz";

  // User-controlled export, no automatic installation or profile edits.
  private final ActivityResultLauncher<String> exportArmorArchive =
      registerForActivityResult(
          new ActivityResultContracts.CreateDocument("application/gzip"), uri -> {
            if (uri == null) return;
            try (InputStream in = getAssets().open(ARMOR_ARCHIVE_ASSET);
                 OutputStream out = getContentResolver().openOutputStream(uri, "w")) {
              if (out == null) throw new java.io.IOException("no output stream");
              byte[] buf = new byte[16384];
              int count;
              while ((count = in.read(buf)) != -1) out.write(buf, 0, count);
              out.flush();
              Toast.makeText(this, "兼容包已保存。进入插件管理 → 导入 ZIP/TAR.GZ，确认启用。",
                  Toast.LENGTH_LONG).show();
            } catch (Exception error) {
              Toast.makeText(this, "导出失败：" + error.getClass().getSimpleName(),
                  Toast.LENGTH_LONG).show();
            }
          });
  // Reviewed exact GitHub release artifact; never install the unrelated npm namesake.
  private static final String FREE_MODEL_URL =
      "https://github.com/Ebony-Vinyl/dsh-our-free-model/releases/download/v2.5.9/dsh-our-free-model-2.5.9.tgz";
  private static final String FREE_MODEL_SHA =
      "3c98427d8144041568c12dd5c61c42632d022856e8f5327e66b813fe80d269a2";

  // Optional read-only GitHub search tools; official GitHub Release archive checksum.
  // The current Harness 0.2.1-rc.2 compatibility is not yet verified.
  private static final String GITHUB_PLUGIN_URL =
      "https://github.com/moxingovo/dsh-github/releases/download/v0.1.6/dsh-plugin-github-0.1.6.tgz";
  private static final String GITHUB_PLUGIN_SHA =
      "cb76ddc1fd02d71dea02bfede0ecc9137877ef1b5c31ac8ca011fe9b1dcf5db3";

  private int dp(int size) {
    return Math.round(size * getResources().getDisplayMetrics().density);
  }

  private TextView text(String value, int sp, int color, boolean bold) {
    TextView label = new TextView(this);
    label.setText(value);
    label.setTextSize(sp);
    label.setTextColor(getColor(color));
    // Keep the user-selected ColorOS font, including its pinyin glyphs.
    if (bold) label.setTypeface(label.getTypeface(), Typeface.BOLD);
    label.setIncludeFontPadding(true);
    label.setFallbackLineSpacing(true);
    label.setLineSpacing(dp(7), 1.12f);
    label.setBreakStrategy(android.text.Layout.BREAK_STRATEGY_HIGH_QUALITY);
    label.setGravity(Gravity.START);
    return label;
  }

  private void addText(LinearLayout parent, TextView label, int top, int bottom) {
    LinearLayout.LayoutParams p =
        new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT);
    p.topMargin = dp(top);
    p.bottomMargin = dp(bottom);
    parent.addView(label, p);
  }

  private void action(LinearLayout parent, String title, boolean primary, Runnable run) {
    AppCompatButton button = new AppCompatButton(this);
    button.setText(title);
    button.setTextSize(16);
    button.setAllCaps(false);
    button.setGravity(Gravity.CENTER);
    // WRAP_CONTENT plus comfortable vertical font metrics: never fix button height.
    button.setMinHeight(dp(64));
    button.setIncludeFontPadding(true);
    button.setFallbackLineSpacing(true);
    button.setSingleLine(false);
    button.setMaxLines(4);
    button.setLineSpacing(dp(7), 1.12f);
    button.setPadding(dp(12), dp(14), dp(12), dp(14));
    button.setBackgroundResource(
        primary ? R.drawable.bg_btn_primary : R.drawable.bg_action_plain);
    button.setTextColor(getColorStateList(
        primary ? R.color.button_primary_text : R.color.primary));
    button.setOnClickListener(v -> run.run());
    LinearLayout.LayoutParams p =
        new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT);
    p.topMargin = dp(12);
    parent.addView(button, p);
  }

  @Override
  protected void onCreate(@Nullable Bundle state) {
    super.onCreate(state);
    // Android launcher opens chat by default. Home remains available explicitly
    // by tapping the main workbench title, rather than becoming a mandatory page.
    if (Intent.ACTION_MAIN.equals(getIntent().getAction())
        && getIntent().hasCategory(Intent.CATEGORY_LAUNCHER)
        && !getIntent().getBooleanExtra("wishcode_show_home", false)) {
      // A live browser task already has the user's conversation and scroll
      // state. Return that exact task before creating a second Web host.
      if (BrowserTasks.resumeBackground(this, true)) {
        finish();
        return;
      }
      startActivity(new Intent(this, MainActivity.class)
          .putExtra("open_web", true)
          .putExtra("wishcode_auto_start_web", true));
      finish();
      return;
    }
    ScrollView scroll = new ScrollView(this);
    scroll.setFillViewport(true);
    scroll.setClipToPadding(false);
    scroll.setVerticalScrollBarEnabled(true);

    LinearLayout content = new LinearLayout(this);
    content.setOrientation(LinearLayout.VERTICAL);
    content.setPadding(dp(18), dp(20), dp(18), dp(26));
    content.setBackgroundColor(getColor(R.color.surface));
    scroll.addView(content);
    setContentView(scroll);

    addText(content, text("许愿编程 · V0.5 测试版004", 26, R.color.text, true), 0, 3);
    addText(content, text("像聊天一样编程 · 工具调用仍由 DSH 执行", 13,
        R.color.text_secondary, false), 0, 18);

    action(content, "开始聊天编程", true, this::openWeb);
    addText(content, text("先选择一个测试工作区，再让模型读写文件。执行命令、插件安装和重要权限仍需确认。",
        13, R.color.text_secondary, false), 9, 18);

    addText(content, text("模型", 19, R.color.text, true), 0, 0);
    action(content, "选择模型 · 官方 DeepSeek / 免费模型", false, this::showModelChoice);
    addText(content, text("其他模型请进入工作台，在「设置 → 模型」中按 DSH 支持的渠道自行配置。",
        13, R.color.text_secondary, false), 10, 0);

    addText(content, text("工具", 19, R.color.text, true), 22, 0);
    action(content, "项目文件", false,
        () -> startActivity(new Intent(this, WorkspaceFilesActivity.class)));
    action(content, "GitHub 搜索与源码研究", false, this::showGitHubHelp);
    action(content, "Flash 破甲插件 · 修复包（手动导入）", false, this::showArmorCompat);
    action(content, "插件管理", false, this::openPlugins);
    action(content, "终端命令", false, this::openTerminal);

    addText(content, text("安全与帮助", 19, R.color.text, true), 22, 0);
    action(content, "权限说明", false, this::showPermissions);
    action(content, "诊断与日志", false,
        () -> startActivity(new Intent(this, DiagnosticActivity.class)));

    String abi = Build.SUPPORTED_ABIS.length > 0 ? Build.SUPPORTED_ABIS[0] : "未知";
    addText(content, text("Android " + Build.VERSION.RELEASE + " · " + abi
        + "\nLinux/Harness 在手机本地运行；AI 模型通过互联网调用。",
        12, R.color.text_muted, false), 22, 0);
  }

  private void openWeb() {
    Intent intent = new Intent(this, MainActivity.class);
    // Upstream consumes open_web and waits for a ready, authenticated local Web.
    intent.putExtra("open_web", true);
    startActivity(intent);
  }

  private void openPlugins() {
    Intent intent = new Intent(this, MainActivity.class);
    intent.putExtra("open_plugins", true);
    startActivity(intent);
  }

  private void openTerminal() {
    Intent intent = new Intent(this, MainActivity.class);
    intent.putExtra("open_terminal", true);
    startActivity(intent);
  }

  private void showModelChoice() {
    new AlertDialog.Builder(this)
        .setTitle("选择模型接入方式")
        .setItems(new String[]{
            "DeepSeek 官方 API Key（按量计费）",
            "免费模型插件（有额度及隐私限制）"
        }, (dialog, selected) -> {
          if (selected == 0) showModelHelp();
          else showFreeModelNotice();
        })
        .setNegativeButton("取消", null).show();
  }

  private void showModelHelp() {
    new AlertDialog.Builder(this)
        .setTitle("连接 DeepSeek Flash")
        .setMessage("你已经有的 DeepSeek API Key 无需发送给任何人。\n\n"
            + "1. 点击开始聊天编程，进入本地 Web 工作台。\n"
            + "2. 在设置 → 模型 → DeepSeek 粘贴 API Key。\n"
            + "3. 保存并选择 deepseek-flash。\n\n"
            + "模型通过网络 API 工作，Token 按官方规则计费。")
        .setPositiveButton("进入工作台", (dialog, which) -> openWeb())
        .setNeutralButton("开放平台", (dialog, which) ->
            openExternal("https://platform.deepseek.com/"))
        .setNegativeButton("返回", null).show();
  }

  private void showFreeModelNotice() {
    new AlertDialog.Builder(this)
        .setTitle("免费模型不是无限免费")
        .setMessage("免费模型通过网络调用，不是下载到手机。\n\n"
            + "Kilo 网关提供无需 API Key 的免费模型，但匿名请求按 IP 限流（官方文档为每小时最多 200 次），并可能存在地区限制。\n\n"
            + "OpenCode 的部分模型为限时免费，且官方对第三方客户端的免费访问有限制，不能保证一直可用。\n\n"
            + "这个插件来自独立开源作者，包含额外的账号渠道、公告、升级与网关功能，尚未完成全面安全审计。"
            + "部分免费服务商可能记录输入或用于改进模型。\n\n"
            + "只在不含隐私及密钥的测试工作区使用。安装前查看来源和权限；不要从 npm 安装同名包。")
        .setPositiveButton("检查安装包", (dialog, which) -> openPinnedPluginInstaller())
        .setNeutralButton("查看 GitHub 源码", (dialog, which) ->
            openExternal("https://github.com/Ebony-Vinyl/dsh-our-free-model"))
        .setNegativeButton("取消", null).show();
  }

  private void openPinnedPluginInstaller() {
    Uri uri = new Uri.Builder()
        .scheme("dsha")
        .authority("install")
        .appendQueryParameter("url", FREE_MODEL_URL)
        .appendQueryParameter("sha256", FREE_MODEL_SHA)
        .appendQueryParameter("name", "dsh-our-free-model")
        .appendQueryParameter("version", "2.5.9")
        .build();
    // PluginInstallActivity performs its own inspection and explicit confirmation.
    startActivity(new Intent(this, PluginInstallActivity.class).setData(uri));
  }

  private void showGitHubHelp() {
    new AlertDialog.Builder(this)
        .setTitle("GitHub 源码研究")
        .setMessage("手机的 Ubuntu 已包含 git。可以在已授权的测试工作区克隆公开仓库，"
            + "再让 Harness 阅读 README、代码和测试。克隆不需要单独的 GitHub 插件。\n\n"
            + "可选 dsh-plugin-github 为 Agent 增加 github_search 与 github_get 工具，"
            + "用来搜索仓库、Issue/PR、读取单个文件；它不提供克隆、推送或写入操作。"
            + "公开检索默认可匿名使用，但有限流。\n\n"
            + "插件是第三方只读扩展，尚未在本机 DSH 0.2.1-rc.2 上验证兼容性。"
            + "检查来源和安装预览后再决定，勿提供具有写权限的 GitHub Token。")
        .setPositiveButton("检查 GitHub 插件", (dialog, which) -> openGithubPluginInstaller())
        .setNeutralButton("打开终端（Git 克隆）", (dialog, which) -> openTerminal())
        .setNegativeButton("取消", null)
        .show();
  }

  private void openGithubPluginInstaller() {
    Uri uri = new Uri.Builder()
        .scheme("dsha")
        .authority("install")
        .appendQueryParameter("url", GITHUB_PLUGIN_URL)
        .appendQueryParameter("sha256", GITHUB_PLUGIN_SHA)
        .appendQueryParameter("name", "dsh-plugin-github")
        .appendQueryParameter("version", "0.1.6")
        .build();
    startActivity(new Intent(this, PluginInstallActivity.class).setData(uri));
  }

  private void showArmorCompat() {
    new AlertDialog.Builder(this)
        .setTitle("dsh-purge-flash 1.4.0 兼容包")
        .setMessage("来源固定：jadezane6634-ops/dsh-purge-flash，提交 "
            + "636059f8002b060fb4dca1c1b47c02e1ef2a2f31。\n\n"
            + "只修正 armor-playbook 技能注册缺少字符串 source 字段的问题；"
            + "不改 DSH 宿主、不改其他第三方插件。\n\n"
            + "插件会修改提示词及请求处理，并可能记录原始会话内容。"
            + "建议先备份工作区，仅在测试会话使用。"
            + "此修复尚未通过安卓实机验证，也不会自动安装或启用。\n\n"
            + "点击「导出兼容包」保存到手机下载目录，随后打开「插件管理」"
            + "选择「导入 ZIP/TAR.GZ」，检查名称和版本再确认安装。"
            + "安装后务必使用真正的 /armor status 命令验证模块状态。")
        .setPositiveButton("导出兼容包", (dialog, which) ->
            exportArmorArchive.launch(ARMOR_ARCHIVE_FILE))
        .setNeutralButton("插件管理", (dialog, which) -> openPlugins())
        .setNegativeButton("取消", null)
        .show();
  }

  private void showPermissions() {
    new AlertDialog.Builder(this)
        .setTitle("文件权限与执行确认")
        .setMessage("默认使用 workspace-write：模型只应写入已授权的工作区。\n\n"
            + "如果出现 DEFAULT_WRITE_NOT_FULL，请先检查工作区及本次会话权限。"
            + "不要为了消除提示直接授予无限制磁盘写入。\n\n"
            + "Shell 命令和第三方插件可能修改、删除文件；确认命令和修改范围后再允许。")
        .setPositiveButton("进入工作台", (dialog, which) -> openWeb())
        .setNegativeButton("关闭", null).show();
  }

  private void openExternal(String url) {
    try {
      startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
    } catch (ActivityNotFoundException missing) {
      Toast.makeText(this, "没有可用浏览器，请复制官网地址到浏览器",
          Toast.LENGTH_LONG).show();
    }
  }
}
