"""Day 34 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day34.code.analyze_visual_oracle import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day34_visual_oracle_results_a.csv";B=FIX/"day34_visual_oracle_results_b.csv"
class Day34Tests(unittest.TestCase):
    def test_a_recovery(self):
        effect=analyze(A)[1]["success_effect"];self.assertEqual((effect["recovery_numerator"],effect["recovery_denominator"]),(2,3))
    def test_a_damage(self):
        effect=analyze(A)[1]["success_effect"];self.assertEqual((effect["damage_numerator"],effect["damage_denominator"]),(1,2))
    def test_overlay_source(self):self.assertTrue(all(row["overlay_source"]=="simulator_ground_truth" for row in analyze(A)[0]))
    def test_cleanup(self):self.assertTrue(analyze(A)[1]["cleanup_verified_for_all_pairs"])
    def test_b_is_new(self):self.assertNotEqual(analyze(A)[1]["success_effect"],analyze(B)[1]["success_effect"])
if __name__=="__main__":unittest.main()
