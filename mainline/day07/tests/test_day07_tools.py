import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from mainline.day04.code.real_preflight import LOCKED
from mainline.day07.code.build_fair_comparison import build
from mainline.day07.code.build_openvla_manifest import build_manifest
from mainline.day07.code.check_day07 import check_challenge, check_real
from mainline.day07.code.minimal_token_decode import decode
from mainline.day07.code.openvla_preflight import evaluate


class Day07ToolTests(unittest.TestCase):
    def test_token_decode_returns_seven_continuous_values(self):
        values = decode(np.array([999, 936, 872, 808, 744, 680, 999]), 1000,
                        np.array([-0.1] * 6 + [0.0]), np.array([0.1] * 6 + [1.0]))
        self.assertEqual(values.shape, (7,)); self.assertTrue(np.all(np.isfinite(values)))

    @patch("mainline.day07.code.build_openvla_manifest.locked_contract")
    def test_openvla_manifest_is_plan_not_result(self, contract):
        contract.return_value = {"commit": LOCKED, "action_bins": 256, "action_dim": 7}
        data = build_manifest(Path("unused"), Path("mainline/day07/config/openvla_a.json"))
        self.assertFalse(data["real_model_run"]); self.assertEqual(data["status"], "planned")

    def test_openvla_preflight_needs_base_and_memory(self):
        base = {"ready_for_real_episode": True}
        self.assertFalse(evaluate(base, 23_999)["ready_for_openvla_pilot"])
        self.assertTrue(evaluate(base, 24_000)["ready_for_openvla_pilot"])

    def test_comparison_rejects_seed_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); controls = {"suite": "s", "level": 0, "task_id": 0, "seed": 7,
                "init_state_index": 0, "num_trials": 1, "max_steps": 300}
            smol = {**controls, "source_kind": "locked_source_static_pilot_plan", "upstream_commit": LOCKED,
                    "checkpoint_revision": "a" * 40}
            openvla = {**controls, "seed": 8, "source_kind": "locked_source_static_openvla_plan",
                       "upstream_commit": LOCKED, "checkpoint_revision": "b" * 40}
            a, b = root / "a.json", root / "b.json"; a.write_text(json.dumps(smol)); b.write_text(json.dumps(openvla))
            with self.assertRaisesRegex(ValueError, "seed"): build(a, b)

    def test_challenge_recomputes_fair_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            answer = Path(tmp) / "answer.json"
            answer.write_text(json.dumps({"selected_pair": "pair_alpha", "rejected_reasons": {
                "pair_beta": "seed 不同", "pair_gamma": "task_id 不同"}}))
            check_challenge(Path("shared/fixtures/day07_comparison_candidates.json"), answer)

    def test_real_registry_requires_exact_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); log, video = root / "episode.log", root / "rollout.mp4"
            log.write_text("fixture log"); video.write_bytes(b"fixture video")
            cfg_path = Path("mainline/day07/config/openvla_a.json"); cfg = json.loads(cfg_path.read_text())
            row = {"commit": LOCKED, "checkpoint_repo": cfg["checkpoint_repo"],
                "checkpoint_revision": cfg["checkpoint_revision"], "suite": cfg["suite"], "level": "0",
                "task_id": "0", "seed": "7", "init_state_index": "0", "status": "completed",
                "source_kind": "real_openvla_vla_arena_episode", "success": "false", "frame_count": "3",
                "log_path": str(log), "video_path": str(video)}
            registry = root / "registry.csv"
            with registry.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(row)); writer.writeheader(); writer.writerow(row)
            check_real(registry, cfg_path)


if __name__ == "__main__": unittest.main()
