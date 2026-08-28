"""Day 19 免费 CPU 测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from mainline.day19.code.build_l1_registry import derive

ROOT = Path(__file__).resolve().parents[3]
L0 = ROOT / "shared/fixtures/day18_l0_spec_a.json"
L1 = ROOT / "shared/fixtures/day19_l1_spec_a.json"


def table(root: Path) -> Path:
    tasks = [{"level": 1, "task_id": i, "task_name": f"t{i}", "bddl_path": f"t{i}.bddl",
              "target_object": f"x{i}", "reference_object": f"y{i}", "goal_relation": "On"} for i in range(5)]
    path = root/"table.json"; path.write_text(json.dumps({"commit": "babe582ebffc82b979b77964a7e56417d02f63a4",
        "suite": "extrapolation_preposition_combinations", "tasks": tasks})); return path


class Day19Tests(unittest.TestCase):
    def test_valid_l1_has_five_tasks(self):
        with tempfile.TemporaryDirectory() as tmp: rows, guard = derive(table(Path(tmp)), L0, L1)
        self.assertEqual(len(rows), 10); self.assertEqual(guard["changed_frozen_fields"], [])

    def changed(self, tmp, key, value):
        data = json.loads(L1.read_text()); data[key] = value; path = Path(tmp)/"l1.json"; path.write_text(json.dumps(data)); return path

    def test_model_revision_drift_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): derive(table(Path(tmp)), L0, self.changed(tmp, "model_revision", "new"))

    def test_threshold_or_result_field_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): derive(table(Path(tmp)), L0, self.changed(tmp, "score", 0.9))

    def test_selection_use_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): derive(table(Path(tmp)), L0, self.changed(tmp, "heldout_use", "select_checkpoint"))

    def test_seed_drift_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): derive(table(Path(tmp)), L0, self.changed(tmp, "seed_base", 999))


if __name__ == "__main__": unittest.main()
