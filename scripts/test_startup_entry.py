"""Contract for one-tap launcher-to-chat handoff. Device state remains untested."""
import tempfile
import unittest
from pathlib import Path
from test_customize import fixture, patch, HOME


class StartupEntryTests(unittest.TestCase):
    def test_launcher_redirects_only_on_explicit_launcher_entry(self):
        self.assertIn('Intent.ACTION_MAIN.equals(getIntent().getAction())', HOME)
        self.assertIn('getIntent().hasCategory(Intent.CATEGORY_LAUNCHER)', HOME)
        self.assertIn('!getIntent().getBooleanExtra("wishcode_show_home", false)', HOME)
        self.assertIn('.putExtra("open_web", true)', HOME)
        self.assertIn('.putExtra("wishcode_auto_start_web", true)', HOME)
        self.assertIn('finish();\n      return;', HOME)
        self.assertIn('BrowserTasks.resumeBackground(this, true)', HOME)
        self.assertLess(HOME.index('BrowserTasks.resumeBackground(this, true)'),
                        HOME.index('startActivity(new Intent(this, MainActivity.class)'))
        self.assertIn('public final class WishCodeHomeActivity', HOME)
        self.assertIn('action(content, "诊断与日志"', HOME)

    def test_upstream_main_routes_explicit_auto_start_to_launch_fragment(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture(root)
            patch.modify(root, HOME)
            main = (root / "app/src/main/java/com/deepseekharness/app/ui/MainActivity.java").read_text()
            self.assertIn('private boolean pendingWishcodeAutoStart;', main)
            self.assertIn('intent.getBooleanExtra("wishcode_auto_start_web", false)', main)
            self.assertIn('args.putBoolean("wishcode_auto_start_web", pendingWishcodeAutoStart)', main)
            self.assertIn('requestAutoEnterWeb(pendingWishcodeAutoStart)', main)
            self.assertIn('WishCodeHomeActivity.class).putExtra("wishcode_show_home", true)', main)
            self.assertIn('startActivity(new Intent(this, OnboardingPrepareActivity.class))', main)

    def test_single_protected_start_with_fail_closed_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture(root)
            patch.modify(root, HOME)
            launch = (root / "app/src/main/java/com/deepseekharness/app/ui/LaunchFragment.java").read_text()
            for required in [
                'private boolean pendingWishcodeStart;',
                'getArguments().getBoolean("wishcode_auto_start_web", false)',
                'requestAutoEnterWeb(boolean autoStart)',
                'pendingWishcodeStart = false;',
                '!controller.isStarting() && !controller.isStopping()',
                '!controller.isRestoringWebSession()',
                '!controller.hasUnresolvedWebSession()',
                'controller.canAutoRestart()',
                '!com.deepseekharness.app.core.EnvironmentAccess.needsRecovery(controller)',
                '!controller.config().isStartupRecoveryRequested()',
                'doStart(requireActivity()',
                'pendingAutoEnter && !webEntryUrl().isEmpty()',
                'FirstRunWebStart.enqueueVisible(',
                'void requestAutoEnterWeb() { requestAutoEnterWeb(false); }',
            ]:
                self.assertIn(required, launch)
            self.assertIn('pendingWishcodeStart = false;\n          preparingStart = false;', launch)
            self.assertIn('pendingAutoEnter = false;\n    pendingWishcodeStart = false;', launch)
            # canAutoRestart() includes the persisted Web STOP_SENTINEL check.\n            self.assertNotIn('!controller.isUserStopped()\\n', launch)\n            self.assertNotIn('timer.schedule(', launch)
            self.assertNotIn('Thread.sleep(', launch)


if __name__ == "__main__":
    unittest.main()
