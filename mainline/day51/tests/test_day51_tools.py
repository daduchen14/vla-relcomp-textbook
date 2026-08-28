"""Day 51 final-manifest tests."""
import unittest
from pathlib import Path
from mainline.day51.code.freeze_final_manifest import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"mainline/day51/config/final_matrix_a.json";B=ROOT/"mainline/day51/config/final_matrix_b.json"
class Day51Tests(unittest.TestCase):
    def test_a_rollout_count(self):self.assertEqual(analyze(A)["expected_episode_rollouts"],270)
    def test_stop_rules_complete(self):self.assertEqual(len(analyze(A)["stop_rules"]),6)
    def test_not_authorized(self):self.assertFalse(analyze(A)["authorized_for_gpu"])
    def test_no_results(self):self.assertFalse(analyze(A)["formal_results_available"])
    def test_b_new_hash(self):self.assertNotEqual(analyze(A)["manifest_sha256"],analyze(B)["manifest_sha256"])
if __name__=="__main__":unittest.main()
