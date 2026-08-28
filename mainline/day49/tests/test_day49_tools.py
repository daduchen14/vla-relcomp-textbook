"""Day 49 ablation tests."""
import unittest
from pathlib import Path
from mainline.day49.code.analyze_cost_matched_ablation import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day49_ablation_a.json";CA=ROOT/"mainline/day49/config/ablation_config_a.json";B=ROOT/"shared/fixtures/day49_ablation_b.json";CB=ROOT/"mainline/day49/config/ablation_config_b.json"
class Day49Tests(unittest.TestCase):
    def test_single_variable(self):self.assertEqual(analyze(A,CA)["changed_factors"],["relation_normalization"])
    def test_all_cost_matched(self):self.assertTrue(analyze(A,CA)["all_cost_matched"])
    def test_all_seeds(self):self.assertEqual(analyze(A,CA)["registered_seeds"],[1,2,3])
    def test_not_formal(self):self.assertFalse(analyze(A,CA)["formal_runs_available"])
    def test_b_new_rows(self):self.assertNotEqual(analyze(A,CA)["paired_rows"],analyze(B,CB)["paired_rows"])
if __name__=="__main__":unittest.main()
