import tempfile
import unittest
from pathlib import Path

from mainline.day10.code.build_success_contract import symbol_source
from mainline.day10.code.evaluate_predicate_fixture import evaluate, evaluate_case
from mainline.day10.code.minimal_done_success import evaluator_success


class Day10ToolTests(unittest.TestCase):
    def test_timeout_done_is_not_success_when_info_says_false(self):
        self.assertFalse(evaluator_success(True, {"success": False, "timeout": True}))

    def test_legacy_fallback_uses_done_only_without_success_key(self):
        self.assertTrue(evaluator_success(True, {"timeout": False}))

    def test_exact_xy_threshold_is_strictly_false(self):
        row = evaluate_case({"case_id": "edge", "reference_z": 0.8, "target_z": 0.9,
            "xy_distance": 0.07, "contact": True, "timeout_done": False})
        self.assertFalse(row["on_predicate"]); self.assertFalse(row["done"])

    def test_success_on_timeout_horizon_wins(self):
        rows = evaluate(Path("shared/fixtures/day10_predicate_b.json"))["cases"]
        case = next(row for row in rows if row["case_id"] == "success_on_horizon")
        self.assertTrue(case["done"]); self.assertTrue(case["evaluator_success"])
        self.assertFalse(case["info"]["timeout"])

    def test_symbol_source_selects_method_not_same_named_function(self):
        source = "class A:\n def f(self): return 1\nclass B:\n def f(self): return 2\n"
        self.assertIn("return 2", symbol_source(source, "B", "f"))


if __name__ == "__main__": unittest.main()
