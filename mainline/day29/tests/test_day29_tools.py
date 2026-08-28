"""Day 29 免费 CPU 测试。"""
import tempfile,unittest
from pathlib import Path
from mainline.day29.code.analyze_approach_probe import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=(FIX/"day29_approach_trace_a.csv",FIX/"day29_approach_config_a.json");B=(FIX/"day29_approach_trace_b.csv",FIX/"day29_approach_config_b.json")
class Day29Tests(unittest.TestCase):
    def test_correct_reference_entry(self):self.assertEqual(analyze(*A)[0][0]["probe_status"],"APPROACHED_REFERENCE")
    def test_wrong_reference_attraction(self):self.assertEqual(analyze(*A)[0][1]["probe_status"],"WRONG_REFERENCE_ATTRACTION")
    def test_progress_without_entry(self):self.assertEqual(analyze(*A)[0][2]["probe_status"],"PROGRESS_NO_ENTRY")
    def test_no_lifted_segment(self):self.assertEqual(analyze(*A)[0][3]["probe_status"],"NO_LIFTED_SEGMENT")
    def test_b_requires_three_entry_steps(self):self.assertEqual(analyze(*B)[0][0]["probe_status"],"APPROACHED_REFERENCE")
if __name__=="__main__":unittest.main()
