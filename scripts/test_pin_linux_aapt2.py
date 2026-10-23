"""Fail-closed AAPT2 Gradle verification metadata contract tests."""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pin_linux_aapt2", HERE / "pin_linux_aapt2.py")
pin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pin)

SAMPLE = '''<?xml version="1.0" encoding="UTF-8"?>
<verification-metadata xmlns="https://schema.gradle.org/dependency-verification">
<components>
''' + pin.OLD + '''
           <sha256 value="7892b466ff80a9e5e11f976e2defad6de0d4062c77c533939fb75ed91ba174b5"/>
         </artifact>
      </component>
</components>
</verification-metadata>
'''


class TestPinLinuxAapt2(unittest.TestCase):
    def test_supplement_only_linux_pin(self):
        output = pin.patch(SAMPLE)
        self.assertEqual(output.count(pin.LINUX_SHA), 1)
        self.assertEqual(output.count(pin.WINDOWS_SHA), 1)
        self.assertEqual(len(output), len(SAMPLE) + len(pin.NEW) - len(pin.OLD))
        self.assertIn('linux.jar', output)

    def test_reapply_must_fail(self):
        with self.assertRaises(ValueError):
            pin.patch(pin.patch(SAMPLE))

    def test_version_drift_stops(self):
        with self.assertRaises(ValueError):
            pin.patch(SAMPLE.replace(pin.VERSION, "9.1.1-UNEXPECTED"))

    def test_windows_hash_drift_stops(self):
        with self.assertRaises(ValueError):
            pin.patch(SAMPLE.replace(pin.WINDOWS_SHA, "0"*64))

    def test_duplicate_component_stops(self):
        with self.assertRaises(ValueError):
            pin.patch(SAMPLE.replace("</components>", pin.OLD + "</components>"))

    def test_no_verification_disable(self):
        source = (HERE / "pin_linux_aapt2.py").read_text()
        self.assertNotIn("--dependency-verification off", source.replace(
            "never Gradle --dependency-verification off", ""))
        self.assertIn("ET.fromstring", source)


if __name__ == "__main__":
    unittest.main()
