"""Day 18 测试：block shape、mask、梯度、训练和错误配置。"""

import unittest

import torch

from foundation_library.f18_transformer_block.code.transformer_lab import (
    TransformerBlock,
    TransformerContractError,
    make_fixture_batch,
    run_experiment,
)


class TransformerLabTests(unittest.TestCase):
    def test_block_preserves_shape_and_zeroes_padding(self) -> None:
        batch = make_fixture_batch(8, 18)
        output = TransformerBlock(8, 16)(batch.vectors, batch.valid_mask)
        self.assertEqual(output.shape, batch.vectors.shape)
        self.assertEqual(float(output[~batch.valid_mask].abs().sum().item()), 0.0)

    def test_gradients_reach_attention_and_feed_forward(self) -> None:
        batch = make_fixture_batch(8, 18)
        block = TransformerBlock(8, 16)
        block(batch.vectors, batch.valid_mask).sum().backward()
        self.assertIsNotNone(block.attention.query.weight.grad)
        self.assertIsNotNone(block.feed_forward[0].weight.grad)

    def test_dropout_range_is_checked(self) -> None:
        with self.assertRaisesRegex(TransformerContractError, "dropout"):
            TransformerBlock(8, 16, dropout=1.0)

    def test_mask_dtype_is_checked(self) -> None:
        with self.assertRaisesRegex(TransformerContractError, "bool"):
            TransformerBlock(8, 16)(torch.zeros(1, 2, 8), torch.ones(1, 2))

    def test_training_reduces_fixture_loss(self) -> None:
        report = run_experiment(32, 80, 0.03, 32, 0.0, 18)
        self.assertLess(report["final_loss"], report["first_loss"])
        self.assertGreaterEqual(report["training_accuracy"], 0.95)

    def test_same_seed_reproduces_summary(self) -> None:
        first = run_experiment(16, 5, 0.03, 16, 0.0, 18)
        second = run_experiment(16, 5, 0.03, 16, 0.0, 18)
        self.assertEqual(first["final_loss"], second["final_loss"])
        self.assertEqual(first["training_accuracy"], second["training_accuracy"])


if __name__ == "__main__":
    unittest.main()
