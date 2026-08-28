"""Day 58 casebook tests."""
import unittest
from pathlib import Path
from mainline.day58.code.build_casebook import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day58_cases_a.json";CA=ROOT/"mainline/day58/config/casebook_a.json";B=ROOT/"shared/fixtures/day58_cases_b.json";CB=ROOT/"mainline/day58/config/casebook_b.json"
class Day58Tests(unittest.TestCase):
    def test_all_strata(self):self.assertTrue(analyze(A,CA)["all_strata_covered"])
    def test_no_manual_override(self):self.assertFalse(analyze(A,CA)["manual_override"])
    def test_not_viewed(self):self.assertFalse(analyze(A,CA)["videos_viewed"])
    def test_not_final(self):self.assertFalse(analyze(A,CA)["final_casebook_available"])
    def test_b_new_selection(self):self.assertNotEqual(analyze(A,CA)["selected_cases"],analyze(B,CB)["selected_cases"])
if __name__=="__main__":unittest.main()
