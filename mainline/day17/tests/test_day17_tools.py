"""Day 17 免费 CPU 测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from mainline.day16.code.build_registry import EPISODE_FIELDS, build, write_csv
from mainline.day17.code.resumable_runner import run_batch

ROOT = Path(__file__).resolve().parents[3]
SPEC = ROOT / "shared/fixtures/day16_registry_spec_a.json"
EXECUTOR = ROOT / "shared/fixtures/day17_executor_a.json"


def setup(root: Path):
    _, episodes, _ = build(SPEC); source = root/"input.csv"; write_csv(source, EPISODE_FIELDS, episodes)
    return source, root/"output.csv", root/"checkpoint.json", root/"evidence"


class Day17Tests(unittest.TestCase):
    def test_interruption_then_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = setup(Path(tmp)); first = run_batch(*args[:3], EXECUTOR, args[3], max_work_items=2)
            second = run_batch(*args[:3], EXECUTOR, args[3])
        self.assertEqual(first["processed_this_call"], 2); self.assertEqual(second["COMPLETED"], 2)
        self.assertEqual(second["INVALID"], 1)

    def test_terminal_rerun_executes_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = setup(Path(tmp)); run_batch(*args[:3], EXECUTOR, args[3]); run_batch(*args[:3], EXECUTOR, args[3])
            again = run_batch(*args[:3], EXECUTOR, args[3])
        self.assertEqual(again["processed_this_call"], 0)

    def test_retry_attempt_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = setup(Path(tmp)); run_batch(*args[:3], EXECUTOR, args[3]); run_batch(*args[:3], EXECUTOR, args[3])
            state = json.loads(args[2].read_text())
        attempts = sorted(item["attempts"] for item in state["episodes"].values())
        self.assertEqual(attempts, [1, 1, 2])

    def test_checkpoint_rejects_unknown_episode(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = setup(Path(tmp)); args[2].write_text(json.dumps({"schema_version": "day17_checkpoint_v1",
                "episodes": {"ep-unknown": {}}}))
            with self.assertRaises(ValueError): run_batch(*args[:3], EXECUTOR, args[3])

    def test_missing_task_script_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = setup(Path(tmp)); config = Path(tmp)/"executor.json"
            config.write_text(json.dumps({"executor_kind": "scripted_fixture_not_vla_model", "max_attempts": 1,
                                          "outcomes_by_task": {"0": ["COMPLETED_SUCCESS"]}}))
            with self.assertRaises(ValueError): run_batch(*args[:3], config, args[3])


if __name__ == "__main__": unittest.main()
