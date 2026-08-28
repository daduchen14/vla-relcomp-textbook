"""Day 42 免费 CPU overfit 测试。"""
import unittest
from pathlib import Path
from mainline.day42.code.run_one_batch_overfit import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day42_one_batch_a.json";B=FIX/"day42_one_batch_b.json";CA=ROOT/"mainline/day42/config/overfit_config_a.json";CB=ROOT/"mainline/day42/config/overfit_config_b.json"
class Day42Tests(unittest.TestCase):
    def test_a_reaches_target(self):self.assertTrue(analyze(A,CA)[1]["target_reached"])
    def test_a_large_reduction(self):self.assertGreater(analyze(A,CA)[1]["loss_reduction_factor"],50)
    def test_adapter_changes(self):self.assertTrue(analyze(A,CA)[1]["adapter_changed"])
    def test_frozen_unchanged(self):self.assertTrue(analyze(A,CA)[1]["frozen_hashes_unchanged"])
    def test_b_new_trajectory(self):self.assertNotEqual(analyze(A,CA)[0],analyze(B,CB)[0])
if __name__=="__main__":unittest.main()
