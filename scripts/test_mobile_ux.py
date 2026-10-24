"""Static regression contracts for ColorOS phone UI; not device rendering tests."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
ENTRY = (ROOT / "WishCodePreviewEntry.java").read_text(encoding="utf-8")
STYLES = (ROOT / "wishcode-mobile.js").read_text(encoding="utf-8")


class MobileUxTests(unittest.TestCase):
    def test_chat_has_no_permanent_preview_toolbar(self):
        patch_source = (ROOT / "customize.py").read_text(encoding="utf-8")
        self.assertNotIn("WishCodePreviewEntry.install(this)", patch_source)
        self.assertNotIn("public static void install(Activity host)", ENTRY)
        self.assertNotIn("shortcut(host", ENTRY)
        self.assertNotIn("bar.addView(", ENTRY)
        # Only a real user click on a validated local link can open preview.
        self.assertIn("WishCodePreviewPolicy.normalize(url", patch_source)
        self.assertIn("request.hasGesture()", patch_source)
        self.assertIn("WishCodePreviewEntry.open(WebPreviewActivity.this, url)", patch_source)
        self.assertIn("WishCodePreviewActivity.class", ENTRY)
        self.assertIn("putExtra(\"chat_port\", chatPort)", ENTRY)
        self.assertIn('putExtra("candidate", candidate)', ENTRY)
        # Home screen retains the manual preview fallback outside of chat.
        home = (ROOT / "WishCodeHomeActivity.java").read_text(encoding="utf-8")
        self.assertIn("WishCodePreviewEntry.open(this, null)", home)

    def test_contextual_preview_not_a_persistent_nav(self):
        source = (ROOT / "wishcode-mobile.js").read_text(encoding="utf-8")
        activity = (ROOT / "WishCodePreviewActivity.java").read_text(encoding="utf-8")
        self.assertIn("function previewCandidate(raw)", source)
        self.assertIn("link.closest('[data-chat-flow]')", source)
        self.assertIn("本地网页链接 · 尚未验证服务", source)
        self.assertIn("wishcode-local-artifact-open", source)
        self.assertIn("DOMContentLoaded", source)
        self.assertIn("MutationObserver", source)
        self.assertIn("decorated = new WeakSet()", source)
        self.assertIn("button.textContent = '预览网页'", source)
        self.assertIn("button.target = '_self'", source)
        self.assertNotIn("window.location =", source)
        self.assertNotIn("fetch(", source)
        self.assertIn('putExtra("from_chat_link", candidate != null)', ENTRY)
        self.assertIn('getBooleanExtra("from_chat_link", false)', activity)
        self.assertIn('WishCodePreviewPolicy.normalize(candidate, chatPort) != null', activity)
        self.assertIn('if (state == null &&', activity)
        self.assertIn('approve();', activity)

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
