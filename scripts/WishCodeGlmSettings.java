package com.deepseekharness.app.ui;

import android.app.Activity;
import android.text.InputType;
import android.util.AtomicFile;
import android.view.View;
import android.view.WindowManager;
import android.widget.*;
import androidx.appcompat.app.AlertDialog;
import com.deepseekharness.app.util.GuestPaths;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;

/** Native-only credential editor. No keys pass through the chat WebView. */
public final class WishCodeGlmSettings {
  private WishCodeGlmSettings() {}
  public static void show(Activity activity) {
    File directory = new File(GuestPaths.rootfs(activity.getFilesDir()), "root/.dsh");
    if (!directory.isDirectory()) {
      Toast.makeText(activity, "请先完成运行环境初始化，再配置 GLM。", Toast.LENGTH_LONG).show();
      return;
    }
    LinearLayout form = new LinearLayout(activity);
    form.setOrientation(LinearLayout.VERTICAL);
    int pad = (int)(20 * activity.getResources().getDisplayMetrics().density);
    form.setPadding(pad,pad,pad,pad);
    TextView help = new TextView(activity);
    help.setText("分别保存普通 API 或 Coding Plan 密钥。聊天模型菜单中选择对应渠道，不会自动切换计费渠道。\nGLM-5.3 仅支持文本，思考强度可选 low / high / max。密钥保存在本应用私有运行环境中，请勿发送到聊天。\n留空保留现有密钥；长按输入框可粘贴。");
    help.setIncludeFontPadding(true); help.setFallbackLineSpacing(true); help.setLineSpacing(8,1.15f);
    form.addView(help);
    Spinner channel = new Spinner(activity);
    channel.setAdapter(new ArrayAdapter<String>(activity,android.R.layout.simple_spinner_dropdown_item,
        new String[]{"普通 API · 按量计费","Coding Plan · 套餐额度"}));
    form.addView(channel);
    EditText key = new EditText(activity);
    key.setHint("输入所选渠道的 API Key");
    key.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
    key.setSingleLine(true); key.setSaveEnabled(false);
    key.setImportantForAutofill(View.IMPORTANT_FOR_AUTOFILL_NO);
    form.addView(key);
    CheckBox clear = new CheckBox(activity); clear.setText("删除所选渠道已保存的密钥"); form.addView(clear);
    TextView state = new TextView(activity); form.addView(state);
    channel.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
      public void onNothingSelected(AdapterView<?> parent) {}
      public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
        key.setText(""); clear.setChecked(false);
        try { state.setText(read(directory).optString(position == 0 ? "api" : "plan", "").isEmpty() ? "该渠道尚未配置" : "该渠道已保存密钥（不回显）"); }
        catch (Exception e) { state.setText("配置读取失败，未修改。请检查运行环境。"); }
      }
    });
    ScrollView scroll = new ScrollView(activity); scroll.addView(form);
    AlertDialog dialog = new AlertDialog.Builder(activity).setTitle("GLM-5.3 渠道设置")
        .setView(scroll).setNegativeButton("取消",null).setPositiveButton("保存",null).create();
    dialog.setOnShowListener(v -> {
      dialog.getWindow().addFlags(WindowManager.LayoutParams.FLAG_SECURE);
      dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(button -> {
        String value = key.getText().toString().trim();
        if (value.matches(".*\\s.*")) { key.setError("密钥不能包含空白字符"); return; }
        try {
          JSONObject config = read(directory);
          String selected = channel.getSelectedItemPosition() == 0 ? "api" : "plan";
          if (clear.isChecked()) config.remove(selected);
          else if (!value.isEmpty()) config.put(selected,value);
          write(directory,config);
          key.setText(""); dialog.dismiss();
          Toast.makeText(activity,"已保存。返回聊天，在模型菜单选择对应 GLM-5.3 渠道。",Toast.LENGTH_LONG).show();
        } catch (Exception e) { state.setText("保存失败，未确认写入。请检查运行环境；密钥不会写入日志。"); }
      });
    });
    dialog.setOnDismissListener(v -> key.setText("")); dialog.show();
  }
  private static File file(File directory) throws IOException {
    File target = new File(directory,"wishcode-glm.json");
    if (!target.getCanonicalPath().equals(new File(directory.getCanonicalFile(),"wishcode-glm.json").getPath()))
      throw new IOException("GLM_CONFIG_PATH");
    return target;
  }
  private static JSONObject read(File directory) throws Exception {
    AtomicFile target = new AtomicFile(file(directory));
    if (!target.getBaseFile().exists()) return new JSONObject();
    return new JSONObject(new String(target.readFully(),StandardCharsets.UTF_8));
  }
  private static void write(File directory, JSONObject config) throws Exception {
    AtomicFile target = new AtomicFile(file(directory));
    FileOutputStream stream = null;
    try {
      stream = target.startWrite();
      android.system.Os.fchmod(stream.getFD(),0600);
      stream.write(config.toString().getBytes(StandardCharsets.UTF_8));
      target.finishWrite(stream);
    } catch (Exception e) { if (stream != null) target.failWrite(stream); throw e; }
  }
}
