"""Day 30 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day30.code.analyze_relation_probe import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=(FIX/"day30_relation_trace_a.csv",FIX/"day30_relation_config_a.json");B=(FIX/"day30_relation_trace_b.csv",FIX/"day30_relation_config_b.json")
class Day30Tests(unittest.TestCase):
    def test_stable_after_release(self):
        row=analyze(*A)[0][0];self.assertEqual((row["probe_status"],row["first_stable_relation_step"]),("STABLE_RELATION",2))
    def test_true_but_not_released(self):self.assertEqual(analyze(*A)[0][1]["probe_status"],"PREDICATE_TRUE_NOT_RELEASED")
    def test_transient_predicate(self):self.assertEqual(analyze(*A)[0][2]["probe_status"],"TRANSIENT_RELATION")
    def test_proxy_does_not_override_official(self):
        row=analyze(*A)[0][3];self.assertEqual((row["probe_status"],row["signal_conflict"]),("PROXY_ONLY_CONFLICT","PROXY_ONLY"))
    def test_b_official_only_conflict(self):
        row=analyze(*B)[0][2];self.assertEqual((row["probe_status"],row["signal_conflict"]),("STABLE_RELATION","OFFICIAL_ONLY"))
if __name__=="__main__":unittest.main()
