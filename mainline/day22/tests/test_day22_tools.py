"""Day 22 免费 CPU 测试。"""

import tempfile
import unittest
from pathlib import Path

from mainline.day22.code.compute_baseline_stats import compute, wilson

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "shared/fixtures/day22_episode_results_a.csv"
B = ROOT / "shared/fixtures/day22_episode_results_b.csv"


class Day22Tests(unittest.TestCase):
    def test_wilson_zero_of_one_not_zero_width(self):
        low, high = wilson(0, 1); self.assertEqual(low, 0.0); self.assertGreater(high, 0.7)

    def test_a_preserves_missing_and_denominator(self):
        rows, report = compute(A)
        self.assertEqual((report["successes"], report["valid_n"], report["missing_n"]), (4, 10, 1))
        self.assertEqual(len(rows), 5)

    def test_macro_and_micro_can_differ(self):
        _, report = compute(A)
        self.assertEqual(report["micro"]["success_rate"], "0.400000")
        self.assertEqual(report["macro"]["success_rate"], "0.500000")

    def test_b_is_new_distribution(self):
        _, report = compute(B); self.assertEqual(report["micro"]["success_rate"], "0.555556")

    def test_completed_missing_success_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text("episode_id,task_id,status,success\ne1,0,COMPLETED,\n", encoding="utf-8")
            with self.assertRaises(ValueError): compute(path)


if __name__ == "__main__": unittest.main()
