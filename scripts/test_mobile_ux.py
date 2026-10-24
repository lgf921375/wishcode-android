"""Static regression contracts for ColorOS phone UI; not device rendering tests."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
ENTRY = (ROOT / "WishCodePreviewEntry.java").read_text(encoding="utf-8")
STYLES = (ROOT / "wishcode-mobile.js").read_text(encoding="utf-8")


class MobileUxTests(unittest.TestCase):
    def test_chat_shortcuts_are_compact_and_preserve_functionality(self):
        self.assertIn('shortcut(host, "预览"', ENTRY)
        self.assertIn('shortcut(host, "文件 / 工具"', ENTRY)
        self.assertIn('open(host, null)', ENTRY)
        self.assertIn('tools(host)', ENTRY)
        self.assertNotIn('bar.addView(button(host, "预览网页"', ENTRY)
        self.assertIn('b.setMinHeight(Math.round(44 * density))', ENTRY)
        self.assertIn('b.setTextSize(14)', ENTRY)
        self.assertIn('b.setSingleLine(false)', ENTRY)
        self.assertIn('b.setMaxLines(2)', ENTRY)
        self.assertIn('column.addView(page, new LinearLayout.LayoutParams(-1, 0, 1))', ENTRY)

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
