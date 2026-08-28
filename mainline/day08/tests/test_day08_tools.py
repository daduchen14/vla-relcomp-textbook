import json
import tempfile
import unittest
from pathlib import Path

from mainline.day08.code.build_pilot_matrix import LOCKED, build
from mainline.day08.code.check_day08 import check_gate
from mainline.day08.code.minimal_denominator import ROWS, summarize as mini_summarize
from mainline.day08.code.select_diagnostic_model import summarize


class Day08ToolTests(unittest.TestCase):
    def fake_manifests(self, root: Path) -> tuple[Path, Path]:
        base = {"upstream_commit": LOCKED, "real_model_run": False,
                "checkpoint_repo": "fixture/model", "checkpoint_revision": "a" * 40}
        smol, openvla = root / "smol.json", root / "open.json"
        smol.write_text(json.dumps({**base, "source_kind": "locked_source_static_pilot_plan"}))
        openvla.write_text(json.dumps({**base, "checkpoint_revision": "b" * 40,
                                      "source_kind": "locked_source_static_openvla_plan"}))
        return smol, openvla

    def test_matrix_has_150_unique_planned_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            smol, openvla = self.fake_manifests(Path(tmp))
            matrix = build(Path("mainline/day08/config/pilot_matrix.json"), smol, openvla)
            self.assertEqual(len(matrix["episodes"]), 150)
            self.assertEqual(len({row["episode_id"] for row in matrix["episodes"]}), 150)
            self.assertTrue(all(not row["real_model_run"] for row in matrix["episodes"]))

    def test_minimal_denominator_excludes_error_and_missing_evidence(self):
        successes, denominator, excluded = mini_summarize(ROWS)
        self.assertEqual((successes, denominator), (1, 2)); self.assertEqual(excluded, ["e3", "e4"])

    def test_gate_fixture_uses_l0_not_l1_l2(self):
        report = summarize(Path("shared/fixtures/day08_gate2_results.csv"))
        self.assertEqual(report["selected_model"], "candidate_cobalt")
        self.assertEqual(report["models"]["candidate_amber"]["levels"]["1"]["successes"], 20)
        self.assertFalse(report["rule"]["l1_l2_performance_used_for_selection"])
        self.assertTrue(report["models"]["candidate_cobalt"]["pilot_complete_75"])

    def test_gate_answer_requires_exact_denominators_and_exclusions(self):
        report = summarize(Path("shared/fixtures/day08_gate2_results.csv"))
        with tempfile.TemporaryDirectory() as tmp:
            answer = Path(tmp) / "answer.json"
            answer.write_text(json.dumps({"selected_model": "candidate_cobalt",
                "excluded_episode_ids": report["excluded_episode_ids"],
                "valid_denominators": {m: {level: stats["valid"] for level, stats in data["levels"].items()}
                                       for m, data in report["models"].items()},
                "next_minimal_experiment": "固定 candidate_cobalt、L0 task 0 和 seed 101 以及 init state，只解析任务结构并建立对象关系表，不增加模型、suite 或新的 GPU 运行。"}, ensure_ascii=False))
            check_gate(report, answer)


if __name__ == "__main__": unittest.main()
