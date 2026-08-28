"""Day 35 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day35.code.build_diagnosis_table import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day35_diagnosis_evidence_a.csv";B=FIX/"day35_diagnosis_evidence_b.csv"
class Day35Tests(unittest.TestCase):
    def test_a_funnel(self):self.assertEqual(analyze(A)[1]["funnel"]["target_lifted_to_reference_approached"]["rate"],0.5)
    def test_a_pair_asymmetry(self):self.assertEqual(analyze(A)[1]["relation_pair"]["pair_asymmetry"],0.5)
    def test_a_candidate_pattern(self):self.assertEqual(analyze(A)[1]["pattern_label"],"LANGUAGE_RELATION_CANDIDATE")
    def test_b_insufficient(self):self.assertEqual(analyze(B)[1]["pattern_label"],"INSUFFICIENT_EVIDENCE")
    def test_boundary(self):self.assertEqual(analyze(B)[1]["evidence_status"],"SYNTHETIC_REHEARSAL_NO_RESEARCH_CONCLUSION")
if __name__=="__main__":unittest.main()
