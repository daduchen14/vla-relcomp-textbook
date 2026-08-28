"""Day 28 免费 CPU 测试。"""
import tempfile,unittest
from pathlib import Path
from mainline.day28.code.analyze_lift_probe import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=(FIX/"day28_lift_trace_a.csv",FIX/"day28_lift_config_a.json");B=(FIX/"day28_lift_trace_b.csv",FIX/"day28_lift_config_b.json")
class Day28Tests(unittest.TestCase):
    def test_grasp_then_lift(self):
        rows,_,_,_=analyze(*A);self.assertEqual(rows[0]["probe_status"],"GRASP_AND_LIFT")
    def test_physical_lift_without_bilateral_is_gap(self):
        rows,_,_,_=analyze(*A);self.assertEqual(rows[1]["probe_status"],"LIFT_WITHOUT_BILATERAL_CONTACT")
    def test_bilateral_without_lift_preserved(self):
        rows,_,_,_=analyze(*A);self.assertEqual(rows[2]["probe_status"],"BILATERAL_NO_LIFT")
    def test_b_requires_three_sustained_steps(self):
        rows,_,_,_=analyze(*B);self.assertEqual(rows[1]["lift_detected"],"false")
    def test_bad_contact_bit_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.csv";path.write_text(A[0].read_text().replace(",1,1,1\n",",2,1,1\n",1))
            with self.assertRaises(ValueError):analyze(path,A[1])
if __name__=="__main__":unittest.main()
