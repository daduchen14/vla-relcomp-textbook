"""Day 54 pair-integrity tests."""
import unittest
from pathlib import Path
from mainline.day54.code.analyze_final_pairs import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day54_pairs_a.json";CA=ROOT/"mainline/day54/config/final_pairs_a.json";B=ROOT/"shared/fixtures/day54_pairs_b.json";CB=ROOT/"mainline/day54/config/final_pairs_b.json"
class Day54Tests(unittest.TestCase):
    def test_integrity(self):self.assertTrue(analyze(A,CA)["integrity_pass"])
    def test_no_missing(self):self.assertEqual(analyze(A,CA)["missing_records"],[])
    def test_no_duplicates(self):self.assertEqual(analyze(A,CA)["duplicate_count"],0)
    def test_not_final_data(self):self.assertFalse(analyze(A,CA)["final_pair_data_available"])
    def test_b_new_pairs(self):self.assertNotEqual(analyze(A,CA)["pair_rows"],analyze(B,CB)["pair_rows"])
if __name__=="__main__":unittest.main()
