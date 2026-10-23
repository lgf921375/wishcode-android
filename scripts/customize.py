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
APP_ID = "app.wishcode.harnessmobile"
HOME_PATH = "app/src/main/java/com/deepseekharness/app/ui/WishCodeHomeActivity.java"
MAIN_MANIFEST = '''        <activity
            android:name=".ui.MainActivity"
            android:exported="true"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>'''
NEW_MANIFEST = '''        <activity
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
    "app/build.gradle": [
        ('applicationId "dsh.android.client"', f'applicationId "{APP_ID}"'),
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
    ],
    "app/src/main/java/com/deepseekharness/app/ui/OnboardingUi.java": [
        ('TextView brand = text("DSHA", 18, R.color.text);',
         'TextView brand = text("许愿编程", 18, R.color.text);'),
    ],
    "app/src/main/java/com/deepseekharness/app/ui/LaunchFragment.java": [
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
        path.write_text(new, encoding="utf-8", newline="")
    home.parent.mkdir(parents=True, exist_ok=True)
    home.write_text(home_template, encoding="utf-8", newline="")
    changes.append({"path": HOME_PATH, "before": None, "after": sha(home_template)})
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
