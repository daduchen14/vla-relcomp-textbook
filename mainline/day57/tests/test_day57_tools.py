"""Day 57 paired-statistics tests."""
import unittest
from pathlib import Path
from mainline.day57.code.compute_paired_statistics import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day57_counts_a.json";CA=ROOT/"mainline/day57/config/statistics_a.json";B=ROOT/"shared/fixtures/day57_counts_b.json";CB=ROOT/"mainline/day57/config/statistics_b.json"
class Day57Tests(unittest.TestCase):
    def test_a_delta(self):self.assertEqual(analyze(A,CA)["paired_success_rate_delta"],0.25)
    def test_a_exact_p(self):self.assertEqual(analyze(A,CA)["mcnemar"]["two_sided_exact_p"],0.125)
    def test_a_not_significant(self):self.assertFalse(analyze(A,CA)["mcnemar"]["reject_equal_marginals"])
    def test_b_significant_under_registered_alpha(self):self.assertTrue(analyze(B,CB)["mcnemar"]["reject_equal_marginals"])
    def test_not_formal(self):self.assertFalse(analyze(A,CA)["formal_statistics_available"])
if __name__=="__main__":unittest.main()
