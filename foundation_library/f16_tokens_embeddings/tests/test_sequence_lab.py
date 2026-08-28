"""Day 16 测试：覆盖词表、补齐、未知字符、位置和复现。"""

import unittest

import torch

from foundation_library.f16_tokens_embeddings.code.sequence_lab import (
    CharacterVocabulary,
    SequenceContractError,
    SequenceEncoder,
    encode_batch,
    run_experiment,
    sinusoidal_positions,
)


class SequenceLabTests(unittest.TestCase):
    def test_vocabulary_is_deterministic_and_reserves_special_ids(self) -> None:
        first = CharacterVocabulary(["杯子", "拿杯"])
        second = CharacterVocabulary(["拿杯", "杯子"])
        self.assertEqual(first.token_to_id, second.token_to_id)
        self.assertEqual(first.token_to_id["<PAD>"], 0)
        self.assertEqual(first.token_to_id["<UNK>"], 1)

    def test_unknown_and_padding_are_distinct(self) -> None:
        vocabulary = CharacterVocabulary(["红杯"])
        ids, valid = vocabulary.encode("绿杯", 4)
        self.assertEqual(ids, [1, vocabulary.token_to_id["杯"], 0, 0])
        self.assertEqual(valid, [True, True, False, False])

    def test_overlong_text_is_not_silently_truncated(self) -> None:
        with self.assertRaisesRegex(SequenceContractError, "不静默截断"):
            CharacterVocabulary(["拿杯"]).encode("拿起杯子", 2)

    def test_position_table_shape_and_first_row(self) -> None:
        table = sinusoidal_positions(5, 8)
        self.assertEqual(tuple(table.shape), (5, 8))
        self.assertTrue(torch.equal(table[0, 0::2], torch.zeros(4)))
        self.assertTrue(torch.equal(table[0, 1::2], torch.ones(4)))

    def test_encoder_zeroes_padding_and_preserves_shape(self) -> None:
        vocabulary = CharacterVocabulary(["拿杯"])
        batch = encode_batch(vocabulary, ["拿", "拿杯"], 3)
        vectors = SequenceEncoder(len(vocabulary), 8, 3)(batch.token_ids, batch.valid_mask)
        self.assertEqual(tuple(vectors.shape), (2, 3, 8))
        self.assertEqual(float(vectors[~batch.valid_mask].abs().sum().item()), 0.0)

    def test_same_seed_reproduces_first_vector(self) -> None:
        first = run_experiment(12, 8, 16)
        second = run_experiment(12, 8, 16)
        self.assertEqual(first["first_vector"], second["first_vector"])


if __name__ == "__main__":
    unittest.main()
