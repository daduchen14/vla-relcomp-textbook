"""Day 20 免费 CPU 测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from mainline.day20.code.build_l2_registry import derive
from mainline.day20.code.classify_failures import classify

ROOT = Path(__file__).resolve().parents[3]
L0 = ROOT / "shared/fixtures/day18_l0_spec_a.json"; L2 = ROOT / "shared/fixtures/day20_l2_spec_a.json"
A = ROOT / "shared/fixtures/day20_failures_a.csv"; B = ROOT / "shared/fixtures/day20_failures_b.csv"


def table(root):
    tasks = [{"level": 2, "task_id": i, "task_name": f"t{i}", "bddl_path": f"t{i}.bddl",
              "target_object": f"x{i}", "reference_object": f"y{i}", "goal_relation": "On"} for i in range(5)]
    path = root/"table.json"; path.write_text(json.dumps({"commit": "babe582ebffc82b979b77964a7e56417d02f63a4",
        "suite": "extrapolation_preposition_combinations", "tasks": tasks})); return path


class Day20Tests(unittest.TestCase):
    def test_l2_plan_has_zero_drift(self):
        with tempfile.TemporaryDirectory() as tmp: rows, guard = derive(table(Path(tmp)), L0, L2)
        self.assertEqual(len(rows), 10); self.assertTrue(guard["strong_ood"])

    def test_a_covers_four_failure_stages(self):
        rows, _ = classify(A); labels = {row["failure_label"] for row in rows}
        self.assertTrue({"TARGET_CONTACT_FAILURE", "LIFT_FAILURE", "REFERENCE_APPROACH_FAILURE", "TERMINAL_RELATION_FAILURE"}.issubset(labels))

    def test_b_preserves_inconsistent_success_signal(self):
        rows, _ = classify(B); self.assertIn("INCONSISTENT_SUCCESS_SIGNAL", {row["failure_label"] for row in rows})

    def test_invalid_allows_missing_success(self):
        rows, _ = classify(A); self.assertEqual(rows[-1]["failure_label"], "ENV_INVALID")

    def test_model_drift_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(L2.read_text()); data["model_revision"] = "changed"; path = Path(tmp)/"l2.json"; path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): derive(table(Path(tmp)), L0, path)


if __name__ == "__main__": unittest.main()
