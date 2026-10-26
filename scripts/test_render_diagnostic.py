"""Source-contract tests for the WishCode renderer timeout diagnostics overlay.

The real upstream source is SHA-verified at build time. This script patches only
exactly matching Java anchors and never changes the trial acceptance condition.
"""
from pathlib import Path
import tempfile
import unittest

import instrument_runtime_trial as diag

ROOT = Path(__file__).resolve().parent


class RenderDiagnosticsTests(unittest.TestCase):
    def test_fail_closed_if_source_anchor_changes(self):
        with self.assertRaisesRegex(ValueError, "anchor drift"):
            diag.patch_trial("class RuntimeTrial {}")
        with self.assertRaisesRegex(ValueError, "anchor drift"):
            diag.patch_browser("class RuntimeBrowserProbe {}")

    def test_readiness_requirements_not_changed_by_overlay(self):
        source = (ROOT / "instrument_runtime_trial.py").read_text(encoding="utf-8")
        self.assertIn('renderTrace.put("statusSeen"', source)
        self.assertIn('renderTrace.put("statusRendererTrue"', source)
        self.assertIn('renderTrace.put("browserAttached"', source)
        self.assertIn('detail.put("renderTrace", renderTrace)', source)
        self.assertIn('TRIAL_BROWSER_COOKIE_REJECTED', source)
        self.assertIn('TRIAL_BROWSER_MAINFRAME_NETWORK_ERROR', source)
        self.assertIn('TRIAL_BROWSER_MAINFRAME_HTTP_ERROR', source)
        self.assertIn('onRenderProcessGone', source)
        # Instrumented trial must not replace the actual success gate or
        # force the renderer true. The script intentionally lacks a complete
        # replacement of the upstream renderer condition.
        self.assertNotIn('return true; // skip renderer', source)
        self.assertNotIn('Boolean.TRUE.equals(status.get("renderer")) {', source)
        self.assertNotIn('setJavaScriptEnabled(false)', source)
        self.assertNotIn('SameSite=None', source)

    def test_only_two_native_java_files_are_scoped(self):
        self.assertEqual(
            diag.TRIAL, "app/src/main/java/com/deepseekharness/app/runtime/RuntimeTrial.java")
        self.assertEqual(
            diag.BROWSER, "app/src/main/java/com/deepseekharness/app/ui/RuntimeBrowserProbe.java")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "missing strict renderer probe source"):
                diag.apply(Path(directory))

    def test_workflow_is_manual_only_and_runs_instrumentation_before_gradle(self):
        workflow = (ROOT.parent / ".github/workflows/build-custom-apk.yml").read_text()
        self.assertIn("instrument_runtime_trial.py", workflow)
        self.assertLess(workflow.index("instrument_runtime_trial.py"),
                        workflow.index("Compile real Standard Debug APK"))
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("\n  schedule:", workflow)


if __name__ == "__main__":
    unittest.main()
