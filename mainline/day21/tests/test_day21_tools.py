"""Day 21 免费 CPU 测试。"""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from mainline.day21.code.analyze_reproducibility import analyze
from mainline.day21.code.build_rerun_manifest import FROZEN, build

ROOT = Path(__file__).resolve().parents[3]
A_RAW = ROOT / "shared/fixtures/day21_repro_results_a.csv"
B_RAW = ROOT / "shared/fixtures/day21_repro_results_b.csv"


def fixture(root: Path, selectors=None):
    registry = root / "registry.csv"
    fields = ("episode_id", "run_id", "level", "task_id", "trial_id", "seed", "init_state_index",
              "task_name", "bddl_path", "model_id", "model_revision", "protocol_lock_sha256")
    with registry.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for task_id in range(2):
            writer.writerow({"episode_id": f"ep{task_id}", "run_id": "run0", "level": 0,
                "task_id": task_id, "trial_id": 0, "seed": 10 + task_id, "init_state_index": 0,
                "task_name": f"task{task_id}", "bddl_path": f"task{task_id}.bddl", "model_id": "model",
                "model_revision": "rev", "protocol_lock_sha256": "a" * 64})
    selection = root / "selection.json"
    selection.write_text(json.dumps({"selection_name": "test", "selection_rule": "pre_registered_boundary_tasks_not_result_cherry_pick",
        "selectors": selectors if selectors is not None else [{"task_id": 0, "trial_id": 0}, {"task_id": 1, "trial_id": 0}],
        "source_kind": "synthetic_test"}), encoding="utf-8")
    return registry, selection


class Day21Tests(unittest.TestCase):
    def test_manifest_pairs_freeze_all_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = build(*fixture(Path(tmp)))
        self.assertEqual(len(rows), 4)
        for left, right in zip(rows[::2], rows[1::2]):
            self.assertEqual(left["replicate"], "original"); self.assertEqual(right["replicate"], "repeat")
            self.assertTrue(all(left[field] == right[field] for field in FROZEN))
            self.assertNotEqual(left["execution_id"], right["execution_id"])

    def test_duplicate_selector_rejected(self):
        selectors = [{"task_id": 0, "trial_id": 0}] * 2
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): build(*fixture(Path(tmp), selectors))

    def test_missing_selector_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): build(*fixture(Path(tmp), [{"task_id": 9, "trial_id": 0}]))

    def test_a_preserves_numerators(self):
        _, report = analyze(A_RAW)
        self.assertEqual(report["success_match"], {"numerator": 3, "denominator": 4, "rate": 0.75})
        self.assertEqual(report["exact_match"], {"numerator": 2, "denominator": 4, "rate": 0.5})

    def test_b_differs_and_invalid_bit_rejected(self):
        _, report = analyze(B_RAW); self.assertEqual(report["pair_count"], 3)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"; text = A_RAW.read_text(encoding="utf-8").replace("r1,1,1", "r1,2,1")
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError): analyze(path)


if __name__ == "__main__":
    unittest.main()
