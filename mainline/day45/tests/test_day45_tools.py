"""Day 45 seed-1 packet tests."""
import unittest
from pathlib import Path
from mainline.day45.code.prepare_seed1_launch import analyze
ROOT=Path(__file__).resolve().parents[3]
ARGS_A=(ROOT/"shared/fixtures/day45_split_a.json",ROOT/"mainline/day45/config/seed1_plan_a.json",ROOT/"shared/fixtures/day44_stability_a.json",ROOT/"mainline/day44/config/candidate_recipe_a.json")
ARGS_B=(ROOT/"shared/fixtures/day45_split_b.json",ROOT/"mainline/day45/config/seed1_plan_b.json",ROOT/"shared/fixtures/day44_stability_b.json",ROOT/"mainline/day44/config/candidate_recipe_b.json")
class Day45Tests(unittest.TestCase):
    def test_seed_one(self):self.assertEqual(analyze(*ARGS_A)[0]["seed"],1)
    def test_test_isolated(self):self.assertTrue(analyze(*ARGS_A)[0]["test_isolated"])
    def test_no_test_access(self):self.assertEqual(analyze(*ARGS_A)[0]["test_access_log"],[])
    def test_checkpoint_not_faked(self):
        contract=analyze(*ARGS_A)[1];self.assertIsNone(contract["checkpoint_sha256"]);self.assertFalse(contract["formal_training_evidence"])
    def test_b_new_split(self):self.assertNotEqual(analyze(*ARGS_A)[0]["split_sha256"],analyze(*ARGS_B)[0]["split_sha256"])
if __name__=="__main__":unittest.main()
