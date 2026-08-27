"""Day 10 测试：验证三种梯度、累积与错误输入。"""

import unittest

import torch

from day10.code.autograd_lab import (
    GradientCheckError,
    build_report,
    demonstrate_accumulation,
    quadratic_loss,
)


class AutogradLabTests(unittest.TestCase):
    def test_three_gradient_methods_match(self) -> None:
        parameters = torch.tensor([3.0, -1.0, 0.5], dtype=torch.float64)
        targets = torch.tensor([1.0, 2.0, -0.5], dtype=torch.float64)
        report = build_report(parameters, targets, epsilon=1e-5, tolerance=1e-8)
        self.assertTrue(report["passed"])
        self.assertLess(report["finite_difference_max_error"], 1e-8)

    def test_gradient_accumulates_until_cleared(self) -> None:
        first, accumulated, cleared = demonstrate_accumulation(3.0)
        self.assertEqual(first, 6.0)
        self.assertEqual(accumulated, 12.0)
        self.assertEqual(cleared, 0.0)

    def test_shape_mismatch_is_rejected(self) -> None:
        parameters = torch.zeros(2, dtype=torch.float64)
        targets = torch.zeros(3, dtype=torch.float64)
        with self.assertRaisesRegex(GradientCheckError, "shape"):
            quadratic_loss(parameters, targets)

    def test_non_floating_parameters_are_rejected(self) -> None:
        parameters = torch.tensor([1, 2], dtype=torch.int64)
        targets = torch.tensor([1, 2], dtype=torch.int64)
        with self.assertRaisesRegex(GradientCheckError, "浮点"):
            quadratic_loss(parameters, targets)


if __name__ == "__main__":
    unittest.main()
