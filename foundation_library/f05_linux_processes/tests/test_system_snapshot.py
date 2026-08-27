"""Day 5 测试：验证探针三条通道与环境变量白名单。"""

import os
import unittest
from unittest.mock import patch

from foundation_library.f05_linux_processes.code.system_snapshot import make_probe, safe_environment


class SystemSnapshotTests(unittest.TestCase):
    def test_probe_keeps_stdout_stderr_and_returncode_separate(self) -> None:
        observation = make_probe(3)
        self.assertEqual(observation.stdout, "fixture_probe_stdout")
        self.assertEqual(observation.stderr, "fixture_probe_stderr")
        self.assertEqual(observation.returncode, 3)

    def test_environment_uses_allowlist_and_does_not_capture_secret(self) -> None:
        fixture_environment = {
            "LANG": "fixture_UTF-8",
            "SECRET_TOKEN": "fixture_must_not_be_saved",
        }
        with patch.dict(os.environ, fixture_environment, clear=True):
            captured = safe_environment()
        self.assertEqual(captured["LANG"], "fixture_UTF-8")
        self.assertNotIn("SECRET_TOKEN", captured)


if __name__ == "__main__":
    unittest.main()
