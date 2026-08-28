"""Day 24 免费 CPU 测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from mainline.day24.code.select_primary_model import select

ROOT = Path(__file__).resolve().parents[3]; FIX = ROOT / "shared/fixtures"
A_STATS = FIX / "day24_candidate_stats_a.csv"; A_POLICY = FIX / "day24_selection_policy_a.json"
B_STATS = FIX / "day24_candidate_stats_b.csv"; B_POLICY = FIX / "day24_selection_policy_b.json"


class Day24Tests(unittest.TestCase):
    def test_a_selects_beta_by_registered_metric(self):
        _, decision = select(A_STATS, A_POLICY); self.assertEqual(decision["selected_model_id"], "synthetic/model-beta")

    def test_eligible_candidates_share_denominators(self):
        rows, _ = select(A_STATS, A_POLICY); self.assertEqual({row["total_valid_n"] for row in rows}, {20})

    def test_b_excludes_insufficient_delta(self):
        rows, decision = select(B_STATS, B_POLICY)
        delta = next(row for row in rows if row["model_id"] == "synthetic/model-delta")
        self.assertEqual(delta["exclusion_reason"], "min_valid_per_task"); self.assertNotIn(delta["model_id"], decision["eligible_model_ids"])

    def test_l1_row_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"; path.write_text(A_STATS.read_text(encoding="utf-8").replace(",0,0,3,4,", ",1,0,3,4,", 1), encoding="utf-8")
            with self.assertRaises(ValueError): select(path, A_POLICY)

    def test_policy_cannot_preselect_winner(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(A_POLICY.read_text(encoding="utf-8")); data["selected_model_id"] = "synthetic/model-alpha"
            policy = Path(tmp) / "policy.json"; policy.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError): select(A_STATS, policy)


if __name__ == "__main__": unittest.main()
