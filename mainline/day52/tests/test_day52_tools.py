"""Day 52 clean-room tests."""
import unittest
from pathlib import Path
from mainline.day52.code.build_clean_baseline_packet import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day52_inventory_a.json";CA=ROOT/"mainline/day52/config/clean_baseline_a.json";B=ROOT/"shared/fixtures/day52_inventory_b.json";CB=ROOT/"mainline/day52/config/clean_baseline_b.json"
class Day52Tests(unittest.TestCase):
    def test_required_inputs(self):self.assertTrue(analyze(A,CA)["required_roles_present"])
    def test_repair_rejected(self):self.assertFalse(analyze(A,CA)["repair_artifacts_accepted"])
    def test_old_results_rejected(self):self.assertFalse(analyze(A,CA)["old_results_accepted"])
    def test_not_run(self):self.assertIsNone(analyze(A,CA)["baseline_records"])
    def test_b_new_cleanroom(self):self.assertNotEqual(analyze(A,CA)["cleanroom_id"],analyze(B,CB)["cleanroom_id"])
if __name__=="__main__":unittest.main()
