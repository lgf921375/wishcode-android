"""Regression tests: opt-in DNF game workflow package, no implicit builds."""
from pathlib import Path
import json
import tarfile
import tempfile
import unittest

import prepare_dnf_dev as dnf

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


class DnfDeveloperToolkitTests(unittest.TestCase):
    def test_archive_contains_three_runtime_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / dnf.ARCHIVE_NAME
            result = dnf.create(out)
            self.assertEqual(result["name"], "dsh-wishcode-dnf-dev")
            self.assertFalse(result["default_auto_installed"])
            self.assertFalse(result["verified_android_runtime"])
            with tarfile.open(out, "r:gz") as archive:
                package = json.load(archive.extractfile("package/package.json"))
                js = archive.extractfile("package/lib/index.js").read().decode()
                patch = archive.extractfile("package/cordis.patch.yml").read().decode()
                self.assertEqual(package["dsh"]["bundle"]["patch"], "./cordis.patch.yml")
                self.assertEqual(package["version"], "0.1.0")
                self.assertIn("source: 'runtime'", js)
                self.assertIn("wishcode-dnf-combat", js)
                self.assertIn("wishcode-dnf-art", js)
                self.assertIn("wishcode-dnf-release", js)
                self.assertIn("name: 'dsh-wishcode-dnf-dev'", patch)
                self.assertIn("enabled: true", patch)
                self.assertNotIn("https://", js)

    def test_package_bytes_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / "a.tgz", Path(directory) / "b.tgz"
            one = dnf.create(a)
            two = dnf.create(b)
            self.assertEqual(one["sha256"], two["sha256"])
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_native_ui_is_user_approved(self):
        home = (HERE / "WishCodeHomeActivity.java").read_text()
        workflow = (REPO / ".github/workflows/build-custom-apk.yml").read_text()
        self.assertIn("showDnfDevToolkit", home)
        self.assertIn("exportDnfArchive.launch(DNF_ARCHIVE_FILE)", home)
        self.assertIn("getAssets().open(DNF_ARCHIVE_ASSET)", home)
        self.assertIn("GitHub 源码插件", home)
        self.assertIn("dsh-wishcode-dnf-dev-0.1.0.tgz", home)
        self.assertIn("prepare_dnf_dev.py", workflow)
        self.assertIn("DNF-DEV-SHA256.txt", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("\n  schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertLess(workflow.index("prepare_dnf_dev.py"),
                        workflow.index("Compile real Standard Debug APK"))

    def test_no_copyright_assets_or_model_keys(self):
        files = dnf.contents()
        combined = b"\n".join(files.values()).decode()
        self.assertIn("original", combined)
        self.assertIn("explicit per-build approval", combined)
        self.assertNotIn("API_KEY=", combined)
        self.assertNotIn("dsh-purge-flash", combined)


if __name__ == "__main__":
    unittest.main()
