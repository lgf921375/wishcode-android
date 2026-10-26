"""Installation safety: new trial APK coexists with earlier WishCode builds."""
from pathlib import Path
import unittest
import importlib.util
from release_config import APP_ID, VERSION_CODE, VERSION_NAME, APK_NAME, ARTIFACT_NAME

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("customize", HERE / "customize.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
WORKFLOW = (HERE.parent / ".github/workflows/build-custom-apk.yml").read_text(encoding="utf-8")


class SideBySideInstallTests(unittest.TestCase):
    def test_new_trial_package_is_distinct_and_versioned(self):
        self.assertEqual(patch.APP_ID, APP_ID)
        self.assertNotEqual(patch.APP_ID, "app.wishcode.harnessmobile.v05trial2")
        self.assertIn(f"versionCode {VERSION_CODE}", str(patch.EXPECTED["app/build.gradle"]))
        self.assertIn(VERSION_NAME, str(patch.EXPECTED["app/build.gradle"]))
        self.assertIn("许愿编程·007", str(patch.EXPECTED["app/src/main/res/values/strings.xml"]))

    def test_workflow_verifies_new_package_before_upload(self):
        self.assertIn(f'test "$package" = "{APP_ID}"', WORKFLOW)
        self.assertIn(APK_NAME, WORKFLOW)
        self.assertIn(ARTIFACT_NAME, WORKFLOW)
        self.assertNotIn('test "$package" = "app.wishcode.harnessmobile.v05trial2"', WORKFLOW)
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
