"""Installation safety: new trial APK coexists with earlier WishCode builds."""
from pathlib import Path
import unittest
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("customize", HERE / "customize.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
WORKFLOW = (HERE.parent / ".github/workflows/build-custom-apk.yml").read_text(encoding="utf-8")


class SideBySideInstallTests(unittest.TestCase):
    def test_new_trial_package_is_distinct_and_versioned(self):
        self.assertEqual(patch.APP_ID, "app.wishcode.harnessmobile.v05trial2")
        self.assertNotEqual(patch.APP_ID, "app.wishcode.harnessmobile.v05preview")
        self.assertIn("versionCode 192", str(patch.EXPECTED["app/build.gradle"]))
        self.assertIn("0.5-preview-002-dsh0.2.1-rc.2", str(patch.EXPECTED["app/build.gradle"]))
        self.assertIn("许愿编程·测试版", str(patch.EXPECTED["app/src/main/res/values/strings.xml"]))

    def test_workflow_verifies_new_package_before_upload(self):
        self.assertIn('test "$package" = "app.wishcode.harnessmobile.v05trial2"', WORKFLOW)
        self.assertIn("WishCode-v0.5-preview-002-arm64-debug.apk", WORKFLOW)
        self.assertIn("WishCode-V0.5-Preview-002-Android-APK", WORKFLOW)
        self.assertNotIn("test \"$package\" = \"app.wishcode.harnessmobile.v05preview\"", WORKFLOW)
        self.assertIn("workflow_dispatch:", WORKFLOW)
        self.assertNotIn("  push:", WORKFLOW)
        self.assertNotIn("  schedule:", WORKFLOW)

    def test_no_signing_key_or_credentials_embedded(self):
        source = (HERE / "customize.py").read_text(encoding="utf-8")
        self.assertNotIn("signingConfigs.create", source)
        self.assertNotIn("debug.keystore", source)
        self.assertNotIn("private_key", source.lower())


if __name__ == "__main__":
    unittest.main()
