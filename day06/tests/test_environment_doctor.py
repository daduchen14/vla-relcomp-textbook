"""Day 6 测试：验证标准库、可选缺失包和非法清单。"""

import unittest

from day06.code.environment_doctor import EnvironmentCheckError, build_report, inspect_requirement


class EnvironmentDoctorTests(unittest.TestCase):
    def test_required_standard_library_is_available(self) -> None:
        observation = inspect_requirement(
            {"module": "json", "distribution": None, "required": True, "reason": "fixture"}
        )
        self.assertTrue(observation.available)
        self.assertIsNone(observation.version)

    def test_missing_optional_module_does_not_block_readiness(self) -> None:
        manifest = {
            "requirements": [
                {
                    "module": "fixture_package_not_installed",
                    "distribution": "fixture-package-not-installed",
                    "required": False,
                    "reason": "fixture optional branch",
                }
            ]
        }
        report = build_report(manifest)
        self.assertTrue(report["ready"])
        self.assertEqual(report["missing_required"], [])

    def test_non_boolean_required_is_rejected(self) -> None:
        with self.assertRaisesRegex(EnvironmentCheckError, "布尔值"):
            inspect_requirement(
                {"module": "json", "distribution": None, "required": "yes", "reason": "fixture"}
            )


if __name__ == "__main__":
    unittest.main()
