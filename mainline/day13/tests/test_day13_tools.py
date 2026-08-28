"""Day 13 免费 CPU 测试。"""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from mainline.day13.code.build_pair_manifest import FIELDS, build, write_csv
from mainline.day13.code.validate_pair_manifest import read_rows, validate


def inputs(root: Path) -> tuple[Path, Path]:
    task = {"level": 0, "task_id": 0, "task_name": "task", "bddl_path": "task.bddl",
            "language": "Put tomato on bowl", "target_object": "tomato", "reference_object": "bowl",
            "goal_relation": "On", "goal_predicate": ["On", "tomato", "bowl"]}
    table = root / "table.json"; table.write_text(json.dumps({"suite": "suite", "tasks": [task]}))
    spec = root / "spec.json"; spec.write_text(json.dumps({"pair_name": "p", "factor": "instruction_surface",
        "task_selector": {"level": 0, "task_id": 0}, "instruction_b": "Place tomato atop bowl",
        "model_id": "m", "model_revision": "r", "seed": 7, "init_state_index": 2,
        "inference_config_sha256": "a" * 64, "order_seed": 9, "source_kind": "planned"}))
    return table, spec


class Day13ToolTests(unittest.TestCase):
    def test_build_and_validate_only_instruction_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            table, spec = inputs(Path(tmp)); manifest = Path(tmp) / "pair.csv"
            write_csv(build(table, spec), manifest); report = validate(manifest, table)
        self.assertEqual(report["changed_fields"], ["instruction_text"])
        self.assertEqual(report["semantic_equivalence_review"], "pending_human_review")

    def test_same_instruction_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            table, spec = inputs(Path(tmp)); data = json.loads(spec.read_text())
            data["instruction_b"] = "put TOMATO on BOWL"; spec.write_text(json.dumps(data))
            with self.assertRaises(ValueError): build(table, spec)

    def test_different_init_state_breaks_matching(self):
        with tempfile.TemporaryDirectory() as tmp:
            table, spec = inputs(Path(tmp)); manifest = Path(tmp) / "pair.csv"; write_csv(build(table, spec), manifest)
            rows = read_rows(manifest); rows[1]["init_state_index"] = "3"
            with manifest.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
            with self.assertRaises(ValueError): validate(manifest, table)

    def test_tampered_pair_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            table, spec = inputs(Path(tmp)); manifest = Path(tmp) / "pair.csv"; write_csv(build(table, spec), manifest)
            rows = read_rows(manifest)
            for row in rows: row["pair_id"] = "pair-tampered"
            with manifest.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS); writer.writeheader(); writer.writerows(rows)
            with self.assertRaises(ValueError): validate(manifest, table)

    def test_csv_row_order_does_not_define_arm(self):
        with tempfile.TemporaryDirectory() as tmp:
            table, spec = inputs(Path(tmp)); manifest = Path(tmp) / "pair.csv"; rows = build(table, spec)
            write_csv(list(reversed(rows)), manifest); report = validate(manifest, table)
        self.assertTrue(report["pair_id"].startswith("pair-"))


if __name__ == "__main__": unittest.main()
