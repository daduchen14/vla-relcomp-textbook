"""Day 53 repair provenance tests."""
import unittest
from pathlib import Path
from mainline.day53.code.build_clean_repair_packet import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day53_checkpoint_a.json";CA=ROOT/"mainline/day53/config/clean_repair_a.json";B=ROOT/"shared/fixtures/day53_checkpoint_b.json";CB=ROOT/"mainline/day53/config/clean_repair_b.json"
class Day53Tests(unittest.TestCase):
    def test_provenance_valid(self):self.assertTrue(analyze(A,CA)["provenance_valid"])
    def test_all_checks(self):self.assertTrue(all(analyze(A,CA)["provenance_checks"].values()))
    def test_protocol_frozen(self):self.assertTrue(analyze(A,CA)["protocol_frozen"])
    def test_not_run(self):self.assertIsNone(analyze(A,CA)["repair_records"])
    def test_b_new_cleanroom(self):self.assertNotEqual(analyze(A,CA)["cleanroom_id"],analyze(B,CB)["cleanroom_id"])
if __name__=="__main__":unittest.main()
