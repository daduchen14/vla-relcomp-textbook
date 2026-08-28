"""Day 31 免费 CPU 测试。"""
import csv,tempfile,unittest
from pathlib import Path
from mainline.day31.code.build_relation_pair_set import build
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day31_relation_pair_spec_a.csv";B=FIX/"day31_relation_pair_spec_b.csv"
class Day31Tests(unittest.TestCase):
    def test_a_bulk_pair_count(self):self.assertEqual((len(build(A)[0]),build(A)[1]["pair_count"]),(6,3))
    def test_two_arms_share_pair_id(self):
        rows=build(A)[0];self.assertEqual(rows[0]["pair_id"],rows[1]["pair_id"])
    def test_relation_changes(self):
        rows=build(A)[0];self.assertNotEqual(rows[0]["relation"],rows[1]["relation"])
    def test_fixed_hashes_match(self):
        rows=build(A)[0];self.assertEqual(rows[0]["matched_state_group_sha256"],rows[1]["matched_state_group_sha256"])
    def test_b_is_new_input(self):self.assertNotEqual(build(A)[1]["relation_contrasts"],build(B)[1]["relation_contrasts"])
if __name__=="__main__":unittest.main()
