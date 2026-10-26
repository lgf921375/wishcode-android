"""Static and fail-closed regression for the pinned Android Lexical-input overlay."""
import tempfile
from pathlib import Path
import unittest
import patch_lexical_input as m

HERE=Path(__file__).resolve().parent

class LexicalInputOverlayTests(unittest.TestCase):
    def test_bad_anchors_refuse_to_patch(self):
        for fn in (m.native,m.browser,m.client):
            with self.assertRaisesRegex(ValueError,"PINNED_SOURCE_ANCHOR_DRIFT"):
                fn("placeholder")

    def test_patch_preserves_screen_authorization_and_non_composer_fallback(self):
        code=(HERE/"patch_lexical_input.py").read_text(encoding="utf-8")
        self.assertIn('context.claimDispatch()',code)
        self.assertIn('context.target().packageName',code)
        self.assertIn('BuildConfig.APPLICATION_ID',code)
        self.assertIn('if (lexical != null) return lexical;',code)
        self.assertIn('return semanticOutcome(context, target.performAction(action, bundle), action);',code)
        self.assertIn('grant.current()',code)
        self.assertIn('done.getCount() != 0',code)
        self.assertIn('owner.wishcodeTypingCurrent()',code)
        self.assertIn("document.activeElement.matches(",code)
        self.assertIn("shell.actions.captureInsertion()",code)
        self.assertIn("shell.actions.insertText(value, span)",code)
        self.assertIn('after.draftRev !== before.draftRev',code)
        self.assertIn("effectVerified",code)
        self.assertNotIn('innerHTML=',code)
        self.assertNotIn('textContent=value',code)
        self.assertNotIn("window.eval(",code)
        self.assertNotIn("execSync(",code)

    def test_integration_strict_one_anchor_each(self):
        src=[
            "        if (!context.claimDispatch()) return ScreenReply.refused(\"SCREEN_RUN_CHANGED\");\n"
            "        return semanticOutcome(context, target.performAction(action, bundle), action);",
            "  private boolean browserResumed;\n"
            "  protected void onResume() {\n    super.onResume();\n    browserResumed = true;\n"
            "  protected void onPause() {\n    WebFullscreenUi.cancelIme(this);\n    browserResumed = false;",
            "  function apply(ctx) {\n"
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for rel,body in zip((m.NATIVE,m.WEB,m.CLIENT),(src[0],src[1],src[2])):
                path=root/rel
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(body,encoding="utf-8")
            report=m.apply(root)
            self.assertEqual(len(report["patches"]),3)
            self.assertTrue(report["authorizedOnly"])
            self.assertFalse(report["phoneVerified"])
            self.assertIn("LEXICAL_INPUT_VERIFIED",(root/m.WEB).read_text())
            self.assertIn("insertText(value, span)",(root/m.CLIENT).read_text())
            with self.assertRaisesRegex(ValueError,"PINNED_SOURCE_ANCHOR_DRIFT"):
                m.apply(root)

    def test_workflow_manual_and_patch_before_gradle(self):
        wf=(HERE.parent/".github/workflows/build-custom-apk.yml").read_text()
        self.assertIn("workflow_dispatch:",wf)
        self.assertNotIn("\n  push:",wf)
        self.assertNotIn("\n  schedule:",wf)
        self.assertIn("patch_lexical_input.py",wf)
        self.assertLess(wf.index("patch_lexical_input.py"),wf.index("Compile real Standard Debug APK"))

if __name__=="__main__":unittest.main()
