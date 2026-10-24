"""Regression contracts for staging GLM into the pinned Preview 002 APK."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import install_glm


class GlmInstallContracts(unittest.TestCase):
    def make_project(self, version_code=192,
                     version_name="0.5-preview-002-dsh0.2.1-rc.2",
                     package="app.wishcode.harnessmobile.v05trial2"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        assets = root / "app/src/main/assets"
        assets.mkdir(parents=True)
        (assets / "builtin-plugins.json").write_text(
            json.dumps({"schema": 1, "plugins": []}), encoding="utf-8")
        (assets / "managed-runtime-inputs.json").write_text(
            json.dumps({"schema": 1, "installs": []}), encoding="utf-8")
        (root / "app/build.gradle").write_text(
            'android { defaultConfig {\n'
            f'  applicationId "{package}"\n'
            f'  versionCode {version_code}\n'
            f'  versionName "{version_name}"\n'
            '} }\n', encoding="utf-8")
        (root / "app/src/main/java/com/deepseekharness/app/ui").mkdir(parents=True)
        return root

    def test_preview002_glm_preserves_version_code_and_package(self):
        root = self.make_project()
        with mock.patch.object(install_glm.subprocess, "run") as runner:
            install_glm.install(root)
        content = (root / "app/build.gradle").read_text(encoding="utf-8")
        self.assertIn('applicationId "app.wishcode.harnessmobile.v05trial2"', content)
        self.assertIn("versionCode 192", content)
        self.assertNotIn("versionCode 193", content)
        self.assertIn('versionName "0.5-preview-002-glm53-dsh0.2.1-rc.2"', content)
        registry = json.loads((root / "app/src/main/assets/builtin-plugins.json").read_text())
        self.assertEqual(registry["plugins"][0]["name"], "dsh-wishcode-glm")
        contract = json.loads((root / "app/src/main/assets/managed-runtime-inputs.json").read_text())
        self.assertTrue(any(x["asset"] == "builtin-plugins/dsh-wishcode-glm/lib/index.js"
                            for x in contract["installs"]))
        self.assertTrue((root / "app/src/main/java/com/deepseekharness/app/ui/WishCodeGlmSettings.java").exists())
        runner.assert_called_once()
        self.assertTrue(runner.call_args.kwargs.get("check"))

    def test_fail_closed_for_wrong_code_version_or_package(self):
        cases = [
            {"version_code": 191},
            {"version_code": 193},
            {"version_name": "0.5-preview-001-dsh0.2.1-rc.2"},
            {"package": "app.wishcode.harnessmobile.v05preview"},
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                root = self.make_project(**kwargs)
                with mock.patch.object(install_glm.subprocess, "run") as runner:
                    with self.assertRaisesRegex(ValueError, "GLM_(VERSION|PACKAGE)_DRIFT"):
                        install_glm.install(root)
                runner.assert_not_called()

    def test_second_install_rejected(self):
        root = self.make_project()
        with mock.patch.object(install_glm.subprocess, "run"):
            install_glm.install(root)
        with self.assertRaisesRegex(ValueError, "GLM_(REGISTRY_DRIFT|ALREADY_STAGED)"):
            install_glm.install(root)


if __name__ == "__main__":
    unittest.main()
