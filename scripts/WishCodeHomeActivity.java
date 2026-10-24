package com.deepseekharness.app.ui;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

/**
 * First-run, Chinese mobile launcher and guidance.
 * Never handles API keys; they remain in upstream DSH provider settings.
 * Never installs any third-party plugin without user approval.
 */
public final class WishCodeHomeActivity extends AppCompatActivity {
  @Override
  protected void onCreate(@Nullable Bundle state) {
    super.onCreate(state);
    String abi = Build.SUPPORTED_ABIS.length > 0 ? Build.SUPPORTED_ABIS[0] : "未知";
    OnboardingUi ui = new OnboardingUi(
        this,
        "本机模式 · 首次配置",
        "许愿编程",
        "不必下载 AI 模型。先配置 DeepSeek Flash，再选择工作区开始编程。常用插件已经内置。");

    ui.row("设备", "Android " + Build.VERSION.RELEASE + " · " + abi);
    ui.note("Linux 和 Harness 在手机本地运行；模型通过 DeepSeek API 在线推理。"
        + "不要把 API Key 发送到聊天，也不要导入来源不明的插件。");

    ui.primary("① 选择模型（DeepSeek / 免费）", this::showModelChoice);
    ui.secondary("② 开始编程 / 选择工作区", this::openLaunch);
    ui.secondary("③ 插件中心 / 已安装插件", this::showPluginHelp);
    ui.secondary("故障诊断 / 导出日志", () ->
        startActivity(new Intent(this, DiagnosticActivity.class)));
  }

  private void openLaunch() {
    Intent i = new Intent(this, MainActivity.class);
    i.putExtra("open_launch", true);
    startActivity(i);
  }

  private void openPlugins() {
    Intent i = new Intent(this, MainActivity.class);
    i.putExtra("open_plugins", true);
    startActivity(i);
  }

  // Fixed, explicitly reviewed GitHub Release asset. Never use the npm namesake.
  private static final String FREE_MODEL_URL =
      "https://github.com/Ebony-Vinyl/dsh-our-free-model/releases/download/v2.5.9/dsh-our-free-model-2.5.9.tgz";
  private static final String FREE_MODEL_SHA =
      "3c98427d8144041568c12dd5c61c42632d022856e8f5327e66b813fe80d269a2";

  private void showModelChoice() {
    new AlertDialog.Builder(this)
        .setTitle("选择模型接入方式")
        .setItems(
            new String[] {"DeepSeek 官方 API Key（按量付费）",
                "免费模型插件（可选；有额度和隐私限制）"},
            (dialog, which) -> {
              if (which == 0) showModelHelp();
              else showFreeModelNotice();
            })
        .setNegativeButton("取消", null)
        .show();
  }

  private void showFreeModelNotice() {
    new AlertDialog.Builder(this)
        .setTitle("免费模型 · 安装前确认")
        .setMessage("模型通过第三方网关在线运行，不是下载到手机。\\n\\n"
            + "Kilo 官方提供无 Key 匿名免费模型，但按 IP 限速，每小时最多 200 次，"
            + "免费模型会变化，部分提供商可能记录和利用输入内容。\\n\\n"
            + "这个开源插件提供 Kilo 和 OpenCode 接入；开发者不是模型服务商。"
            + "OpenCode 部分免费模型限时且可能限制第三方客户端。"
            + "插件还包含可选账号渠道、公告、升级与本地代理，尚未经过全面安全审计。\\n\\n"
            + "只用于公开测试项目。不要发送私人源码、密钥、账号资料。"
            + "安装前会进入上游插件确认页面；若校验失败，不要绕过。"
            + "切勿从 npm 安装同名包。")
        .setPositiveButton("查看插件并确认安装", (dialog, which) -> openPinnedPluginInstaller())
        .setNeutralButton("查看开源项目", (dialog, which) ->
            openExternal("https://github.com/Ebony-Vinyl/dsh-our-free-model"))
        .setNegativeButton("取消", null)
        .show();
  }

  private void openPinnedPluginInstaller() {
    Uri link = new Uri.Builder()
        .scheme("dsha")
        .authority("install")
        .appendQueryParameter("url", FREE_MODEL_URL)
        .appendQueryParameter("sha256", FREE_MODEL_SHA)
        .appendQueryParameter("name", "dsh-our-free-model")
        .appendQueryParameter("version", "2.5.9")
        .build();
    startActivity(new Intent(this, PluginInstallActivity.class).setData(link));
  }

  private void showModelHelp() {
    new AlertDialog.Builder(this)
        .setTitle("DeepSeek Flash：只需要配置，不用安装")
        .setMessage("1. 你已有的 DeepSeek API Key 可以直接使用，无需发送给任何人。\n\n"
            + "2. 点击【开始编程】，等本地环境就绪，进入 Web 界面。\n\n"
            + "3. 在 Web 界面打开【设置 → 模型 → DeepSeek】，粘贴 API Key 并保存。\n\n"
            + "4. 在对话模型选择器中选择 deepseek-flash。\n\n"
            + "API 请求会产生使用费用。此向导不读取、保存或上传密钥。")
        .setPositiveButton("进入编程界面", (dialog, which) -> openLaunch())
        .setNeutralButton("DeepSeek 开放平台", (dialog, which) ->
            openExternal("https://platform.deepseek.com/"))
        .setNegativeButton("关闭", null)
        .show();
  }

  private void showPluginHelp() {
    new AlertDialog.Builder(this)
        .setTitle("先使用内置插件，不用安装")
        .setMessage("系统已经内置手机 Web 界面、任务通知和设备能力引导等插件。\n\n"
            + "1. 点击【打开插件中心】，查看已安装状态与开关。\n\n"
            + "2. 先完成模型配置和工作区测试。此时无需额外插件，也能读写代码和执行终端任务。\n\n"
            + "3. 只有明确需要第三方功能时，才从可信来源导入仓库链接或 ZIP/TAR.GZ。\n\n"
            + "第三方插件可能执行安装脚本和访问应用可访问的数据。")
        .setPositiveButton("打开插件中心", (dialog, which) -> openPlugins())
        .setNegativeButton("关闭", null)
        .show();
  }

  private void openExternal(String url) {
    try {
      startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
    } catch (ActivityNotFoundException missing) {
      Toast.makeText(this, "浏览器未找到，请手动访问 platform.deepseek.com",
          Toast.LENGTH_LONG).show();
    }
  }
}
