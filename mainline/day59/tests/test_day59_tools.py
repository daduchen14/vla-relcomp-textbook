"""Day 59 resource-ledger tests."""
import unittest
from pathlib import Path
from mainline.day59.code.summarize_resources import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day59_resources_a.json";CA=ROOT/"mainline/day59/config/resource_a.json";B=ROOT/"shared/fixtures/day59_resources_b.json";CB=ROOT/"mainline/day59/config/resource_b.json"
class Day59Tests(unittest.TestCase):
    def test_a_denominators(self):self.assertEqual(analyze(A,CA)["denominators"],{"planned":5,"attempted":4,"completed":3,"failed":1,"not_run":1})
    def test_failed_cost_included(self):self.assertTrue(analyze(A,CA)["failed_cost_included"])
    def test_peak_includes_attempts(self):self.assertEqual(analyze(A,CA)["max_peak_memory_gib_attempted"],7.4)
    def test_not_real(self):self.assertFalse(analyze(A,CA)["real_gpu_measurements"])
    def test_b_new_denominator(self):self.assertNotEqual(analyze(A,CA)["denominators"],analyze(B,CB)["denominators"])
if __name__=="__main__":unittest.main()
