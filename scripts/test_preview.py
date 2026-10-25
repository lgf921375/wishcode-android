"""真实 Java URL/HTTP 测试 + 隔离配置契约；不是 Android 编译证明。"""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class PreviewTests(unittest.TestCase):
    def test_java_policy_and_http(self):
        with tempfile.TemporaryDirectory() as out:
            subprocess.run(['java', 'com.sun.tools.javac.Main', '-d', out,
                str(ROOT / 'scripts/WishCodePreviewPolicy.java'),
                str(ROOT / 'scripts/WishCodePreviewHttp.java'),
                str(ROOT / 'tests/java/WishCodePreviewTest.java')], check=True)
            subprocess.run(['java', '-cp', out, 'WishCodePreviewTest'], check=True)

    def test_java_ui_syntax(self):
        with tempfile.TemporaryDirectory() as out:
            subprocess.run(['java', 'com.sun.tools.javac.Main', '-d', out,
                str(ROOT / 'tests/java/ParseJavaSources.java')], check=True)
            sources = sorted(str(p) for p in (ROOT / 'scripts').glob('WishCode*.java'))
            subprocess.run(['java', '-cp', out, 'ParseJavaSources', *sources], check=True)

    def test_no_native_bridge_and_restricted_webview(self):
        source = (ROOT / 'scripts/WishCodePreviewActivity.java').read_text()
        for forbidden in ['addJavascriptInterface(', 'getCookie(', 'setCookie(', 'WebPageScripts.', 'PreviewAuth']:
            self.assertNotIn(forbidden, source)
        for required in ['setAllowFileAccess(false)', 'setAllowContentAccess(false)',
                         'setAllowUniversalAccessFromFileURLs(false)', 'setAcceptCookie(false)',
                         'setBlockNetworkLoads(true)', 'setSafeBrowsingEnabled(true)',
                         'request.deny()', 'Content-Security-Policy', 'onRenderProcessGone']:
            self.assertIn(required, source)
        patch = (ROOT / 'scripts/customize.py').read_text()
        # Historical preview sources remain in Git for audit, but none may be
        # injected into the new APK or intercept the upstream browser.
        self.assertNotIn('android:process=":wishcode_preview"', patch)
        self.assertNotIn("WishCodePreviewActivity", patch)
        self.assertNotIn("WishCodePreviewEntry", patch)
        self.assertNotIn("WishCodePreviewPolicy", patch)
        self.assertNotIn("WebPreviewActivity.java", patch)
        self.assertIn('android:name=".ui.MainActivity"', patch)
        self.assertIn('setDataDirectorySuffix', patch)

if __name__ == '__main__':
    unittest.main()
