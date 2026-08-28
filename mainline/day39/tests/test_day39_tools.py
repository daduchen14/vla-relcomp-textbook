"""Day 39 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day39.code.build_training_pairs import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day39_training_registry_a.csv";B=FIX/"day39_training_registry_b.csv";CA=ROOT/"mainline/day39/config/training_pair_config_a.json";CB=ROOT/"mainline/day39/config/training_pair_config_b.json"
class Day39Tests(unittest.TestCase):
    def test_a_balanced(self):self.assertEqual(analyze(A,CA)[1]["selected_relation_counts"],{"Between":2,"In":2,"NextTo":2,"On":2})
    def test_a_pairs_complete(self):self.assertEqual((analyze(A,CA)[1]["pair_count"],analyze(A,CA)[1]["arm_count"]),(8,16))
    def test_same_action_target(self):
        rows=analyze(A,CA)[0];self.assertEqual(rows[0]["action_target_sha256"],rows[1]["action_target_sha256"])
    def test_outcome_free(self):self.assertFalse(analyze(A,CA)[1]["selection_uses_outcomes"])
    def test_b_new_target(self):self.assertEqual((analyze(B,CB)[1]["target_per_relation"],analyze(B,CB)[1]["pair_count"]),(1,4))
if __name__=="__main__":unittest.main()
