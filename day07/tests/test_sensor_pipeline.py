"""Day 7 测试：检查 shape、dtype、归一化和动作尺度。"""

import unittest

import numpy as np

from day07.code.sensor_pipeline import (
    ArrayContractError,
    build_fixture_action,
    build_fixture_observation,
    normalize_image,
    validate_action,
    validate_observation,
)


class SensorPipelineTests(unittest.TestCase):
    def test_observation_shapes_and_dtypes(self) -> None:
        observation = build_fixture_observation(4, 6)
        validate_observation(observation)
        self.assertEqual(observation.image.shape, (4, 6, 3))
        self.assertEqual(observation.image.dtype, np.uint8)
        self.assertEqual(observation.state.shape, (4,))

    def test_normalization_returns_float32_in_unit_interval(self) -> None:
        image = build_fixture_observation(3, 5).image
        normalized = normalize_image(image)
        self.assertEqual(normalized.dtype, np.float32)
        self.assertGreaterEqual(float(normalized.min()), 0.0)
        self.assertLessEqual(float(normalized.max()), 1.0)

    def test_action_scale_does_not_change_gripper(self) -> None:
        action = build_fixture_action(2.0)
        validate_action(action)
        self.assertAlmostEqual(float(action[0]), 0.02, places=6)
        self.assertAlmostEqual(float(action[-1]), 1.0, places=6)

    def test_wrong_action_shape_is_rejected(self) -> None:
        wrong = np.zeros(6, dtype=np.float32)
        with self.assertRaisesRegex(ArrayContractError, r"\(7,\)"):
            validate_action(wrong)


if __name__ == "__main__":
    unittest.main()
