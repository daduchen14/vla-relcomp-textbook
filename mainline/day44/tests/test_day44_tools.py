"""Day 44 免费 CPU 稳定性测试。"""
import unittest
from pathlib import Path
from mainline.day44.code.audit_and_freeze_recipe import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"shared/fixtures/day44_stability_a.json";CA=ROOT/"mainline/day44/config/candidate_recipe_a.json";B=ROOT/"shared/fixtures/day44_stability_b.json";CB=ROOT/"mainline/day44/config/candidate_recipe_b.json"
class Day44Tests(unittest.TestCase):
    def test_a_all_finite(self):self.assertTrue(analyze(A,CA)[0]["all_finite"])
    def test_a_within_spread(self):self.assertTrue(analyze(A,CA)[0]["within_spread_limit"])
    def test_nan_aborts_before_step(self):
        anomaly=analyze(A,CA)[0]["anomaly_test"];self.assertTrue(anomaly["caught_before_backward"]);self.assertFalse(anomaly["optimizer_step_executed"]);self.assertTrue(anomaly["adapter_unchanged"])
    def test_recipe_not_authorized(self):self.assertFalse(analyze(A,CA)[1]["authorized_for_formal_training"])
    def test_b_has_new_recipe_hash(self):self.assertNotEqual(analyze(A,CA)[1]["recipe_sha256"],analyze(B,CB)[1]["recipe_sha256"])
if __name__=="__main__":unittest.main()
