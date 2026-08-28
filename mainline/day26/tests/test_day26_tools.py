"""Day 26 免费 CPU 测试。"""
import json, tempfile, unittest
from pathlib import Path
from mainline.day26.code.build_hypothesis_matrix import build
ROOT=Path(__file__).resolve().parents[3]; A=ROOT/"shared/fixtures/day26_hypotheses_a.json"; B=ROOT/"shared/fixtures/day26_hypotheses_b.json"
class Day26Tests(unittest.TestCase):
    def test_a_has_three_untested_hypotheses(self):
        rows,report=build(A); self.assertEqual(len(rows),3); self.assertEqual(report["causal_status"],"pre_registered_untested")
    def test_each_has_two_alternatives(self):
        rows,_=build(A); self.assertTrue(all(" | " in row["alternative_explanations"] for row in rows))
    def test_b_changes_events(self):
        _,report=build(B); self.assertIn("approach",report["primary_event_counts"])
    def test_result_field_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=json.loads(A.read_text()); data["observed_result"]="good"; path=Path(tmp)/"x.json"; path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): build(path)
    def test_missing_control_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=json.loads(A.read_text()); data["hypotheses"][0]["control_variables"].remove("seed"); path=Path(tmp)/"x.json"; path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): build(path)
if __name__=="__main__": unittest.main()
