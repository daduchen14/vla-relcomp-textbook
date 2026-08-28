"""Day 27 免费 CPU 测试。"""
import tempfile, unittest
from pathlib import Path
from mainline.day27.code.analyze_target_probe import analyze
ROOT=Path(__file__).resolve().parents[3]; FIX=ROOT/"shared/fixtures"; A=(FIX/"day27_target_trace_a.csv",FIX/"day27_target_config_a.json"); B=(FIX/"day27_target_trace_b.csv",FIX/"day27_target_config_b.json")
class Day27Tests(unittest.TestCase):
    def test_near_and_contact_are_separate(self):
        rows,_,_=analyze(*A); a1=next(row for row in rows if row["episode_id"]=="a1"); self.assertEqual((a1["near_detected"],a1["target_contact_detected"]),("true","true"))
    def test_wrong_object_is_preserved(self):
        rows,_,_=analyze(*A); a2=next(row for row in rows if row["episode_id"]=="a2"); self.assertEqual(a2["probe_status"],"WRONG_OBJECT_ONLY")
    def test_single_frame_does_not_pass_sustained(self):
        rows,_,_=analyze(*A); a3=next(row for row in rows if row["episode_id"]=="a3"); self.assertEqual(a3["near_detected"],"false")
    def test_b_wrong_first_then_target(self):
        rows,_,_=analyze(*B); b2=next(row for row in rows if row["episode_id"]=="b2"); self.assertEqual(b2["probe_status"],"WRONG_OBJECT_FIRST_THEN_TARGET")
    def test_non_contiguous_steps_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.csv"; path.write_text((A[0]).read_text().replace("a1,2,","a1,5,",1))
            with self.assertRaises(ValueError): analyze(path,A[1])
if __name__=="__main__": unittest.main()
