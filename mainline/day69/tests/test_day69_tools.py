import tempfile,unittest
from pathlib import Path
from mainline.day69.code.build_defense_package import build
ROOT=Path(__file__).resolve().parents[3]
class Day69Tests(unittest.TestCase):
 def make(self,s):t=tempfile.TemporaryDirectory();o=Path(t.name)/"o";m=build(ROOT/f"shared/fixtures/day69_talk_{s}.json",ROOT/f"mainline/day69/config/talk_{s}.json",o);return t,o,m
 def test_timing(self):t,o,m=self.make("a");self.assertEqual(m["total_seconds"],600);t.cleanup()
 def test_slides(self):t,o,m=self.make("a");self.assertEqual(m["slide_count"],8);t.cleanup()
 def test_qa(self):t,o,m=self.make("b");self.assertEqual(m["qa_count"],10);t.cleanup()
 def test_boundaries(self):t,o,m=self.make("b");self.assertTrue(m["all_slides_bounded"]);t.cleanup()
 def test_not_formal(self):t,o,m=self.make("b");self.assertFalse(m["formal_defense"]);t.cleanup()
if __name__=="__main__":unittest.main()
