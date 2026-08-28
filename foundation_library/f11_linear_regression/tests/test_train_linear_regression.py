"""Day 11 测试：验证数据重复性、收敛、闭式解和错误参数。"""

import unittest

import torch

from foundation_library.f11_linear_regression.code.train_linear_regression import (
    TrainingContractError,
    closed_form_solution,
    make_fixture_data,
    train,
)


class LinearRegressionTests(unittest.TestCase):
    def test_fixture_data_repeats_with_same_seed(self) -> None:
        x1, y1 = make_fixture_data(0.1, 7)
        x2, y2 = make_fixture_data(0.1, 7)
        self.assertTrue(torch.equal(x1, x2))
        self.assertTrue(torch.equal(y1, y2))

    def test_gradient_descent_converges_near_closed_form(self) -> None:
        features, targets = make_fixture_data(0.1, 7)
        weight, bias, history = train(features, targets, 0.1, 100)
        closed_weight, closed_bias = closed_form_solution(features, targets)
        self.assertLess(history[-1].loss, history[0].loss)
        self.assertAlmostEqual(float(weight), closed_weight, places=4)
        self.assertAlmostEqual(float(bias), closed_bias, places=4)

    def test_zero_noise_recovers_known_line(self) -> None:
        features, targets = make_fixture_data(0.0, 7)
        weight, bias, _ = train(features, targets, 0.1, 100)
        self.assertAlmostEqual(float(weight), 2.0, places=4)
        self.assertAlmostEqual(float(bias), 1.0, places=4)

    def test_non_positive_learning_rate_is_rejected(self) -> None:
        features, targets = make_fixture_data(0.0, 7)
        with self.assertRaisesRegex(TrainingContractError, "learning_rate"):
            train(features, targets, 0.0, 10)


if __name__ == "__main__":
    unittest.main()
