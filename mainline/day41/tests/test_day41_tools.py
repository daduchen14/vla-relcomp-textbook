"""Day 41 免费 CPU 配置测试。"""
import unittest
from pathlib import Path
from mainline.day41.code.validate_bounded_train_config import analyze
ROOT=Path(__file__).resolve().parents[3];A=ROOT/"mainline/day41/config/bounded_train_config_a.json";B=ROOT/"mainline/day41/config/bounded_train_config_b.json"
class Day41Tests(unittest.TestCase):
    def test_a_global_batch(self):self.assertEqual(analyze(A)["global_batch_size"],16)
    def test_a_checkpoint_count(self):self.assertEqual(analyze(A)["planned_checkpoint_count"],4)
    def test_headroom(self):self.assertGreaterEqual(analyze(A)["planning_headroom_fraction"],0.20)
    def test_lora_not_selected(self):self.assertFalse(analyze(A)["lora_enabled"])
    def test_b_new_plan(self):self.assertNotEqual(analyze(A)["global_batch_size"],analyze(B)["global_batch_size"])
if __name__=="__main__":unittest.main()
