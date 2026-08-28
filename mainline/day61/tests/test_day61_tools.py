import json,tempfile,unittest
from pathlib import Path
from mainline.day61.code.build_release_candidate import build
ROOT=Path(__file__).resolve().parents[3]
class Day61Tests(unittest.TestCase):
 def make(self,s):
  tmp=tempfile.TemporaryDirectory();out=Path(tmp.name)/"release";m=build(ROOT/f"shared/fixtures/day61_episodes_{s}.json",ROOT/f"mainline/day61/config/release_{s}.json",out);return tmp,out,m
 def test_a_rows(self):
  t,o,m=self.make("a");self.assertEqual(m["row_count"],4);t.cleanup()
 def test_source_unchanged(self):
  t,o,m=self.make("a");self.assertTrue(m["source_unchanged"]);t.cleanup()
 def test_provenance(self):
  t,o,m=self.make("a");self.assertEqual(len(json.loads((o/"provenance_index.json").read_text())["rows"]),4);t.cleanup()
 def test_no_overwrite(self):
  t,o,m=self.make("a")
  with self.assertRaises(FileExistsError):build(ROOT/"shared/fixtures/day61_episodes_a.json",ROOT/"mainline/day61/config/release_a.json",o)
  t.cleanup()
 def test_not_formal(self):
  t,o,m=self.make("b");self.assertFalse(m["formal_results"]);t.cleanup()
if __name__=="__main__":unittest.main()
