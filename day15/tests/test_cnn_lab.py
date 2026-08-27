"""Day 15 测试：覆盖数据契约、shape、训练与复现。"""

import unittest

import torch

from day15.code.cnn_lab import StripeDataset, TinyStripeCNN, run_experiment


class CnnLabTests(unittest.TestCase):
    def test_fixture_dataset_shape_and_ids(self) -> None:
        image, label, sample_id = StripeDataset(8, seed=15)[0]
        self.assertEqual(tuple(image.shape), (1, 8, 8))
        self.assertEqual(label.dtype, torch.int64)
        self.assertTrue(sample_id.startswith("fixture_"))

    def test_model_preserves_batch_and_outputs_two_logits(self) -> None:
        logits = TinyStripeCNN(channels=4)(torch.zeros((3, 1, 8, 8)))
        self.assertEqual(tuple(logits.shape), (3, 2))

    def test_wrong_image_shape_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "images 必须"):
            TinyStripeCNN()(torch.zeros((3, 8, 8)))

    def test_training_learns_fixture_task(self) -> None:
        report = run_experiment(40, 30, 0.2, 4, 15)
        self.assertLess(report["final_loss"], report["first_loss"])
        self.assertGreaterEqual(report["accuracy"], 0.95)

    def test_same_seed_reproduces_summary(self) -> None:
        first = run_experiment(16, 5, 0.2, 2, 15)
        second = run_experiment(16, 5, 0.2, 2, 15)
        self.assertEqual(first["final_loss"], second["final_loss"])
        self.assertEqual(first["predictions"], second["predictions"])


if __name__ == "__main__":
    unittest.main()
