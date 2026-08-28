"""Day 60 results-lock tests."""
import unittest
from pathlib import Path
from mainline.day60.code.build_results_lock import analyze

ROOT=Path(__file__).resolve().parents[3]
def report(suffix):
    return analyze(ROOT/f"shared/fixtures/day60_claims_{suffix}.json",ROOT/f"mainline/day60/config/results_lock_{suffix}.json")

class Day60Tests(unittest.TestCase):
    def test_three_random_claims(self): self.assertEqual(len(report("a")["selected_claims"]),3)
    def test_links_complete(self): self.assertTrue(report("a")["criteria"]["claim_evidence_links_complete"])
    def test_negative_result_preserved(self): self.assertGreater(report("a")["negative_result_count"],0)
    def test_formal_missing_stops(self): self.assertEqual(report("a")["outcome"],"停止扩张")
    def test_gate_not_passed(self): self.assertFalse(report("a")["gate7_passed"])
    def test_b_is_new(self): self.assertNotEqual(report("a")["source_sha256"],report("b")["source_sha256"])

if __name__ == "__main__": unittest.main()
