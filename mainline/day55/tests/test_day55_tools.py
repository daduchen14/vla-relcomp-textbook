"""Day 55 oracle-partition tests."""
import unittest
from pathlib import Path
from mainline.day55.code.analyze_final_oracles import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day55_oracle_a.json";CA=ROOT/"mainline/day55/config/final_oracle_a.json";B=ROOT/"shared/fixtures/day55_oracle_b.json";CB=ROOT/"mainline/day55/config/final_oracle_b.json"
class Day55Tests(unittest.TestCase):
    def test_records_complete(self):self.assertTrue(analyze(A,CA)["records_complete"])
    def test_oracle_not_primary(self):self.assertFalse(analyze(A,CA)["oracle_in_primary_result"])
    def test_oracle_not_deployable(self):self.assertFalse(analyze(A,CA)["oracle_deployable"])
    def test_no_final_data(self):self.assertFalse(analyze(A,CA)["final_oracle_data_available"])
    def test_b_new_oracle_results(self):self.assertNotEqual(analyze(A,CA)["diagnostic_oracles"],analyze(B,CB)["diagnostic_oracles"])
if __name__=="__main__":unittest.main()
