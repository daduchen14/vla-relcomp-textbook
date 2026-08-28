import tempfile
import unittest
from collections import deque
from pathlib import Path

from mainline.day09.code.build_task_structures import parse_one, parse_sexpr, structure
from mainline.day09.code.extract_fixture import extract


class Day09ToolTests(unittest.TestCase):
    def test_minimal_parser_builds_nested_goal(self):
        tree = parse_sexpr("(:goal (And (On tomato_1 bowl_1)))")
        self.assertEqual(tree[1][1], ["On", "tomato_1", "bowl_1"])

    def test_missing_right_parenthesis_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "右括号"):
            parse_one(deque(["(", ":goal", "(", "On", "a", "b", ")"]))

    def test_structure_uses_goal_not_interest_as_target(self):
        data = extract(Path("shared/fixtures/day09_challenge.bddl"))
        self.assertEqual(data["goal_predicate"], ["In", "apple_1", "bowl_1"])
        self.assertEqual(data["obj_of_interest"], ["apple_2"])
        self.assertFalse(data["goal_args_covered_by_obj_of_interest"])

    def test_single_goal_and_initial_placements(self):
        text = """(define (problem x) (:language move a into b) (:fixtures table - table)
        (:objects a - apple b - bowl) (:obj_of_interest a b)
        (:init (On a table_left) (On b table_right)) (:goal (And (In a b))))"""
        data = structure(text, 0, 0, "x", "fixture", "unit_fixture")
        self.assertEqual(data["target_initial_predicate"], ["On", "a", "table_left"])
        self.assertEqual(data["reference_initial_predicate"], ["On", "b", "table_right"])


if __name__ == "__main__": unittest.main()
