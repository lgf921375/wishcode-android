"""Static regression contracts for ColorOS phone UI; not device rendering tests."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
ENTRY = (ROOT / "WishCodePreviewEntry.java").read_text(encoding="utf-8")
STYLES = (ROOT / "wishcode-mobile.js").read_text(encoding="utf-8")


class MobileUxTests(unittest.TestCase):
    def test_limited_preview_no_longer_claimed_or_injected(self):
        patch_source = (ROOT / "customize.py").read_text(encoding="utf-8")
        home = (ROOT / "WishCodeHomeActivity.java").read_text(encoding="utf-8")
        self.assertNotIn("WishCodePreviewEntry.install(this)", patch_source)
        self.assertNotIn("WishCodePreviewEntry.open(WebPreviewActivity.this, url)", patch_source)
        self.assertNotIn("WishCodePreviewEntry.open(this, null)", home)
        self.assertNotIn("预览网页 · HTML 实时交互", home)
        self.assertNotIn("wishcode-local-artifact", STYLES)
        self.assertNotIn("function previewCandidate(", STYLES)
        self.assertNotIn("MutationObserver", STYLES)
        self.assertIn("开始聊天编程", home)
        self.assertIn("GLM-5.3 · API / 套餐设置", home)
        self.assertIn("项目文件", home)
        self.assertIn("插件管理", home)

    def test_contextual_preview_node_smoke(self):
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js unavailable; this is not a passing JS runtime test")
        subprocess.run([node, str(ROOT / "test_contextual_preview.cjs")],
                       cwd=ROOT.parent, check=True, timeout=25)

    def test_model_popover_only_is_constrained(self):
        # Verified upstream shape: model menu is portaled to body, role=group,
        # whereas reasoning effort uses role=menu.
        self.assertIn('[class*="_7KE1Ra_menu"][role="group"]', STYLES)
        self.assertIn('[class*="_7KE1Ra_groups"][role="menu"]', STYLES)
        self.assertIn('max-height: min(48dvh, 420px) !important', STYLES)
        self.assertIn('max-height: 34dvh !important', STYLES)
        self.assertIn('overflow-y: auto !important', STYLES)
        self.assertIn('overscroll-behavior: contain', STYLES)
        self.assertIn('min-height: 44px', STYLES)

    def test_no_provider_side_effects_or_font_override(self):
        self.assertIn('window.top !== window', STYLES)
        self.assertNotIn('fetch(', STYLES)
        self.assertNotIn('XMLHttpRequest', STYLES)
        self.assertNotIn('localStorage', STYLES)
        self.assertNotIn('font-family:', STYLES)
        self.assertNotIn('display: none !important; } [role="menuitemradio"]', STYLES)
        self.assertIn('font(b)', ENTRY)
        self.assertIn('view.setIncludeFontPadding(true)', ENTRY)

    def test_original_ofm_nav_fix_is_retained(self):
        self.assertIn('.ofm_root .ofm_nav {', STYLES)
        self.assertIn('position: relative !important', STYLES)
        self.assertIn('flex-wrap: nowrap !important', STYLES)


if __name__ == "__main__":
    unittest.main()
