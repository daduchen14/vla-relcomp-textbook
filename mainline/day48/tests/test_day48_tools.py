"""Day 48 OOD analysis tests."""
import unittest
from pathlib import Path
from mainline.day48.code.analyze_ood_results import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day48_ood_a.json";CA=ROOT/"mainline/day48/config/ood_analysis_a.json";B=ROOT/"shared/fixtures/day48_ood_b.json";CB=ROOT/"mainline/day48/config/ood_analysis_b.json"
class Day48Tests(unittest.TestCase):
    def test_a_both_levels(self):self.assertEqual(set(analyze(A,CA)["levels"]),{"L1","L2"})
    def test_a_all_pass(self):self.assertTrue(analyze(A,CA)["all_levels_pass"])
    def test_no_primary_pooling(self):self.assertFalse(analyze(A,CA)["pooling_for_primary_conclusion"])
    def test_no_best_level_selection(self):self.assertFalse(analyze(A,CA)["best_level_selection"])
    def test_b_new_preregistration(self):self.assertNotEqual(analyze(A,CA)["analysis_config_sha256"],analyze(B,CB)["analysis_config_sha256"])
if __name__=="__main__":unittest.main()
