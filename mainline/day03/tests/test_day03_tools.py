import tempfile
import unittest
from pathlib import Path

from mainline.day03.code.check_deliverables import check_challenge
from mainline.day03.code.summarize_observation import DEFAULT_INPUT, build_summary
from mainline.day03.code.trace_locked_evaluator import function_calls


class Day03ToolTests(unittest.TestCase):
    def test_fixture_summary_has_real_raw_keys_and_types(self):
        summary = build_summary(DEFAULT_INPUT)
        self.assertEqual(summary["arrays"]["agentview_image"]["shape"], [2, 2, 3])
        self.assertEqual(summary["arrays"]["agentview_image"]["dtype"], "uint8")
        self.assertEqual(summary["source_kind"], "local_fixture_not_vla_arena_run")

    def test_ast_call_extraction_does_not_import_upstream(self):
        source = "def run_episode(env, obs):\n    x = prepare_observation(obs)\n    return env.step(x)\n"
        self.assertEqual(function_calls(source, "run_episode"), {"prepare_observation", "env.step"})

    def test_missing_observation_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "broken.json"
            broken.write_text('{"fixture_id":"x","observation":{}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "缺少"):
                build_summary(broken)

    def test_copy_example_and_change_id_cannot_pass_challenge(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copied = build_summary(DEFAULT_INPUT)
            copied["fixture_id"] = "day03_observation_changed_input"
            summary = root / "challenge.json"
            summary.write_text(__import__("json").dumps(copied), encoding="utf-8")
            reasoning = root / "reasoning.md"
            reasoning.write_text(
                "[2,3,3] 与 [3,1,3] 是新图像 shape，state 使用 float64。" * 8
                + "这是 fixture，未运行真实环境。",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "不能复制"):
                check_challenge(summary, reasoning)


if __name__ == "__main__":
    unittest.main()
