"""Day 56 funnel tests."""
import unittest
from pathlib import Path
from mainline.day56.code.analyze_stage_funnel import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day56_stages_a.json";CA=ROOT/"mainline/day56/config/stage_funnel_a.json";B=ROOT/"shared/fixtures/day56_stages_b.json";CB=ROOT/"mainline/day56/config/stage_funnel_b.json"
class Day56Tests(unittest.TestCase):
    def test_four_stages(self):self.assertEqual(len(analyze(A,CA)["stages"]),4)
    def test_monotonic(self):self.assertTrue(analyze(A,CA)["monotonicity_pass"])
    def test_denominator(self):self.assertEqual(analyze(A,CA)["conversion_denominator"],"previous_stage_reached")
    def test_not_final(self):self.assertFalse(analyze(A,CA)["stage_metrics_final"])
    def test_b_new_funnel(self):self.assertNotEqual(analyze(A,CA)["conditions"],analyze(B,CB)["conditions"])
if __name__=="__main__":unittest.main()
