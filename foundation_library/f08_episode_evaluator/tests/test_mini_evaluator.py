"""Day 8 测试：验证 success、截断、reset success 与非法动作。"""

import math
import unittest

from foundation_library.f08_episode_evaluator.code.mini_evaluator import (
    EpisodeContractError,
    FixtureLineWorld,
    ProportionalFixturePolicy,
    run_episode,
)


class NaNPolicy:
    """用于验证环境拒绝非有限动作的 fixture 策略。"""

    def act(self, observation: object) -> float:
        return math.nan


class MiniEvaluatorTests(unittest.TestCase):
    def test_policy_reaches_target_and_terminates(self) -> None:
        environment = FixtureLineWorld(target=1.0, tolerance=0.05, max_action=0.25)
        records, success, reason = run_episode(
            "fixture_success", environment, ProportionalFixturePolicy(1.0), 0.0, 6
        )
        self.assertTrue(success)
        self.assertEqual(reason, "success")
        self.assertEqual(len(records), 4)
        self.assertTrue(records[-1].terminated)

    def test_zero_gain_is_valid_episode_failure_with_truncation(self) -> None:
        environment = FixtureLineWorld(target=1.0, tolerance=0.05, max_action=0.25)
        records, success, reason = run_episode(
            "fixture_truncated", environment, ProportionalFixturePolicy(0.0), 0.0, 3
        )
        self.assertFalse(success)
        self.assertEqual(reason, "max_steps")
        self.assertTrue(records[-1].truncated)

    def test_start_at_goal_succeeds_without_fake_step(self) -> None:
        environment = FixtureLineWorld(target=1.0, tolerance=0.05, max_action=0.25)
        records, success, reason = run_episode(
            "fixture_reset_success", environment, ProportionalFixturePolicy(1.0), 1.0, 3
        )
        self.assertTrue(success)
        self.assertEqual(records, [])
        self.assertEqual(reason, "success_at_reset")

    def test_nan_action_is_infrastructure_error(self) -> None:
        environment = FixtureLineWorld(target=1.0, tolerance=0.05, max_action=0.25)
        with self.assertRaisesRegex(EpisodeContractError, "有限数"):
            run_episode("fixture_nan", environment, NaNPolicy(), 0.0, 3)


if __name__ == "__main__":
    unittest.main()
