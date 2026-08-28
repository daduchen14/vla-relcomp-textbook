import json,tempfile,unittest
from pathlib import Path
from mainline.day70.code.capstone_contract import expected_analysis
from mainline.day70.code.prepare_capstone import prepare
from shared.answer_keys.day70_reference import analyze
ROOT=Path(__file__).resolve().parents[3]
class Day70Tests(unittest.TestCase):
 def payload(self,s):return json.loads((ROOT/f"shared/fixtures/day70_capstone_{s}.json").read_text())
 def test_reference_a(self):self.assertEqual(analyze(self.payload("a"),.1),expected_analysis(self.payload("a"),.1))
 def test_reference_b(self):self.assertEqual(analyze(self.payload("b"),.3),expected_analysis(self.payload("b"),.3))
 def test_new_shapes(self):self.assertNotEqual(expected_analysis(self.payload("a"),.1)["observation_summary"],expected_analysis(self.payload("b"),.1)["observation_summary"])
 def test_parameter_change(self):
  low=expected_analysis(self.payload("b"),.1);high=expected_analysis(self.payload("b"),.3);self.assertNotEqual(low["meets_threshold"],high["meets_threshold"])
 def test_prepare_no_answer(self):
  with tempfile.TemporaryDirectory() as t:
   out=Path(t)/"exam";prepare("B",out);self.assertIn("NotImplementedError",(out/"core_module.py").read_text());self.assertNotIn("day70_reference",(out/"core_module.py").read_text())
if __name__=="__main__":unittest.main()
