"""Day 38 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day38.code.apply_relation_normalizer import analyze
from mainline.day38.code.relation_normalizer import normalize_relation_instruction
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day38_relation_examples_a.csv";B=FIX/"day38_relation_examples_b.csv"
class Day38Tests(unittest.TestCase):
    def test_a_rows(self):self.assertEqual(analyze(A)[1]["row_count"],4)
    def test_between_is_canonical(self):self.assertIn("START=between(cabinet_4+teapot_4)",analyze(A)[0][3]["normalized_instruction"])
    def test_input_not_mutated(self):self.assertEqual(analyze(A)[1]["input_mutation_count"],0)
    def test_l1_rejected(self):
        with self.assertRaisesRegex(ValueError,"只接受 L0"):normalize_relation_instruction({"level":"1","target_object_id":"x","start_relation":"In","start_reference_ids":"y","goal_relation":"On","goal_reference_ids":"z"})
    def test_b_is_new(self):self.assertNotEqual([r["input_row_sha256"] for r in analyze(A)[0]],[r["input_row_sha256"] for r in analyze(B)[0]])
if __name__=="__main__":unittest.main()
