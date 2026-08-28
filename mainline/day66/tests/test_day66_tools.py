import tempfile,unittest
from pathlib import Path
from mainline.day66.code.build_complete_report import build
ROOT=Path(__file__).resolve().parents[3]
class Day66Tests(unittest.TestCase):
 def make(self,s):t=tempfile.TemporaryDirectory();o=Path(t.name)/"o";m=build(ROOT/f"shared/fixtures/day66_dossier_{s}.json",ROOT/f"mainline/day66/config/report_{s}.json",o);return t,o,m
 def test_sections(self):t,o,m=self.make("a");self.assertEqual(len(m["sections"]),11);t.cleanup()
 def test_limits(self):t,o,m=self.make("a");self.assertEqual(m["limitation_dimensions"],5);t.cleanup()
 def test_ethics(self):t,o,m=self.make("a");self.assertEqual(m["ethics_dimensions"],5);t.cleanup()
 def test_negative(self):t,o,m=self.make("b");self.assertTrue(m["negative_results_present"]);t.cleanup()
 def test_not_formal(self):t,o,m=self.make("b");self.assertFalse(m["formal_report"]);t.cleanup()
if __name__=="__main__":unittest.main()
