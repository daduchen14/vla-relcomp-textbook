import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
