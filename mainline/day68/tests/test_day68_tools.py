import tempfile,unittest
from pathlib import Path
from shared.scripts.course_demo import run
ROOT=Path(__file__).resolve().parents[3]
class Day68Tests(unittest.TestCase):
 def make(self,s):t=tempfile.TemporaryDirectory();o=Path(t.name)/"r.json";r=run(ROOT/f"shared/fixtures/day68_demo_{s}.json",o);return t,o,r
 def test_a_pass(self):t,o,r=self.make("a");self.assertTrue(r["all_passed"]);t.cleanup()
 def test_b_new(self):t,o,r=self.make("b");self.assertEqual(r["demo_id"],"public-entry-b");t.cleanup()
 def test_fallbacks(self):t,o,r=self.make("a");self.assertTrue(all(x["fallback"] for x in r["steps"]));t.cleanup()
 def test_cpu(self):t,o,r=self.make("b");self.assertFalse(r["gpu_used"]);t.cleanup()
 def test_no_overwrite(self):
  t,o,r=self.make("a")
  with self.assertRaises(FileExistsError):run(ROOT/"shared/fixtures/day68_demo_a.json",o)
  t.cleanup()
if __name__=="__main__":unittest.main()
