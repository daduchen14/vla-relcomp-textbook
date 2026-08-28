"""Day 37 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day37.code.build_l0_dataset import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day37_registry_a.csv";B=FIX/"day37_registry_b.csv"
class Day37Tests(unittest.TestCase):
    def test_a_l0_rows(self):self.assertEqual(analyze(A)[1]["output_rows"],6)
    def test_a_excludes_heldout(self):self.assertEqual(analyze(A)[1]["excluded_heldout_counts"],{"L1":1,"L2":2})
    def test_only_level_zero(self):self.assertTrue(all(row["level"]=="0" for row in analyze(A)[0]))
    def test_lineage_hashes(self):self.assertTrue(all(len(row["dataset_row_sha256"])==64 for row in analyze(A)[0]))
    def test_b_is_new(self):self.assertNotEqual(analyze(A)[1]["output_split_counts"],analyze(B)[1]["output_split_counts"])
if __name__=="__main__":unittest.main()
