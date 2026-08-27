"""Day 17 测试：覆盖 shape、归一化、mask、梯度和错误输入。"""

import unittest

import torch

from day17.code.attention_lab import (
    AttentionContractError,
    SingleHeadSelfAttention,
    make_fixture_batch,
    run_experiment,
)


class AttentionLabTests(unittest.TestCase):
    def test_output_and_weight_shapes(self) -> None:
        vectors, mask, _, _ = make_fixture_batch()
        result = SingleHeadSelfAttention(8)(vectors, mask)
        self.assertEqual(tuple(result.output.shape), (2, 4, 8))
        self.assertEqual(tuple(result.weights.shape), (2, 4, 4))

    def test_valid_attention_rows_sum_to_one(self) -> None:
        vectors, mask, _, _ = make_fixture_batch()
        weights = SingleHeadSelfAttention(8)(vectors, mask).weights
        self.assertTrue(torch.allclose(weights[mask].sum(-1), torch.ones(7), atol=1e-6))

    def test_padding_key_and_query_are_zeroed(self) -> None:
        vectors, mask, _, _ = make_fixture_batch()
        result = SingleHeadSelfAttention(8)(vectors, mask)
        self.assertEqual(float(result.weights[1, :, 3].abs().max().item()), 0.0)
        self.assertEqual(float(result.weights[1, 3].abs().sum().item()), 0.0)
        self.assertEqual(float(result.output[1, 3].abs().sum().item()), 0.0)

    def test_gradients_reach_input_and_projection(self) -> None:
        vectors, mask, _, _ = make_fixture_batch()
        vectors.requires_grad_()
        module = SingleHeadSelfAttention(8)
        module(vectors, mask).output.sum().backward()
        self.assertIsNotNone(vectors.grad)
        self.assertIsNotNone(module.query.weight.grad)

    def test_all_padding_sequence_is_rejected(self) -> None:
        vectors = torch.zeros((1, 2, 4))
        mask = torch.zeros((1, 2), dtype=torch.bool)
        with self.assertRaisesRegex(AttentionContractError, "至少需要一个"):
            SingleHeadSelfAttention(4)(vectors, mask)

    def test_same_seed_reproduces_weights(self) -> None:
        first = run_experiment(17, 1.0)
        second = run_experiment(17, 1.0)
        self.assertEqual(first["first_sequence_weights"], second["first_sequence_weights"])


if __name__ == "__main__":
    unittest.main()
