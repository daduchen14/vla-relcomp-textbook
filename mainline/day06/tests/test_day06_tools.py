import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mainline.day06.code.build_pilot_manifest import LOCKED, build_manifest
from mainline.day06.code.check_day06 import check_real
from mainline.day06.code.minimal_action_queue import rollout


class Day06ToolTests(unittest.TestCase):
    def test_action_queue_reuses_three_step_chunks(self):
        actions, calls = rollout(num_steps=7, chunk_size=3)
        self.assertEqual(calls, 3); self.assertEqual(actions[3], [10.0, 11.0])

    @patch("mainline.day06.code.build_pilot_manifest.locked_contract")
    def test_manifest_records_locked_contract(self, contract):
        contract.return_value = {"commit": LOCKED, "chunk_size": 50, "n_action_steps": 50}
        manifest = build_manifest(Path("unused"), Path("mainline/day06/config/pilot_a.json"))
        self.assertFalse(manifest["real_model_run"])
        self.assertEqual(manifest["locked_contract"]["chunk_size"], 50)

    def test_invalid_checkpoint_revision_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(Path("mainline/day06/config/pilot_a.json").read_text())
            data["checkpoint_revision"] = "main"
            path = Path(tmp) / "bad.json"; path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "40 位"), patch(
                "mainline.day06.code.build_pilot_manifest.locked_contract"
            ):
                build_manifest(Path("unused"), path)

    def test_real_registry_requires_exact_checkpoint_and_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); log, video = root / "episode.log", root / "rollout.mp4"
            log.write_text("fixture log"); video.write_bytes(b"fixture video")
            cfg_path = Path("mainline/day06/config/pilot_b.json")
            cfg = json.loads(cfg_path.read_text())
            row = {"commit": LOCKED, "checkpoint_repo": cfg["checkpoint_repo"],
                   "checkpoint_revision": cfg["checkpoint_revision"], "suite": cfg["suite"],
                   "level": "0", "task_id": str(cfg["task_id"]), "seed": str(cfg["seed"]),
                   "init_state_index": str(cfg["init_state_index"]), "status": "completed",
                   "source_kind": "real_smolvla_vla_arena_episode", "success": "false",
                   "frame_count": "2", "log_path": str(log), "video_path": str(video)}
            registry = root / "registry.csv"
            with registry.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(row)); writer.writeheader(); writer.writerow(row)
            check_real(registry, cfg_path)


if __name__ == "__main__":
    unittest.main()
