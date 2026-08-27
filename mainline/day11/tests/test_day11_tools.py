"""Day 11 免费 CPU 测试。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mainline.day11.code.capture_vla_state import capture_state
from mainline.day11.code.snapshot_fixture import snapshot


ROOT = Path(__file__).resolve().parents[3]


def task_table(path: Path) -> Path:
    rows = [
        {"level": 0, "task_id": 0, "task_name": "a", "goal_predicate": ["On", "tomato_3", "bowl_3"],
         "target_object": "tomato_3", "reference_object": "bowl_3"},
        {"level": 2, "task_id": 3, "task_name": "b", "goal_predicate": ["On", "tomato_2", "bowl_2"],
         "target_object": "tomato_2", "reference_object": "bowl_2"},
    ]
    path.write_text(json.dumps({"commit": "locked", "suite": "suite", "tasks": rows}), encoding="utf-8")
    return path


class FakeState:
    def __init__(self, pos, quat, contact=False): self.pos, self.quat, self.contact = pos, quat, contact
    def get_geom_state(self): return {"pos": self.pos, "quat": self.quat}
    def check_contact(self, other): return self.contact


class FakeEnv:
    def __init__(self):
        self.object_states_dict = {
            "target": FakeState([0.01, 0.02, 0.80], [1, 0, 0, 0]),
            "reference": FakeState([0.00, 0.00, 0.76], [1, 0, 0, 0], True),
        }
        self.obj_body_id = {"target": 7, "reference": 9}


class FakeControlEnv:
    def __init__(self): self.env = FakeEnv()


class Day11ToolTests(unittest.TestCase):
    def test_real_adapter_uses_reference_contact_and_marks_privileged(self):
        result = capture_state(FakeControlEnv(), target="target", reference="reference", step=4)
        self.assertTrue(result["contact"]); self.assertTrue(result["on_by_locked_formula"])
        self.assertEqual(result["target_body_id"], 7)
        self.assertEqual(result["visibility"], "privileged_evaluator_state_not_policy_input")

    def test_adapter_rejects_missing_goal_object(self):
        with self.assertRaises(KeyError): capture_state(FakeEnv(), target="missing", reference="reference", step=0)

    def test_snapshot_derives_names_from_task_not_object_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            table = task_table(Path(tmp) / "table.json")
            fixture = {"task_selector": {"level": 2, "task_id": 3}, "objects": {
                "distractor": {"body_id": 1, "pos": [9, 9, 9], "quat_wxyz": [1, 0, 0, 0]},
                "bowl_2": {"body_id": 4, "pos": [0, 0, 0.8], "quat_wxyz": [1, 0, 0, 0]},
                "tomato_2": {"body_id": 3, "pos": [0, 0, 0.7], "quat_wxyz": [1, 0, 0, 0]}},
                "contacts": [["bowl_2", "tomato_2"]], "source_kind": "test"}
            path = Path(tmp) / "fixture.json"; path.write_text(json.dumps(fixture))
            result = snapshot(table, path)
        self.assertEqual((result["target"], result["reference"]), ("tomato_2", "bowl_2"))
        self.assertFalse(result["relation_state"]["on_by_locked_formula"])

    def test_contact_pair_order_is_irrelevant(self):
        with tempfile.TemporaryDirectory() as tmp:
            table = task_table(Path(tmp) / "table.json")
            fixture = {"task_selector": {"level": 0, "task_id": 0}, "objects": {
                "tomato_3": {"body_id": 2, "pos": [0, 0, 0.8], "quat_wxyz": [1, 0, 0, 0]},
                "bowl_3": {"body_id": 3, "pos": [0, 0, 0.7], "quat_wxyz": [1, 0, 0, 0]}},
                "contacts": [["bowl_3", "tomato_3"]], "source_kind": "test"}
            path = Path(tmp) / "fixture.json"; path.write_text(json.dumps(fixture))
            result = snapshot(table, path)
        self.assertTrue(result["relation_state"]["contact"])

    def test_body_id_collision_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            table = task_table(Path(tmp) / "table.json")
            fixture = {"task_selector": {"level": 0, "task_id": 0}, "objects": {
                "tomato_3": {"body_id": 2, "pos": [0, 0, 0.8], "quat_wxyz": [1, 0, 0, 0]},
                "bowl_3": {"body_id": 2, "pos": [0, 0, 0.7], "quat_wxyz": [1, 0, 0, 0]}},
                "contacts": [], "source_kind": "test"}
            path = Path(tmp) / "fixture.json"; path.write_text(json.dumps(fixture))
            with self.assertRaises(ValueError): snapshot(table, path)


if __name__ == "__main__": unittest.main()
