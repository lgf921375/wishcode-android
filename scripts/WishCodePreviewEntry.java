package com.deepseekharness.app.ui;

import android.app.Activity;
import android.content.Intent;
import android.widget.TextView;
import androidx.appcompat.widget.AppCompatButton;
import com.deepseekharness.app.util.WishCodePreviewPolicy;

/** 原生入口不读取聊天 DOM、不接收网页桥消息。 */
public final class WishCodePreviewEntry {
  private WishCodePreviewEntry() {}

  public static void font(TextView view) {
    view.setIncludeFontPadding(true);
    view.setFallbackLineSpacing(true);
    view.setLineSpacing(6 * view.getResources().getDisplayMetrics().density, 1.12f);
  }

  public static AppCompatButton button(Activity host, String title, Runnable action) {
    AppCompatButton b = new AppCompatButton(host);
    b.setText(title);
    b.setAllCaps(false);
    b.setSingleLine(false);
    font(b);
    b.setMinHeight(Math.round(56 * host.getResources().getDisplayMetrics().density));
    b.setOnClickListener(v -> action.run());
    return b;
  }

  public static void open(Activity host, String candidate) {
    // Retired at user's request: never open the limited isolated WebView.
    // Keep the symbol so legacy callers cannot accidentally open it.
    new DshaDialogBuilder(host).setTitle("旧网页预览已停用")
        .setMessage("该预览器不兼容部分游戏和跨站网页。请返回聊天，使用常规浏览器或项目工具进行测试。")
        .setPositiveButton("知道了", null).show();
  }

}
