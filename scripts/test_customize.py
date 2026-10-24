"""Source patch contract tests only. APK build/device test is separate."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("customize", HERE / "customize.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
HOME = (HERE / "WishCodeHomeActivity.java").read_text(encoding="utf-8")


def fixture(root):
    for path, replacements in patch.EXPECTED.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(before for before, _ in replacements), encoding="utf-8")
    with (root / "app/build.gradle").open("a") as f:
        f.write("\nabiFilters 'arm64-v8a'\n")
    with (root / "app/src/main/java/com/deepseekharness/app/core/ConfigStore.java").open("a") as f:
        f.write('\nreturn flag(Constants.KEY_CONFIRM_SHELL, true);\n')
        f.write('return "proroot".equals(text(Constants.KEY_CONTAINER_RUNTIME, "proot"));\n')


class PatchTests(unittest.TestCase):
    def test_home_is_created(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture(root)
            result = patch.modify(root, HOME)
            self.assertFalse(result["android_apk_built"])
            self.assertEqual((root / "app/src/main/AndroidManifest.xml")
                             .read_text().count("android.intent.category.LAUNCHER"), 1)
            self.assertTrue((root / patch.HOME_PATH).exists())
            self.assertTrue((root / patch.MOBILE_PATH).exists())

    def test_first_run_least_privilege_and_stop(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture(root)
            patch.modify(root, HOME)
            config = (root / "app/src/main/java/com/deepseekharness/app/core/ConfigStore.java").read_text()
            launch = (root / "app/src/main/java/com/deepseekharness/app/ui/LaunchFragment.java").read_text()
            self.assertIn('KEY_PERMISSION_MODE, "workspace-write"', config)
            self.assertIn('KEY_CONFIRM_SHELL, true', config)
            self.assertIn("pendingAutoEnter = false;", launch)
            self.assertIn("pendingAutoEnter = true;", launch)

    def test_anchor_drift_fails_without_partial_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture(root)
            source = root / "app/build.gradle"
            original = source.read_text()
            bad = root / "app/src/main/java/com/deepseekharness/app/ui/LaunchFragment.java"
            bad.write_text("unexpected source")
            with self.assertRaises(RuntimeError):
                patch.modify(root, HOME)
            self.assertEqual(source.read_text(), original)
            self.assertFalse((root / patch.HOME_PATH).exists())

    def test_reapply_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture(root)
            patch.modify(root, HOME)
            with self.assertRaises(RuntimeError):
                patch.modify(root, HOME)

    def test_guide_has_no_credential_storage(self):
        self.assertIn("deepseek-flash", HOME)
        self.assertNotIn("getApiKey(", HOME)
        self.assertNotIn("setApiKey(", HOME)
        self.assertIn("openPlugins", HOME)

    def test_pinned_free_model_install_requires_user_action(self):
        self.assertIn("showModelChoice", HOME)
        self.assertIn("showFreeModelNotice", HOME)
        self.assertIn("检查安装包", HOME)
        self.assertIn("PluginInstallActivity.class", HOME)
        self.assertIn('appendQueryParameter("sha256", FREE_MODEL_SHA)', HOME)
        self.assertIn('appendQueryParameter("version", "2.5.9")', HOME)
        # No startup side effect; launch happens only from an explicit button.
        constructor = HOME.split("protected void onCreate", 1)[1].split("private void openWeb", 1)[0]
        self.assertNotIn("openPinnedPluginInstaller()", constructor)

    def test_uses_exact_release_not_impostor_npm(self):
        self.assertIn("Ebony-Vinyl/dsh-our-free-model/releases/download/v2.5.9/", HOME)
        self.assertIn("3c98427d8144041568c12dd5c61c42632d022856e8f5327e66b813fe80d269a2", HOME)
        self.assertNotIn("dsh plugin add dsh-our-free-model", HOME)

    def test_free_models_are_never_claimed_unlimited_or_offline(self):
        self.assertIn("每小时最多 200 次", HOME)
        self.assertIn("隐私", HOME) if "隐私" in HOME else self.assertIn("数据", HOME)
        self.assertIn("不是下载到手机", HOME)

    def test_mobile_layout_is_scoped_to_dsh_webview(self):
        js = (HERE / "wishcode-mobile.js").read_text(encoding="utf-8")
        self.assertIn("max-width: 760px", js)
        self.assertIn("data-mobile-nav", js)
        self.assertIn('role="dialog"', js)
        self.assertIn("data-composer-input", js)
        self.assertIn("window.top !== window", js)
        self.assertNotIn("fetch(", js)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture(root)
            patch.modify(root, HOME)
            source = (root / "app/src/main/java/com/deepseekharness/app/ui/WebPageScripts.java").read_text()
            self.assertIn('read(context, "web-integration/wishcode-mobile.js")', source)

    def test_ofm_mobile_tabs_stop_covering_page(self):
        js = (HERE / "wishcode-mobile.js").read_text(encoding="utf-8")
        self.assertIn(".ofm_root .ofm_nav {", js)
        self.assertIn("position: relative !important", js)
        self.assertIn("top: auto !important", js)
        self.assertIn(".ofm_root .ofm_tabs {", js)
        self.assertIn("flex-wrap: nowrap !important", js)
        self.assertIn("overflow-x: auto !important", js)
        self.assertIn(".ofm_root .ofm_tabglider { display: none !important; }", js)
        self.assertIn('.ofm_root .ofm_tab[data-on="true"]', js)
        self.assertIn("min-height: 44px", js)
        self.assertNotIn("font-family:", js)
        self.assertNotIn("fetch(", js)

    def test_restore_dialog_compact_copy_preserves_choice(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture(root)
            patch.modify(root, HOME)
            main = (root / "app/src/main/java/com/deepseekharness/app/ui/MainActivity.java").read_text()
            self.assertIn('"恢复旧备份？", "Restore backup?"', main)
            self.assertIn("若曾导出旧备份", main)
            self.assertIn("无需开启所有文件访问", main)
            self.assertNotIn("是否需要恢复以前的备份？", main)
            # Only content anchors are touched, so upstream restore/skip handlers remain intact.
            for before, after in patch.EXPECTED[
                "app/src/main/java/com/deepseekharness/app/ui/MainActivity.java"
            ]:
                self.assertIn(after, main)
                self.assertNotIn(before, main)

    def test_coloros_pinyin_system_font_is_preserved(self):
        self.assertNotIn('Typeface.create("sans-serif"', HOME)
        self.assertIn('label.getTypeface()', HOME)
        self.assertIn('label.setIncludeFontPadding(true)', HOME)
        self.assertIn('label.setFallbackLineSpacing(true)', HOME)
        self.assertIn('label.setLineSpacing(', HOME)
        self.assertIn('button.setSingleLine(false)', HOME)
        self.assertIn('button.setMaxLines(4)', HOME)
        self.assertIn('button.setFallbackLineSpacing(true)', HOME)
        self.assertIn('button.setLineSpacing(', HOME)
        self.assertIn('LayoutParams.WRAP_CONTENT', HOME)

    def test_onboarding_preserves_pinyin_metrics(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture(root)
            patch.modify(root, HOME)
            src = (root / "app/src/main/java/com/deepseekharness/app/ui/OnboardingUi.java").read_text()
            self.assertIn("t.setIncludeFontPadding(true)", src)
            self.assertIn("t.setFallbackLineSpacing(true)", src)
            self.assertIn("b.setSingleLine(false)", src)
            self.assertIn("b.setMaxLines(4)", src)
            self.assertIn("brand.getTypeface()", src)
            self.assertIn("heading.getTypeface()", src)

    def test_pinyin_web_typography_preserves_font_and_text_visibility(self):
        js = (HERE / "wishcode-mobile.js").read_text(encoding="utf-8")
        self.assertIn('line-height: 1.9 !important', js)
        self.assertIn('overflow-wrap: break-word', js)
        self.assertIn('overflow-y: auto', js)
        self.assertIn('height: auto !important', js)
        self.assertIn('overflow-x: auto', js)
        self.assertNotIn('overflow-x: clip', js)
        self.assertNotIn('font-family:', js)
        self.assertNotIn('font-size:', js)

    def test_github_search_plugin_is_opt_in_and_pinned(self):
        self.assertIn("GitHub 搜索与源码研究", HOME)
        self.assertIn("showGitHubHelp", HOME)
        self.assertIn("openGithubPluginInstaller", HOME)
        self.assertIn("dsh-plugin-github-0.1.6.tgz", HOME)
        self.assertIn(
            "cb76ddc1fd02d71dea02bfede0ecc9137877ef1b5c31ac8ca011fe9b1dcf5db3", HOME
        )
        self.assertIn('appendQueryParameter("sha256", GITHUB_PLUGIN_SHA)', HOME)
        self.assertIn('appendQueryParameter("version", "0.1.6")', HOME)
        self.assertIn("未在本机 DSH 0.2.1-rc.2 上验证兼容性", HOME)
        self.assertIn("github_search", HOME)
        self.assertIn("github_get", HOME)
        self.assertIn("它不提供克隆、推送或写入操作", HOME)
        # The user must explicitly open the dialog and approve install.
        start = HOME.split("protected void onCreate", 1)[1].split("private void openWeb", 1)[0]
        self.assertNotIn("openGithubPluginInstaller()", start)

    def test_app_identity_is_separate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture(root)
            patch.modify(root, HOME)
            self.assertIn('applicationId "app.wishcode.harnessmobile.v05preview"',
                          (root / "app/build.gradle").read_text())


if __name__ == "__main__":
    unittest.main()
