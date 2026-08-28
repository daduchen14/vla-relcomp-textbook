import tempfile,unittest
from pathlib import Path
from mainline.day62.code.generate_paper_table import build
ROOT=Path(__file__).resolve().parents[3]
class Day62Tests(unittest.TestCase):
 def make(self,s):
  t=tempfile.TemporaryDirectory();o=Path(t.name)/"out";m=build(ROOT/f"shared/fixtures/day62_tidy_{s}.csv",ROOT/f"mainline/day62/config/table_{s}.json",o);return t,o,m
 def test_groups(self):t,o,m=self.make("a");self.assertEqual(m["group_count"],4);t.cleanup()
 def test_counts(self):t,o,m=self.make("a");self.assertTrue(m["counts_reported"]);t.cleanup()
 def test_interval(self):t,o,m=self.make("a");self.assertEqual(m["interval"],"95% Wilson");t.cleanup()
 def test_boundary(self):t,o,m=self.make("b");self.assertFalse(m["formal_results"]);t.cleanup()
 def test_no_overwrite(self):
  t,o,m=self.make("a")
  with self.assertRaises(FileExistsError):build(ROOT/"shared/fixtures/day62_tidy_a.csv",ROOT/"mainline/day62/config/table_a.json",o)
  t.cleanup()
if __name__=="__main__":unittest.main()
