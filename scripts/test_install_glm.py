"""GLM staging contract: fail before Android tooling if preview version drifts."""
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock
from release_config import APP_ID, VERSION_CODE, VERSION_NAME, GLM_VERSION_NAME

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("install_glm", HERE / "install_glm.py")
glm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(glm)

OLD_VERSION = f'versionName "{VERSION_NAME}"'
GLM_VERSION = f'versionName "{GLM_VERSION_NAME}"'


def build_fixture(root, code=VERSION_CODE, version=OLD_VERSION):
    assets = root / "app/src/main/assets"
    assets.mkdir(parents=True)
    ui = root / "app/src/main/java/com/deepseekharness/app/ui"
    ui.mkdir(parents=True)
    (assets / "builtin-plugins.json").write_text(
        json.dumps({"schema": 1, "plugins": []}), encoding="utf-8")
    (assets / "managed-runtime-inputs.json").write_text(
        json.dumps({"schema": 1, "installs": []}), encoding="utf-8")
    gradle = root / "app/build.gradle"
    gradle.write_text(
        f'android {{\n applicationId "{APP_ID}"\n'
        f' versionCode {code}\n {version}\n}}\n', encoding="utf-8")
    return assets, gradle


class GlmStageTests(TestCase):
    def test_stages_glm_without_changing_independent_package_version_code(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            assets, gradle = build_fixture(root)
            with mock.patch.object(glm.subprocess, "run") as generator:
                glm.install(root)
            generator.assert_called_once()
            self.assertEqual(gradle.read_text().count(f"versionCode {VERSION_CODE}"), 1)
            self.assertEqual(gradle.read_text().count(GLM_VERSION), 1)
            self.assertNotIn(OLD_VERSION, gradle.read_text())
            self.assertIn(APP_ID, gradle.read_text())
            registry = json.loads((assets / "builtin-plugins.json").read_text())
            self.assertEqual([p["name"] for p in registry["plugins"]],
                             ["dsh-wishcode-glm"])
            installs = json.loads(
                (assets / "managed-runtime-inputs.json").read_text())["installs"]
            self.assertEqual(len(installs), 4)
            for record in installs:
                self.assertTrue((assets / record["asset"]).is_file())
                self.assertTrue(record["target"].startswith("root/dsha-wishcode-glm/"))
            self.assertTrue((root /
                "app/src/main/java/com/deepseekharness/app/ui/WishCodeGlmSettings.java").is_file())

    def test_rejects_previous_preview_version_before_writing_anything(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            assets, gradle = build_fixture(
                root, code=192, version='versionName "0.5-preview-002-dsh0.2.1-rc.2"')
            before = gradle.read_text()
            with mock.patch.object(glm.subprocess, "run") as generator:
                with self.assertRaisesRegex(ValueError, "GLM_VERSION_DRIFT"):
                    glm.install(root)
            generator.assert_not_called()
            self.assertEqual(gradle.read_text(), before)
            self.assertFalse((assets / "builtin-plugins/dsh-wishcode-glm").exists())
            self.assertEqual(json.loads((assets / "builtin-plugins.json").read_text())
                             ["plugins"], [])

    def test_rejects_future_version_name_drift_fail_closed(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            assets, gradle = build_fixture(
                root, code=193, version='versionName "0.5-preview-004-dsh0.2.1-rc.2"')
            original = gradle.read_text()
            with mock.patch.object(glm.subprocess, "run") as generator:
                with self.assertRaisesRegex(ValueError, "GLM_VERSION_DRIFT"):
                    glm.install(root)
            generator.assert_not_called()
            self.assertEqual(gradle.read_text(), original)
            self.assertFalse((assets / "builtin-plugins/dsh-wishcode-glm").exists())

    def test_second_install_refused(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            assets, gradle = build_fixture(root)
            with mock.patch.object(glm.subprocess, "run") as generator:
                glm.install(root)
                with self.assertRaisesRegex(ValueError, "GLM_REGISTRY_DRIFT"):
                    glm.install(root)
            generator.assert_called_once()
