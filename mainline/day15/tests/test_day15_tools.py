"""Day 15 免费 CPU 测试。"""

import tempfile
import unittest
from pathlib import Path

from mainline.day15.code.freeze_protocol import file_records, validate_spec


def base_spec():
    return {"lock_name": "x", "mode": "formal", "model_id": "m", "model_revision": "r",
        "suite": "extrapolation_preposition_combinations", "levels": [0, 1, 2], "trials_per_task": 5,
        "seed_policy": "seed+init", "success_field": "info.success", "invalid_episode_rule": "exclude env",
        "training_scope": "L0", "held_out_scope": "L1_L2_never_select", "evidence_required": ["video"],
        "files_to_hash": ["x"], "source_kind": "formal_baseline"}


class Day15Tests(unittest.TestCase):
    def test_formal_placeholder_rejected(self):
        spec = base_spec(); spec["model_revision"] = "fill_after_placeholder"
        with self.assertRaises(ValueError): validate_spec(spec)

    def test_wrong_success_field_rejected(self):
        spec = base_spec(); spec["success_field"] = "done"
        with self.assertRaises(ValueError): validate_spec(spec)

    def test_duplicate_files_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x"; path.write_text("x")
            with self.assertRaises(ValueError): file_records(Path(tmp), ["x", "x"])

    def test_parent_escape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): file_records(Path(tmp), ["../outside"])

    def test_hash_changes_with_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x"; path.write_text("a"); first = file_records(Path(tmp), ["x"])[0]["sha256"]
            path.write_text("b"); second = file_records(Path(tmp), ["x"])[0]["sha256"]
        self.assertNotEqual(first, second)


if __name__ == "__main__": unittest.main()
