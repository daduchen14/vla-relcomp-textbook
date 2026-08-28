"""Day 50 Gate 6 tests."""
import argparse,unittest
from pathlib import Path
from mainline.day50.code.run_gate6 import analyze
ROOT=Path(__file__).resolve().parents[3]
def args(suffix):
    return argparse.Namespace(split=ROOT/f"shared/fixtures/day45_split_{suffix}.json",base_plan=ROOT/f"mainline/day45/config/seed1_plan_{suffix}.json",repeat_plan=ROOT/f"mainline/day46/config/repeat_plan_{suffix}.json",stability=ROOT/f"shared/fixtures/day44_stability_{suffix}.json",candidate=ROOT/f"mainline/day44/config/candidate_recipe_{suffix}.json",l0_input=ROOT/f"shared/fixtures/day47_l0_retention_{suffix}.json",l0_config=ROOT/f"mainline/day47/config/retention_config_{suffix}.json",ood_input=ROOT/f"shared/fixtures/day48_ood_{suffix}.json",ood_config=ROOT/f"mainline/day48/config/ood_analysis_{suffix}.json",ablation_input=ROOT/f"shared/fixtures/day49_ablation_{suffix}.json",ablation_config=ROOT/f"mainline/day49/config/ablation_config_{suffix}.json")
class Day50Tests(unittest.TestCase):
    def test_missing_formal_evidence(self):self.assertFalse(analyze(args("a"))["criteria"]["formal_evidence_complete"])
    def test_stops_expansion(self):self.assertEqual(analyze(args("a"))["outcome"],"停止扩张")
    def test_gate_not_passed(self):self.assertFalse(analyze(args("a"))["gate6_passed"])
    def test_rebuilds_all_criteria(self):self.assertEqual(len(analyze(args("a"))["criteria"]),7)
    def test_b_new_sources(self):self.assertNotEqual(analyze(args("a"))["source_sha256"],analyze(args("b"))["source_sha256"])
if __name__=="__main__":unittest.main()
