"""Day 18 免费 CPU 测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from mainline.day18.code.build_l0_registry import build, write
from mainline.day18.code.build_video_index import build as index

ROOT = Path(__file__).resolve().parents[3]
SPEC_A = ROOT / "shared/fixtures/day18_l0_spec_a.json"
SPEC_B = ROOT / "shared/fixtures/day18_l0_spec_b.json"


def table(root: Path) -> Path:
    tasks = [{"level": 0, "task_id": task_id, "task_name": f"task-{task_id}",
              "bddl_path": f"task-{task_id}.bddl", "target_object": f"target-{task_id}",
              "reference_object": f"reference-{task_id}", "goal_relation": "On"} for task_id in range(5)]
    path = root / "table.json"; path.write_text(json.dumps({
        "commit": "babe582ebffc82b979b77964a7e56417d02f63a4",
        "suite": "extrapolation_preposition_combinations", "tasks": tasks}))
    return path


class Day18Tests(unittest.TestCase):
    def test_a_covers_five_tasks_twice(self):
        with tempfile.TemporaryDirectory() as tmp: rows = build(table(Path(tmp)), SPEC_A)
        self.assertEqual(len(rows), 10); self.assertEqual({row["task_id"] for row in rows}, set(range(5)))

    def test_b_is_new_three_trial_plan(self):
        with tempfile.TemporaryDirectory() as tmp: rows = build(table(Path(tmp)), SPEC_B)
        self.assertEqual(len(rows), 15); self.assertEqual(len({row["episode_id"] for row in rows}), 15)

    def test_duplicate_init_indices_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(SPEC_A.read_text()); data["init_state_indices"] = [1, 1]
            path = Path(tmp)/"spec.json"; path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): build(table(Path(tmp)), path)

    def test_unequal_task_denominator_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = build(table(Path(tmp)), SPEC_A)[:-1]; registry = Path(tmp)/"registry.csv"; write(registry, rows)
            with self.assertRaises(ValueError): index(registry, Path(tmp))

    def test_completed_without_video_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = build(table(Path(tmp)), SPEC_A); rows[0]["status"] = "COMPLETED"; rows[0]["success"] = "1"
            registry = Path(tmp)/"registry.csv"; write(registry, rows)
            with self.assertRaises(ValueError): index(registry, Path(tmp))


if __name__ == "__main__": unittest.main()
