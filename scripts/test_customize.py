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
        self.assertIn("showPluginHelp", HOME)

    def test_app_identity_is_separate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture(root)
            patch.modify(root, HOME)
            self.assertIn('applicationId "app.wishcode.harnessmobile"',
                          (root / "app/build.gradle").read_text())


if __name__ == "__main__":
    unittest.main()
