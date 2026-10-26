"""Regression for DSHA strict APK asset manifest registration (#15 build failure)."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import register_wishcode_assets as assets

HERE = Path(__file__).resolve().parent


class AssetDeploymentTests(unittest.TestCase):
    def build_fixture(self, root: Path):
        manifest = root / assets.MANIFEST
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({
            "schema": 1,
            "packagedFiles": ["one-unchanged.bin"],
            "dynamicReaders": [{"source": "upstream/Existing.java", "assets": ["one-unchanged.bin"]}],
            "sourceInputs": [],
            "packagedTrees": [],
            "sourceOnlyTrees": [],
            "generatedFiles": [],
            "externalGeneratedFiles": [],
        }))
        java = root / assets.JAVA_READER
        java.parent.mkdir(parents=True, exist_ok=True)
        java.write_text('private static final String ARMOR_ARCHIVE_ASSET = "'+
                        assets.ASSETS[0]+'";\nprivate static final String DNF_ARCHIVE_ASSET = "'+
                        assets.ASSETS[1]+'";\n')
        a = root / "app/src/main/assets" / assets.ASSETS[0]
        b = root / "app/src/main/assets" / assets.ASSETS[1]
        for p, data in ((a, b"flash-archive"), (b, b"dnf-archive")):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        armor = root / "armor-compat-report.json"
        dnf = root / "dnf-dev-report.json"
        armor.write_text(json.dumps({
            "upstream_commit": "636059f8002b060fb4dca1c1b47c02e1ef2a2f31",
            "archive_sha256": hashlib.sha256(a.read_bytes()).hexdigest()}))
        dnf.write_text(json.dumps({
            "name": "dsh-wishcode-dnf-dev",
            "version": "0.1.0",
            "sha256": hashlib.sha256(b.read_bytes()).hexdigest()}))
        return manifest, a, b, armor, dnf

    def test_exact_two_assets_are_registered_without_disabling_upstream_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, a, b, armor, dnf = self.build_fixture(root)
            result = assets.register(root, armor_report=armor, dnf_report=dnf)
            m = json.loads(manifest.read_text())
            self.assertEqual(m["packagedFiles"], ["one-unchanged.bin", *assets.ASSETS])
            self.assertEqual(m["dynamicReaders"][0]["source"], "upstream/Existing.java")
            self.assertEqual(m["dynamicReaders"][1]["source"], assets.JAVA_READER)
            self.assertEqual(m["dynamicReaders"][1]["assets"], list(assets.ASSETS))
            self.assertFalse(result["auto_installed"])
            # Re-running against modified input must STOP, not add duplicates.
            with self.assertRaisesRegex(ValueError, "already exists"):
                assets.register(root, armor_report=armor, dnf_report=dnf)

    def test_checksum_mismatch_fails_without_modifying_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, a, b, armor, dnf = self.build_fixture(root)
            old = manifest.read_bytes()
            b.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                assets.register(root, armor_report=armor, dnf_report=dnf)
            self.assertEqual(manifest.read_bytes(), old)

    def test_untrusted_reader_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest, a, b, armor, dnf = self.build_fixture(root)
            old = manifest.read_bytes()
            (root / assets.JAVA_READER).write_text("not a WishCode reader")
            with self.assertRaisesRegex(ValueError, "reader anchor drift"):
                assets.register(root, armor_report=armor, dnf_report=dnf)
            self.assertEqual(manifest.read_bytes(), old)

    def test_manual_workflow_executes_registration_before_gradle(self):
        workflow = (HERE.parent / ".github/workflows/build-custom-apk.yml").read_text()
        self.assertIn("register_wishcode_assets.py", workflow)
        self.assertLess(workflow.index("register_wishcode_assets.py"),
                        workflow.index("Compile real Standard Debug APK"))
        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("\n  schedule:", workflow)


if __name__ == "__main__":
    unittest.main()
