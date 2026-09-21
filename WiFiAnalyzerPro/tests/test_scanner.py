"""
WiFi Analyzer Pro - Scanner Subprocess & Execution Tests
Verifies silent subprocess flags and execution safety.
"""

import unittest
from app.utils.subprocess_utils import get_silent_subprocess_flags, run_hidden_command
from app.scanner import WiFiScanner


class TestScanner(unittest.TestCase):

    def test_subprocess_flags(self):
        startupinfo, creationflags = get_silent_subprocess_flags()
        # Verify function executes without exceptions on any OS
        self.assertIsInstance(creationflags, int)

    def test_run_hidden_command_echo(self):
        # Run a safe benign command to verify hidden runner
        code, stdout, stderr = run_hidden_command(["python3", "-c", "print('SilentExecutionOK')"])
        self.assertEqual(code, 0)
        self.assertIn("SilentExecutionOK", stdout)
        self.assertEqual(stderr, "")

    def test_demo_mode_scanner(self):
        scanner = WiFiScanner(demo_mode=True)
        self.assertTrue(scanner.demo_mode)
        res = scanner.scan()
        self.assertTrue(res.success)
        self.assertGreater(res.count, 5)
        self.assertGreater(res.count_24ghz, 0)
        self.assertGreater(res.count_5ghz, 0)
        self.assertIsNotNone(res.strongest_network)


if __name__ == "__main__":
    unittest.main()
