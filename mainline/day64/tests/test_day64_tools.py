import tempfile,unittest
from pathlib import Path
from mainline.day64.code.build_methods_draft import build
ROOT=Path(__file__).resolve().parents[3]
class Day64Tests(unittest.TestCase):
 def make(self,s):t=tempfile.TemporaryDirectory();o=Path(t.name)/"o";m=build(ROOT/f"shared/fixtures/day64_protocol_{s}.json",ROOT/f"mainline/day64/config/methods_{s}.json",o);return t,o,m
 def test_sections(self):t,o,m=self.make("a");self.assertEqual(len(m["sections"]),9);t.cleanup()
 def test_definitions(self):t,o,m=self.make("a");self.assertEqual(len(m["operational_definitions"]),4);t.cleanup()
 def test_no_results(self):t,o,m=self.make("a");self.assertFalse(m["result_claims_in_methods"]);t.cleanup()
 def test_locked_commit(self):t,o,m=self.make("b");self.assertEqual(m["upstream_commit"],"babe582ebffc82b979b77964a7e56417d02f63a4");t.cleanup()
 def test_not_formal(self):t,o,m=self.make("b");self.assertFalse(m["formal_methods"]);t.cleanup()
if __name__=="__main__":unittest.main()
