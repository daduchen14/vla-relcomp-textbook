import tempfile,unittest
from pathlib import Path
from mainline.day65.code.build_results_draft import build
ROOT=Path(__file__).resolve().parents[3]
class Day65Tests(unittest.TestCase):
 def make(self,s):t=tempfile.TemporaryDirectory();o=Path(t.name)/"o";m=build(ROOT/f"shared/fixtures/day65_results_{s}.json",ROOT/f"mainline/day65/config/results_{s}.json",o);return t,o,m
 def test_order(self):t,o,m=self.make("a");self.assertEqual(m["claim_types"][0],"denominator");t.cleanup()
 def test_count(self):t,o,m=self.make("a");self.assertEqual(m["claim_count"],8);t.cleanup()
 def test_negative(self):t,o,m=self.make("a");self.assertTrue(m["negative_results_preserved"]);t.cleanup()
 def test_boundaries(self):t,o,m=self.make("b");self.assertTrue(m["all_claims_have_boundaries"]);t.cleanup()
 def test_not_formal(self):t,o,m=self.make("b");self.assertFalse(m["formal_results"]);t.cleanup()
if __name__=="__main__":unittest.main()
