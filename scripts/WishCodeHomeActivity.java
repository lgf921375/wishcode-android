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

    ui.primary("① 连接 DeepSeek Flash", this::showModelHelp);
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
