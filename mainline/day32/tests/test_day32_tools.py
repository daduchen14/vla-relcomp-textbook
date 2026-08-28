"""Day 32 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day32.code.build_object_pair_set import build
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day32_object_pair_spec_a.csv";B=FIX/"day32_object_pair_spec_b.csv"
class Day32Tests(unittest.TestCase):
    def test_a_pair_and_combo_count(self):self.assertEqual((build(A)[1]["pair_count"],build(A)[1]["unique_object_combinations"]),(3,6))
    def test_relation_is_fixed(self):
        rows=build(A)[0];self.assertEqual(rows[0]["relation"],rows[1]["relation"])
    def test_combo_changes(self):
        rows=build(A)[0];self.assertNotEqual(rows[0]["object_combination"],rows[1]["object_combination"])
    def test_reference_only_change_is_allowed(self):
        rows=build(A)[0];self.assertEqual(rows[2]["target_object_id"].split("_")[0],rows[3]["target_object_id"].split("_")[0])
    def test_b_has_new_coverage(self):self.assertNotEqual(build(A)[1]["relation_coverage"],build(B)[1]["relation_coverage"])
if __name__=="__main__":unittest.main()
