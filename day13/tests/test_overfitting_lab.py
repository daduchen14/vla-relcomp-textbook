"""Day 13 测试：划分、更新次数、评估模式和摘要。"""

import unittest

import torch
from torch import nn

from day13.code.overfitting_lab import (
    FixtureMLP,
    make_fixture_splits,
    make_loader,
    summarize,
    train,
)


class OverfittingLabTests(unittest.TestCase):
    def test_splits_have_expected_shapes(self) -> None:
        train_set, validation_set = make_fixture_splits(7)
        self.assertEqual(tuple(train_set.tensors[0].shape), (16, 1))
        self.assertEqual(tuple(validation_set.tensors[0].shape), (121, 1))

    def test_optimizer_step_count_matches_batches_times_epochs(self) -> None:
        torch.manual_seed(7)
        train_set, validation_set = make_fixture_splits(7)
        loader = make_loader(train_set, batch_size=4, seed=7)
        history = train(FixtureMLP(8), loader, validation_set, 0.01, epochs=3)
        self.assertEqual(history[-1].optimizer_steps, 12)

    def test_evaluation_leaves_model_in_eval_mode(self) -> None:
        torch.manual_seed(7)
        train_set, validation_set = make_fixture_splits(7)
        loader = make_loader(train_set, 4, 7)
        model = FixtureMLP(8)
        train(model, loader, validation_set, 0.01, epochs=1)
        self.assertFalse(model.training)

    def test_summary_uses_lowest_validation_epoch(self) -> None:
        from day13.code.overfitting_lab import EpochRecord

        history = [
            EpochRecord(0, 2.0, 3.0, 1),
            EpochRecord(1, 1.0, 1.0, 2),
            EpochRecord(2, 0.5, 2.0, 3),
        ]
        report = summarize(history)
        self.assertEqual(report["best_epoch"], 1)
        self.assertTrue(report["overfitting_signal"])


if __name__ == "__main__":
    unittest.main()
