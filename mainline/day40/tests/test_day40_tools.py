"""Day 40 免费 CPU 测试。"""
import unittest
from pathlib import Path
from mainline.day40.code.build_trainability_report import analyze
ROOT=Path(__file__).resolve().parents[3];FIX=ROOT/"shared/fixtures";A=FIX/"day40_trainability_a.json";B=FIX/"day40_trainability_b.json";CA=ROOT/"mainline/day40/config/trainability_config_a.json";CB=ROOT/"mainline/day40/config/trainability_config_b.json"
class Day40Tests(unittest.TestCase):
    def test_only_adapter_trainable(self):self.assertEqual(analyze(A,CA)["trainable_parameter_names"],["relation_adapter.weight"])
    def test_frozen_have_no_grad(self):self.assertEqual(analyze(A,CA)["frozen_grad_count"],0)
    def test_adapter_has_gradient(self):self.assertGreater(analyze(A,CA)["parameters"][2]["grad_norm"],0.0)
    def test_no_optimizer_step(self):self.assertFalse(analyze(A,CA)["optimizer_step_run"])
    def test_b_new_loss(self):self.assertNotEqual(analyze(A,CA)["loss"],analyze(B,CB)["loss"])
if __name__=="__main__":unittest.main()
