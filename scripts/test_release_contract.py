"""Pre-build invariant tests: no second browser and one coherent release version."""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

release = module("release_config")
patch = module("customize")
workflow = (REPO / ".github/workflows/build-custom-apk.yml").read_text(encoding="utf-8")
mobile = (HERE / "wishcode-mobile.js").read_text(encoding="utf-8")
home = (HERE / "WishCodeHomeActivity.java").read_text(encoding="utf-8")


class ReleaseIntegrityTests(unittest.TestCase):
    def test_one_release_identity_and_no_forced_glm(self):
        self.assertEqual(patch.APP_ID, release.APP_ID)
        gradle = str(patch.EXPECTED["app/build.gradle"])
        self.assertIn(f'versionCode {release.VERSION_CODE}', gradle)
        self.assertIn(release.VERSION_NAME, gradle)
        self.assertIn(f'test "$package" = "{release.APP_ID}"', workflow)
        self.assertIn(release.APK_NAME, workflow)
        self.assertIn(release.ARTIFACT_NAME, workflow)
        self.assertNotIn("GLM_VERSION_NAME", release.__dict__)
        self.assertNotIn("install_glm", workflow)
        self.assertNotIn("glm.test.mjs", workflow)
        self.assertNotIn("WishCodeGlmSettings", home)
        self.assertNotIn("GLM-5.3", home)
        self.assertIn("设置 → 模型", home)

    def test_no_glm_builtin_in_new_source_tree(self):
        self.assertFalse((HERE / "install_glm.py").exists())
        self.assertFalse((HERE / "WishCodeGlmSettings.java").exists())
        self.assertFalse((REPO / "plugins/dsh-wishcode-glm").exists())
        self.assertFalse((REPO / "tests/glm.test.mjs").exists())

    def test_signed_debug_app_is_separate_from_previous_install(self):
        self.assertNotEqual(release.APP_ID, "app.wishcode.harnessmobile.v05trial2")
        self.assertIn("v05trial3", release.APP_ID)
        self.assertIn("许愿编程·003", str(
            patch.EXPECTED["app/src/main/res/values/strings.xml"]))
        self.assertIn("V0.5 测试版003", home)
        self.assertIn("Preview 003", workflow)

    def test_retired_browser_not_packaged_or_replaced(self):
        manifest = patch.NEW_MANIFEST
        self.assertNotIn("WishCodePreviewActivity", manifest)
        self.assertNotIn(":wishcode_preview", manifest)
        self.assertNotIn("WebPreviewActivity.java", patch.EXPECTED)
        self.assertNotIn("DshaApp.java", patch.EXPECTED)
        source = (HERE / "customize.py").read_text(encoding="utf-8")
        self.assertNotIn("WishCodePreviewActivity", source)
        self.assertNotIn("WishCodePreviewEntry", source)
        self.assertNotIn("WishCodePreviewPolicy", source)
        self.assertNotIn("wishcode-local-artifact", mobile)
        self.assertNotIn("MutationObserver", mobile)
        self.assertNotIn("预览网页 · HTML 实时交互", home)
        self.assertIn("项目文件", home)
        self.assertIn("插件管理", home)

    def test_manual_only_and_regression_before_compile(self):
        self.assertIn("workflow_dispatch:", workflow)
        for forbidden in ("  push:", "  pull_request:", "  schedule:"):
            self.assertNotIn(forbidden, workflow)
        self.assertLess(workflow.index("python3 -m unittest discover"),
                        workflow.index("Compile real Standard Debug APK"))
        self.assertLess(workflow.index("node scripts/test_contextual_preview.cjs"),
                        workflow.index("Compile real Standard Debug APK"))
        self.assertIn("test_side_install.py", "\n".join(
            p.name for p in HERE.glob("test_*.py")))
        self.assertNotIn("cancel-in-progress: true", workflow)


if __name__ == "__main__":
    unittest.main()
