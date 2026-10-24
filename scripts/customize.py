#!/usr/bin/env python3
"""Fail-closed adaptation for SHA-verified DSHA 0.2.1-rc.2 sources.

Preserves upstream runtime, security confirmations, extraction and shutdown.
This module does not prove APK or real-device functionality.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

BASE = "DSH-APP/DSHA@c750348a4d4b18edcb165a93b4ca66403b040b4c"
APP_ID = "app.wishcode.harnessmobile.v05preview"
HOME_PATH = "app/src/main/java/com/deepseekharness/app/ui/WishCodeHomeActivity.java"
MOBILE_PATH = "app/src/main/assets/web-integration/wishcode-mobile.js"
MAIN_MANIFEST = '''        <activity
            android:name=".ui.MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>'''
NEW_MANIFEST = '''        <activity android:name=".ui.WishCodePreviewActivity"
            android:exported="false" android:process=":wishcode_preview"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:windowSoftInputMode="adjustResize" />
        <activity
            android:name=".ui.MainActivity"
            android:exported="false"
            android:windowSoftInputMode="adjustResize" />
        <!-- Independent launcher; all runtime controls remain upstream. -->
        <activity android:name=".ui.WishCodeHomeActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>'''

EXPECTED = {
    "app/src/main/java/com/deepseekharness/app/DshaApp.java": [
        ('    super.onCreate();',
         '    super.onCreate();\n'
         '    if (android.app.Application.getProcessName().endsWith(":wishcode_preview")) {\n'
         '      android.webkit.WebView.setDataDirectorySuffix("wishcode_developer_preview");\n'
         '      return; // 不初始化工作台、桥、备份或运行时服务。\n'
         '    }'),
    ],
    "app/src/main/java/com/deepseekharness/app/ui/WebPreviewActivity.java": [
        ('      if (request.hasGesture()\n',
         '      if (request.hasGesture() && com.deepseekharness.app.util.WishCodePreviewPolicy.normalize(url,\n'
         '          com.deepseekharness.app.util.WishCodePreviewPolicy.port(baseUrl)) != null) {\n'
         '        WishCodePreviewEntry.open(WebPreviewActivity.this, url); return true;\n'
         '      }\n      if (request.hasGesture()\n'),
    ],
    "app/build.gradle": [
        ('applicationId "dsh.android.client"', f'applicationId "{APP_ID}"'),
        ('versionCode 190', 'versionCode 191'),
        ('versionName "0.2.1-rc.2-20261022.2100-dsh0.2.1-rc.2"',
         'versionName "0.5-preview-001-dsh0.2.1-rc.2"'),
    ],
    "app/src/main/res/values/strings.xml": [
        ('<string name="app_name" translatable="false">DSHA</string>',
         '<string name="app_name" translatable="false">许愿编程</string>'),
    ],
    "app/src/main/AndroidManifest.xml": [(MAIN_MANIFEST, NEW_MANIFEST)],
    "app/src/main/java/com/deepseekharness/app/core/ConfigStore.java": [
        ('return flag(Constants.KEY_CHECK_UPDATE, true);',
         'return flag(Constants.KEY_CHECK_UPDATE, false);'),
        ('text(Constants.KEY_PERMISSION_MODE, "danger-full-access")',
         'text(Constants.KEY_PERMISSION_MODE, "workspace-write")'),
    ],
    "app/src/main/java/com/deepseekharness/app/ui/MainActivity.java": [
        ('startActivity(new Intent(this, WelcomeActivity.class));',
         'startActivity(new Intent(this, OnboardingPrepareActivity.class));'),
        ('  private boolean pendingOpenWeb;',
         '  private boolean pendingOpenWeb;\n'
         '  private boolean pendingWishcodeAutoStart;'),
        ('    TextView title = findViewById(R.id.app_title);\n'
         '    renderThemeButton();',
         '    TextView title = findViewById(R.id.app_title);\n'
         '    title.setOnClickListener(v -> startActivity(new Intent(this, '
         'WishCodeHomeActivity.class).putExtra("wishcode_show_home", true)));\n'
         '    renderThemeButton();'),
        ('              args.putBoolean(LaunchFragment.ARG_OPEN_WEB, true);\n'
         '              f.setArguments(args);',
         '              args.putBoolean(LaunchFragment.ARG_OPEN_WEB, true);\n'
         '              args.putBoolean("wishcode_auto_start_web", pendingWishcodeAutoStart);\n'
         '              pendingWishcodeAutoStart = false;\n'
         '              f.setArguments(args);'),
        ('    intent.removeExtra("open_web");\n'
         '    BottomNavigationView nav = findViewById(R.id.bottom_nav);',
         '    intent.removeExtra("open_web");\n'
         '    pendingWishcodeAutoStart = intent.getBooleanExtra("wishcode_auto_start_web", false);\n'
         '    intent.removeExtra("wishcode_auto_start_web");\n'
         '    BottomNavigationView nav = findViewById(R.id.bottom_nav);'),
        ('      ((LaunchFragment) shown).requestAutoEnterWeb();',
         '      ((LaunchFragment) shown).requestAutoEnterWeb(pendingWishcodeAutoStart);\n'
         '      pendingWishcodeAutoStart = false;'),
        ('"是否需要恢复以前的备份？", "Restore an older backup?"',
         '"恢复旧备份？", "Restore backup?"'),
        ('"当前环境没有用户数据。系统暂时无法枚举卸载前的 Download/DSHA 文件；可用文件选择器直接选择备份，不需要开启所有文件访问。",',
         '"当前安装没有用户数据。若曾导出旧备份，点「手动选择」；没有则点「不用了」继续。无需开启所有文件访问。",'),
    ],
    "app/src/main/java/com/deepseekharness/app/ui/OnboardingUi.java": [
        ('TextView brand = text("DSHA", 18, R.color.text);',
         'TextView brand = text("许愿编程", 18, R.color.text);'),
        ('brand.setTypeface(null, android.graphics.Typeface.BOLD);',
         'brand.setTypeface(brand.getTypeface(), android.graphics.Typeface.BOLD);'),
        ('heading.setTypeface(null, android.graphics.Typeface.BOLD);',
         'heading.setTypeface(heading.getTypeface(), android.graphics.Typeface.BOLD);'),
        ('t.setIncludeFontPadding(false);',
         't.setIncludeFontPadding(true);\n    t.setFallbackLineSpacing(true);\n'
         '    t.setLineSpacing(dp(6), 1.12f);'),
        ('b.setMinHeight(dp(48));',
         'b.setMinHeight(dp(64));\n    b.setIncludeFontPadding(true);\n'
         '    b.setFallbackLineSpacing(true);\n    b.setSingleLine(false);\n'
         '    b.setMaxLines(4);\n    b.setLineSpacing(dp(6), 1.12f);'),
    ],
    "app/src/main/java/com/deepseekharness/app/ui/WebPageScripts.java": [
        ('''        + read(context, "web-integration/page.js")
        + "\\nwindow.__dshaNativePresentation.install("''',
         '''        + read(context, "web-integration/page.js")
        + "\\n"
        + read(context, "web-integration/wishcode-mobile.js")
        + "\\nwindow.__dshaNativePresentation.install("'''),
    ],
    "app/src/main/java/com/deepseekharness/app/ui/LaunchFragment.java": [
        ('  private boolean pendingAutoEnter;',
         '  private boolean pendingAutoEnter;\n'
         '  private boolean pendingWishcodeStart;'),
        ('          if (pendingAutoEnter && !webEntryUrl().isEmpty()) {\n'
         '            pendingAutoEnter = false;\n'
         '            enterWeb();\n'
         '          }',
         '          if (pendingAutoEnter && !webEntryUrl().isEmpty()) {\n'
         '            pendingAutoEnter = false;\n'
         '            pendingWishcodeStart = false;\n'
         '            enterWeb();\n'
         '          } else if (pendingAutoEnter && pendingWishcodeStart\n'
         '              && getView() != null && isResumed()\n'
         '              && !controller.isStarting() && !controller.isStopping()\n'
         '              && !controller.isRestoringWebSession()\n'
         '              && !controller.hasUnresolvedWebSession()\n'
         '              && !controller.isUserStopped()\n'
         '              && !com.deepseekharness.app.core.EnvironmentAccess.needsRecovery(controller)\n'
         '              && !controller.config().isStartupRecoveryRequested()) {\n'
         '            // Exactly one user-initiated launcher start; never auto-retry after failure.\n'
         '            pendingWishcodeStart = false;\n'
         '            doStart(requireActivity(),\n'
         '                getView().findViewById(R.id.launch_status),\n'
         '                getView().findViewById(R.id.launch_start));\n'
         '          }'),
        ('      getArguments().remove(ARG_OPEN_WEB);\n'
         '      pendingAutoEnter = true;',
         '      getArguments().remove(ARG_OPEN_WEB);\n'
         '      pendingWishcodeStart = getArguments().getBoolean("wishcode_auto_start_web", false);\n'
         '      getArguments().remove("wishcode_auto_start_web");\n'
         '      pendingAutoEnter = true;'),
        ('  void requestAutoEnterWeb() {\n'
         '    pendingAutoEnter = true;',
         '  void requestAutoEnterWeb() { requestAutoEnterWeb(false); }\n'
         '  void requestAutoEnterWeb(boolean autoStart) {\n'
         '    pendingWishcodeStart = autoStart;\n'
         '    pendingAutoEnter = true;'),
        ('          startRequest.incrementAndGet();\n'
         '          preparingStart = false;\n'
         '          FirstRunWebStart.cancel(requireContext());',
         '          startRequest.incrementAndGet();\n'
         '          pendingAutoEnter = false;\n'
         '          pendingWishcodeStart = false;\n'
         '          preparingStart = false;\n'
         '          FirstRunWebStart.cancel(requireContext());'),
        ('    // 页面不可见时撤销自动进入：用户离开了启动页，回来不该被"突袭"打开 Web。\n'
         '    pendingAutoEnter = false;',
         '    // 页面不可见时撤销自动进入：用户离开了启动页，回来不该被"突袭"打开 Web。\n'
         '    pendingAutoEnter = false;\n'
         '    pendingWishcodeStart = false;'),
        ('''    start.setOnClickListener(
        x -> {
          if (webReady || !webEntryUrl().isEmpty()) {
            enterWeb();
            return;
          }
          doStart(activity, status, start);
        });''',
         '''    start.setOnClickListener(
        x -> {
          if (webReady || !webEntryUrl().isEmpty()) {
            enterWeb();
            return;
          }
          doStart(activity, status, start);
          // The existing refreshState waits for a *real* Web auth URL.
          pendingAutoEnter = true;
        });'''),
        ('''    stop.setOnClickListener(
        x -> {
          startRequest.incrementAndGet();''',
         '''    stop.setOnClickListener(
        x -> {
          pendingAutoEnter = false;
          startRequest.incrementAndGet();'''),
    ],
}


def sha(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def modify(root: Path, home_template: str) -> dict:
    root = root.resolve()
    pending = {}
    changes = []
    for relative, replacements in EXPECTED.items():
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"STOP: missing upstream file {relative}")
        old = path.read_text(encoding="utf-8")
        new = old
        for before, after in replacements:
            n = new.count(before)
            if n != 1:
                raise RuntimeError(f"STOP: upstream anchor drift {relative}: {before[:55]!r} (found {n})")
            new = new.replace(before, after, 1)
        pending[path] = new
        changes.append({"path": relative, "before": sha(old), "after": sha(new)})
    home = root / HOME_PATH
    if home.exists():
        raise RuntimeError("STOP: home activity already exists, refusing to overwrite")
    if "public final class WishCodeHomeActivity extends AppCompatActivity" not in home_template:
        raise RuntimeError("STOP: unexpected home template")
    mobile = root / MOBILE_PATH
    if mobile.exists():
        raise RuntimeError("STOP: mobile stylesheet asset already exists")
    mobile_template = Path(__file__).with_name("wishcode-mobile.js").read_text(encoding="utf-8")
    if "wishcode-mobile-v04" not in mobile_template or "data-composer-input" not in mobile_template:
        raise RuntimeError("STOP: unexpected mobile stylesheet asset")

    for name, package in [("WishCodePreviewActivity", "ui"),
                          ("WishCodePreviewEntry", "ui"), ("WishCodePreviewPolicy", "util"),
                          ("WishCodePreviewHttp", "util")]:
        relative = f"app/src/main/java/com/deepseekharness/app/{package}/{name}.java"
        path = root / relative
        if path.exists():
            raise RuntimeError(f"STOP: preview source already exists: {relative}")
        source = Path(__file__).with_name(name + ".java").read_text(encoding="utf-8")
        if f"public final class {name}" not in source:
            raise RuntimeError(f"STOP: unexpected preview source: {name}")
        pending[path] = source
        changes.append({"path": relative, "before": None, "after": sha(source)})

    store = pending[root / "app/src/main/java/com/deepseekharness/app/core/ConfigStore.java"]
    if 'return flag(Constants.KEY_CONFIRM_SHELL, true);' not in store:
        raise RuntimeError("STOP: original Shell approval must remain enabled")
    if 'text(Constants.KEY_CONTAINER_RUNTIME, "proot")' not in store:
        raise RuntimeError("STOP: stable proot runtime must remain default")
    manifest = pending[root / "app/src/main/AndroidManifest.xml"]
    if manifest.count('android.intent.category.LAUNCHER') != 1:
        raise RuntimeError("STOP: expected exactly one launcher intent")
    gradle = pending[root / "app/build.gradle"]
    if "abiFilters 'arm64-v8a'" not in gradle:
        raise RuntimeError("STOP: original ARM64 filter missing")

    for path, new in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8", newline="")
    home.parent.mkdir(parents=True, exist_ok=True)
    home.write_text(home_template, encoding="utf-8", newline="")
    changes.append({"path": HOME_PATH, "before": None, "after": sha(home_template)})
    mobile.parent.mkdir(parents=True, exist_ok=True)
    mobile.write_text(mobile_template, encoding="utf-8", newline="")
    changes.append({"path": MOBILE_PATH, "before": None, "after": sha(mobile_template)})
    return {"base": BASE, "application_id": APP_ID,
            "android_apk_built": False, "compatibility_verified": False,
            "changes": changes}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source_root", type=Path)
    p.add_argument("--report", type=Path)
    p.add_argument("--template", type=Path, default=Path(__file__).with_name("WishCodeHomeActivity.java"))
    a = p.parse_args()
    result = modify(a.source_root, a.template.read_text(encoding="utf-8"))
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
