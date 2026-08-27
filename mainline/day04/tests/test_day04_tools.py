import csv
import json
import tempfile
import unittest
from pathlib import Path

from mainline.day04.code.check_day04 import check_episode, check_preflight
from mainline.day04.code.real_preflight import LOCKED, evaluate


class Day04ToolTests(unittest.TestCase):
    def test_non_linux_snapshot_is_truthfully_blocked(self):
        report = evaluate({"os": "Darwin", "python": "3.14.0", "commit": LOCKED,
                           "nvidia_smi_returncode": 127, "MUJOCO_GL": None,
                           "PYOPENGL_PLATFORM": None})
        self.assertFalse(report["ready_for_real_episode"])
        self.assertIn("linux", report["blockers"])

    def test_complete_linux_snapshot_is_ready(self):
        report = evaluate({"os": "Linux", "python": "3.11.9", "commit": LOCKED,
                           "nvidia_smi_returncode": 0, "MUJOCO_GL": "egl",
                           "PYOPENGL_PLATFORM": "egl"})
        self.assertTrue(report["ready_for_real_episode"])

    def test_preflight_ready_cannot_disagree_with_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "preflight.json"
            path.write_text(json.dumps({"source_kind": "real_local_preflight_not_episode",
                "commit": LOCKED, "checks": {"linux": False},
                "ready_for_real_episode": True, "blockers": ["linux"]}))
            with self.assertRaisesRegex(ValueError, "ready"):
                check_preflight(path)

    def test_episode_registry_is_checked_against_gate_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); log, video = root / "run.log", root / "run.mp4"
            log.write_text("real fixture log"); video.write_bytes(b"fixture-video")
            gate = root / "gate.json"
            gate.write_text(json.dumps({"level": 0, "task_id": 1, "seed": 19, "init_state_index": 0}))
            row = {"commit": LOCKED, "suite": "extrapolation_preposition_combinations",
                   "level": "0", "task_id": "1", "seed": "19", "init_state_index": "0",
                   "status": "completed", "source_kind": "real_vla_arena_episode",
                   "success": "false", "frame_count": "2", "log_path": str(log), "video_path": str(video)}
            registry = root / "registry.csv"
            with registry.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(row)); writer.writeheader(); writer.writerow(row)
            check_episode(registry, gate)


if __name__ == "__main__":
    unittest.main()
