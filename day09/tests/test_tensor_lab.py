"""Day 9 测试：验证 batch、布局、dtype 与设备拒绝路径。"""

import unittest

import torch

from day09.code.tensor_lab import (
    TensorContractError,
    build_fixture_batch,
    prepare_images,
    select_device,
    validate_batch,
)


class TensorLabTests(unittest.TestCase):
    def test_batch_shapes_and_dtypes_on_cpu(self) -> None:
        batch = build_fixture_batch(3, torch.device("cpu"))
        validate_batch(batch)
        self.assertEqual(tuple(batch.images.shape), (3, 3, 4, 3))
        self.assertEqual(tuple(batch.states.shape), (3, 4))
        self.assertEqual(tuple(batch.actions.shape), (3, 7))

    def test_prepare_images_changes_layout_and_range(self) -> None:
        batch = build_fixture_batch(2, torch.device("cpu"))
        prepared = prepare_images(batch.images)
        self.assertEqual(tuple(prepared.shape), (2, 3, 3, 4))
        self.assertEqual(prepared.dtype, torch.float32)
        self.assertTrue(prepared.is_contiguous())
        self.assertGreaterEqual(float(prepared.min()), 0.0)
        self.assertLessEqual(float(prepared.max()), 1.0)

    def test_non_positive_batch_is_rejected(self) -> None:
        with self.assertRaisesRegex(TensorContractError, "正整数"):
            build_fixture_batch(0, torch.device("cpu"))

    def test_unavailable_cuda_is_rejected_in_cpu_environment(self) -> None:
        if torch.cuda.is_available():
            self.skipTest("当前环境实际有 CUDA；拒绝分支不适用")
        with self.assertRaisesRegex(TensorContractError, "cuda"):
            select_device("cuda")


if __name__ == "__main__":
    unittest.main()
