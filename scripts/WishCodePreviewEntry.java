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
    // 只传当前工作台端口，不传 auth URL、Cookie、令牌或工作区文件。
    var identity = com.deepseekharness.app.core.HarnessController.get(host).getReadyWebPageIdentity();
    int chatPort = identity == null ? -1 : WishCodePreviewPolicy.port(identity.authUrl());
    if (chatPort < 1) {
      new DshaDialogBuilder(host).setTitle("请先进入聊天工作台")
          .setMessage("需要核对当前工作台端口，防止把聊天服务当成开发网页。")
          .setPositiveButton("知道了", null).show();
      return;
    }
    host.startActivity(new Intent(host, WishCodePreviewActivity.class)
        .putExtra("chat_port", chatPort).putExtra("candidate", candidate));
  }

}
