"""Day 36 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day36.code.make_repair_decision import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";CFG=ROOT/"mainline/day36/config/repair_decision_weights.json";A=FIX/"day36_repair_candidates_a.csv";B=FIX/"day36_repair_candidates_b.csv"
class Day36Tests(unittest.TestCase):
    def test_a_selects_language(self):self.assertEqual(analyze(A,CFG)[1]["selected_decision"],"LANGUAGE_RELATION_NORMALIZATION")
    def test_b_stops_on_gate(self):self.assertEqual(analyze(B,CFG)[1]["selected_decision"],"STOP_NO_REPAIR")
    def test_one_selected(self):self.assertEqual(sum(row["selected"]=="true" for row in analyze(A,CFG)[0]),1)
    def test_training_not_authorized(self):self.assertFalse(analyze(A,CFG)[1]["authorized_for_training"])
    def test_weights_frozen(self):self.assertEqual(analyze(A,CFG)[1]["matrix_weights"]["leakage_risk"],-2)
if __name__=="__main__":unittest.main()
