"""Day 46 repeat-plan tests."""
import unittest
from pathlib import Path
from mainline.day46.code.prepare_repeat_launches import analyze
ROOT=Path(__file__).resolve().parents[3]
A=(ROOT/"shared/fixtures/day45_split_a.json",ROOT/"mainline/day45/config/seed1_plan_a.json",ROOT/"mainline/day46/config/repeat_plan_a.json",ROOT/"shared/fixtures/day44_stability_a.json",ROOT/"mainline/day44/config/candidate_recipe_a.json")
B=(ROOT/"shared/fixtures/day45_split_b.json",ROOT/"mainline/day45/config/seed1_plan_b.json",ROOT/"mainline/day46/config/repeat_plan_b.json",ROOT/"shared/fixtures/day44_stability_b.json",ROOT/"mainline/day44/config/candidate_recipe_b.json")
class Day46Tests(unittest.TestCase):
    def test_registered_seeds(self):self.assertEqual(analyze(*A)["all_registered_seeds"],[1,2,3])
    def test_same_recipe_and_split(self):self.assertTrue(analyze(*A)["same_recipe_for_all"] and analyze(*A)["same_split_for_all"])
    def test_budget_bounded(self):
        result=analyze(*A);self.assertLessEqual(result["total_planned_gpu_hours"],result["total_gpu_hours_cap"])
    def test_no_fake_results(self):
        result=analyze(*A);self.assertIsNone(result["variance_policy"]["metrics"]);self.assertFalse(result["formal_checkpoints_produced"])
    def test_b_new_identity(self):self.assertNotEqual(analyze(*A)["runs"][0]["recipe_sha256"],analyze(*B)["runs"][0]["recipe_sha256"])
if __name__=="__main__":unittest.main()
