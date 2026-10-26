"""Offline, contract-level checks for the optional Flash compatibility package."""
from __future__ import annotations

import gzip
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare_purge_flash as armor

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


class FlashCompatTests(unittest.TestCase):
    def sample(self):
        skills = (
            b'const disposer = skills.register({\n'
            + armor.ANCHOR
            + b'      content: body,\n    });\n'
        )
        package = json.dumps({
            "name": "dsh-purge-flash",
            "version": "1.4.0",
            "dsh": {"bundle": {"patch": "./cordis.patch.yml"}},
        }).encode()
        files = {
            "lib/skills.js": skills,
            "lib/index.js": b'export const inject = ["systemPrompt"];\n',
            "package.json": package,
            "cordis.patch.yml": b"- insert: []\n",
            "skill/armor-playbook.md": b"# armor-playbook\n",
        }
        hashes = {key: armor.git_blob_sha(files[key]) for key in armor.SOURCE_BLOB_SHA}
        return files, hashes

    def test_patch_is_exactly_one_missing_source_and_archive_is_importable(self):
        files, hashes = self.sample()
        with patch.dict(armor.SOURCE_BLOB_SHA, hashes, clear=True):
            result = armor.patch_source(files)
        self.assertIn(b'source: "runtime"', files["lib/skills.js"])
        self.assertEqual(files["lib/skills.js"].count(armor.REPLACEMENT), 1)
        self.assertIn(armor.INJECT_REPLACEMENT, files["lib/index.js"])
        self.assertFalse(result["auto_installed"])
        self.assertFalse(result["auto_enabled"])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "compat.tgz"
            digest = armor.make_archive(files, path)
            self.assertEqual(digest, armor.hashlib.sha256(path.read_bytes()).hexdigest())
            with tarfile.open(path, "r:gz") as archive:
                self.assertIn("package/package.json", archive.getnames())
                patched = archive.extractfile("package/lib/skills.js").read()
                self.assertIn(b'source: "runtime"', patched)
                patched_index = archive.extractfile("package/lib/index.js").read()
                self.assertIn(armor.INJECT_REPLACEMENT, patched_index)

    def test_rejects_unexpected_upstream_bytes(self):
        files, hashes = self.sample()
        with patch.dict(armor.SOURCE_BLOB_SHA, hashes, clear=True):
            files["lib/skills.js"] = files["lib/skills.js"].replace(b"armor-playbook", b"other-playbook")
            with self.assertRaisesRegex(ValueError, "blob SHA mismatch"):
                armor.patch_source(files)

    def test_rejects_missing_skill_dependency_injection(self):
        files, hashes = self.sample()
        with patch.dict(armor.SOURCE_BLOB_SHA, hashes, clear=True):
            files["lib/index.js"] = b'export const inject = ["other"];\n'
            hashes["lib/index.js"] = armor.git_blob_sha(files["lib/index.js"])
            with self.assertRaisesRegex(ValueError, "injection anchor drift"):
                armor.patch_source(files)

    def test_rejects_unsafe_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "evil.tar.gz"
            with tarfile.open(path, "w:gz") as archive:
                entry = tarfile.TarInfo("repo/link")
                entry.type = tarfile.SYMTYPE
                entry.linkname = "/etc/passwd"
                archive.addfile(entry)
            with self.assertRaisesRegex(ValueError, "source member type"):
                armor.extract_source(path)

    def test_ui_only_exports_package_after_user_action(self):
        home = (ROOT / "WishCodeHomeActivity.java").read_text(encoding="utf-8")
        workflow = (REPO / ".github/workflows/build-custom-apk.yml").read_text(encoding="utf-8")
        self.assertIn("showArmorCompat", home)
        self.assertIn("ActivityResultContracts.CreateDocument", home)
        self.assertIn('getAssets().open(ARMOR_ARCHIVE_ASSET)', home)
        self.assertIn('exportArmorArchive.launch(ARMOR_ARCHIVE_FILE)', home)
        self.assertNotIn("auto-install-armor", home)
        self.assertIn("prepare_purge_flash.py", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("  push:", workflow)
        self.assertNotIn("  schedule:", workflow)
        self.assertLess(workflow.index("prepare_purge_flash.py"),
                        workflow.index("Compile real Standard Debug APK"))

    def test_source_is_pinned_and_archive_is_bundled_not_installed(self):
        script = (ROOT / "prepare_purge_flash.py").read_text(encoding="utf-8")
        workflow = (REPO / ".github/workflows/build-custom-apk.yml").read_text(encoding="utf-8")
        self.assertIn(armor.UPSTREAM_COMMIT, script)
        self.assertIn(armor.UPSTREAM_COMMIT, workflow)
        self.assertIn("SOURCE_BLOB_SHA", script)
        self.assertIn('dsh-purge-flash-v1.4.0-compat.tgz', workflow)
        self.assertNotIn("PluginRepository.install", script)
        self.assertNotIn("plugin --profile", workflow)


if __name__ == "__main__":
    unittest.main()
