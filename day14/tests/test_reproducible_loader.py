"""Day 14 测试：验证 ID、split、batch shape 与同 seed 顺序。"""

import unittest

from day14.code.reproducible_loader import (
    IndexedFixtureDataset,
    collect_loader_manifest,
    make_loader,
    make_splits,
)


class ReproducibleLoaderTests(unittest.TestCase):
    def test_dataset_returns_stable_fixture_id(self) -> None:
        sample = IndexedFixtureDataset(12)[3]
        self.assertEqual(sample["sample_id"], "fixture_sample_003")
        self.assertEqual(tuple(sample["feature"].shape), (1,))

    def test_splits_are_disjoint_and_complete(self) -> None:
        dataset = IndexedFixtureDataset(12)
        train_set, validation_set = make_splits(dataset, 3, 7)
        train_ids = {train_set[index]["sample_id"] for index in range(len(train_set))}
        validation_ids = {
            validation_set[index]["sample_id"] for index in range(len(validation_set))
        }
        self.assertFalse(train_ids & validation_ids)
        self.assertEqual(len(train_ids | validation_ids), 12)

    def test_same_seed_produces_same_shuffle_order(self) -> None:
        dataset = IndexedFixtureDataset(12)
        train_set, _ = make_splits(dataset, 3, 7)
        first = collect_loader_manifest(make_loader(train_set, 4, 7, 0, True), "train")
        second = collect_loader_manifest(make_loader(train_set, 4, 7, 0, True), "train")
        self.assertEqual(first["sample_order"], second["sample_order"])

    def test_last_batch_keeps_remaining_sample(self) -> None:
        dataset = IndexedFixtureDataset(10)
        loader = make_loader(dataset, batch_size=4, seed=7, num_workers=0, shuffle=False)
        manifest = collect_loader_manifest(loader, "all")
        self.assertEqual([len(batch["sample_ids"]) for batch in manifest["batches"]], [4, 4, 2])


if __name__ == "__main__":
    unittest.main()
