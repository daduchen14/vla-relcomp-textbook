"""Day 12 免费 CPU 测试。"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mainline.day12.code.capture_event_frame import capture_frame
from mainline.day12.code.event_logger import summarize

ROOT = Path(__file__).resolve().parents[3]
CFG = ROOT / "mainline/day12/config/event_thresholds.json"
A = ROOT / "shared/fixtures/day12_frames_a.json"
B = ROOT / "shared/fixtures/day12_frames_b.json"


class FakeState:
    def __init__(self, pos, contact=False): self.pos, self.contact = pos, contact
    def get_geom_state(self): return {"pos": self.pos, "quat": [1, 0, 0, 0]}
    def check_gripper_contact(self): return self.contact


class FakeEnv:
    def __init__(self):
        self.object_states_dict = {"target": FakeState([0.03, 0.04, 0.8], True),
                                   "reference": FakeState([0, 0, 0.7])}


class Day12ToolTests(unittest.TestCase):
    def test_a_has_expected_ordered_first_steps(self):
        result = summarize(A, CFG)
        steps = [result["events"][name]["first_step"] for name in
                 ("target_contacted", "target_lifted", "reference_approached", "relation_satisfied")]
        self.assertEqual(steps, [2, 4, 7, 8]); self.assertEqual(result["anomalies"], [])

    def test_b_filters_flicker_and_keeps_relation_anomaly(self):
        result = summarize(B, CFG)
        self.assertEqual(result["events"]["target_contacted"]["first_step"], 5)
        self.assertEqual(result["events"]["target_lifted"]["first_step"], 5)
        self.assertEqual(result["events"]["relation_satisfied"]["first_step"], 8)
        self.assertEqual(result["events"]["reference_approached"]["first_step"], 9)
        self.assertEqual(result["anomalies"], ["relation_before_reference_approached"])

    def test_relation_is_not_erased_when_prior_probe_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = {"episode_id": "x", "target_object": "a", "reference_object": "b", "relation": "On",
                    "source_kind": "test", "frames": [{"step": 0, "target_z": 0.7,
                    "target_gripper_contact": False, "target_reference_xy_distance": 0.0,
                    "relation_satisfied": True}]}
            path = Path(tmp) / "x.json"; path.write_text(json.dumps(data))
            result = summarize(path, CFG)
        self.assertTrue(result["relation_satisfied"]); self.assertFalse(result["target_contacted"])
        self.assertIn("relation_before_target_contacted", result["anomalies"])

    def test_non_monotonic_steps_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(A.read_text()); data["frames"][1]["step"] = 0
            path = Path(tmp) / "x.json"; path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): summarize(path, CFG)

    def test_capture_frame_uses_info_success_not_done(self):
        frame = capture_frame(FakeEnv(), {"success": False}, target="target", reference="reference", step=3)
        self.assertAlmostEqual(frame["target_reference_xy_distance"], 0.05)
        self.assertTrue(frame["target_gripper_contact"]); self.assertFalse(frame["relation_satisfied"])
        with self.assertRaises(KeyError): capture_frame(FakeEnv(), {}, target="target", reference="reference", step=3)


if __name__ == "__main__": unittest.main()
