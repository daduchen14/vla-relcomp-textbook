"""Day 14 免费 CPU 测试。"""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from mainline.day14.code.analyze_oracle_results import analyze
from mainline.day14.code.build_oracle_manifest import build

ROOT = Path(__file__).resolve().parents[3]
RESULTS_A = ROOT / "shared/fixtures/day14_oracle_results_a.csv"


class Day14ToolTests(unittest.TestCase):
    def test_recovery_and_damage_use_different_denominators(self):
        result = analyze(RESULTS_A)["success"]
        self.assertEqual((result["recovered_n"], result["control_failure_n"]), (2, 3))
        self.assertEqual((result["damaged_n"], result["control_success_n"]), (1, 2))

    def test_stage_metrics_preserve_raw_cells(self):
        result = analyze(RESULTS_A)
        self.assertEqual(sum(result["stages"]["target_lifted"]["cells_control_oracle"].values()), 5)

    def test_incomplete_pair_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines = RESULTS_A.read_text().splitlines(); path = Path(tmp) / "x.csv"
            path.write_text("\n".join(lines[:-1]) + "\n")
            with self.assertRaises(ValueError): analyze(path)

    def test_success_relation_disagreement_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines = RESULTS_A.read_text().replace("p1,oracle,1,1,1,1,1,1", "p1,oracle,1,1,1,1,1,0")
            path = Path(tmp) / "x.csv"; path.write_text(lines)
            with self.assertRaises(ValueError): analyze(path)

    def test_manifest_has_matched_control_oracle_and_privilege_label(self):
        table = ROOT / "shared/fixtures/day09_task_table_for_test_missing.json"
        # 用最小内存对象落到临时目录，避免测试依赖学习者输出。
        with tempfile.TemporaryDirectory() as tmp:
            import json
            task = {"level": 0, "task_id": 0, "task_name": "t", "bddl_path": "t.bddl",
                    "language": "original", "target_object": "x", "reference_object": "y",
                    "goal_relation": "On", "target_initial_predicate": ["On", "x", "region"]}
            table = Path(tmp) / "table.json"; table.write_text(json.dumps({"suite": "s", "tasks": [task]}))
            spec = Path(tmp) / "spec.json"; spec.write_text(json.dumps({"pilot_name": "p",
                "task_selector": {"level": 0, "task_id": 0}, "model_id": "m", "model_revision": "r",
                "inference_config_sha256": "a" * 64, "trials": [{"seed": 1, "init_state_index": 2}],
                "source_kind": "planned"}))
            rows = build(table, spec)
        self.assertEqual({row["arm"] for row in rows}, {"control", "oracle"})
        self.assertEqual({row["privileged_info_used"] for row in rows}, {"bddl_goal_and_init"})
        fixed = [key for key in rows[0] if key not in {"arm", "intervention", "instruction_text"}]
        self.assertTrue(all(rows[0][key] == rows[1][key] for key in fixed))


if __name__ == "__main__": unittest.main()
