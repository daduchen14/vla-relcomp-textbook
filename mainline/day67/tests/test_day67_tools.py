import tempfile,unittest
from pathlib import Path
from mainline.day67.code.reproduce_minimal_table import reproduce
ROOT=Path(__file__).resolve().parents[3]
class Day67Tests(unittest.TestCase):
 def make(self,s):t=tempfile.TemporaryDirectory();o=Path(t.name)/"o";m=reproduce(ROOT/f"shared/fixtures/day67_repro_{s}.csv",ROOT/f"shared/fixtures/day67_expected_{s}.json",o);return t,o,m
 def test_pass(self):t,o,m=self.make("a");self.assertEqual(m["status"],"PASS");t.cleanup()
 def test_no_cache(self):t,o,m=self.make("a");self.assertFalse(m["cache_used"]);t.cleanup()
 def test_cpu_only(self):t,o,m=self.make("b");self.assertFalse(m["gpu_used"]);t.cleanup()
 def test_rows(self):t,o,m=self.make("b");self.assertEqual(m["row_count"],6);t.cleanup()
 def test_no_overwrite(self):
  t,o,m=self.make("a")
  with self.assertRaises(FileExistsError):reproduce(ROOT/"shared/fixtures/day67_repro_a.csv",ROOT/"shared/fixtures/day67_expected_a.json",o)
  t.cleanup()
if __name__=="__main__":unittest.main()
