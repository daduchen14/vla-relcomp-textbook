"""Day 33 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day33.code.analyze_language_oracle import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day33_language_oracle_results_a.csv";B=FIX/"day33_language_oracle_results_b.csv"
class Day33Tests(unittest.TestCase):
    def test_a_recovery(self):
        effect=analyze(A)[1]["success_effect"];self.assertEqual((effect["recovery_numerator"],effect["recovery_denominator"]),(2,3))
    def test_a_damage(self):
        effect=analyze(A)[1]["success_effect"];self.assertEqual((effect["damage_numerator"],effect["damage_denominator"]),(1,2))
    def test_first_changed_stage(self):self.assertEqual(analyze(A)[0][1]["first_changed_stage"],"reference_approached")
    def test_no_change_is_preserved(self):self.assertEqual(analyze(A)[0][2]["first_changed_stage"],"NONE")
    def test_b_new_rates(self):self.assertNotEqual(analyze(A)[1]["stage_effects"],analyze(B)[1]["stage_effects"])
if __name__=="__main__":unittest.main()
