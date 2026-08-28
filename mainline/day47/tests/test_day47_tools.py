"""Day 47 L0 retention tests."""
import unittest
from pathlib import Path
from mainline.day47.code.analyze_l0_retention import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day47_l0_retention_a.json";CA=ROOT/"mainline/day47/config/retention_config_a.json";B=ROOT/"shared/fixtures/day47_l0_retention_b.json";CB=ROOT/"mainline/day47/config/retention_config_b.json"
class Day47Tests(unittest.TestCase):
    def test_a_retains_all_baseline_successes(self):self.assertEqual(analyze(A,CA)[1]["retention_rate"],1.0)
    def test_a_delta(self):self.assertEqual(analyze(A,CA)[1]["success_rate_delta"],0.125)
    def test_b_records_regression(self):self.assertEqual(analyze(B,CB)[1]["catastrophic_regressions"],["B12"])
    def test_b_meets_frozen_threshold(self):self.assertTrue(analyze(B,CB)[1]["retention_pass"])
    def test_not_real_eval(self):self.assertFalse(analyze(A,CA)[1]["vla_arena_run"])
if __name__=="__main__":unittest.main()
