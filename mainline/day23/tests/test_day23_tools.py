"""Day 23 免费 CPU 测试。"""

import tempfile
import unittest
from pathlib import Path

from mainline.day23.code.build_evidence_index import build

ROOT = Path(__file__).resolve().parents[3]


def paths(suffix: str):
    base = ROOT / "shared/fixtures"
    return tuple(base / f"day23_{name}_{suffix}.csv" for name in ("registry", "videos", "stages", "exceptions"))


class Day23Tests(unittest.TestCase):
    def test_left_join_preserves_registry_rows(self):
        rows, report = build(*paths("a")); self.assertEqual(len(rows), 5); self.assertTrue(report["cardinality_preserved"])

    def test_a_keeps_four_triage_states(self):
        _, report = build(*paths("a"))
        self.assertTrue({"RUN_ERROR", "INCOMPLETE_EVIDENCE", "SIGNAL_CONFLICT", "COMPLETE_FAILURE"}.issubset(report["evidence_state_counts"]))

    def test_missing_stage_is_not_failure_rewrite(self):
        rows, _ = build(*paths("b")); row = next(item for item in rows if item["episode_id"] == "q4")
        self.assertEqual((row["success"], row["evidence_state"]), ("1", "INCOMPLETE_EVIDENCE"))

    def test_duplicate_video_rejected(self):
        registry, videos, stages, exceptions = paths("a")
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "videos.csv"; lines = videos.read_text(encoding="utf-8").splitlines()
            bad.write_text("\n".join(lines + [lines[1]]) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError): build(registry, bad, stages, exceptions)

    def test_orphan_stage_rejected(self):
        registry, videos, stages, exceptions = paths("b")
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "stages.csv"
            bad.write_text(stages.read_text(encoding="utf-8") + "ghost,1,1,1,1\n", encoding="utf-8")
            with self.assertRaises(ValueError): build(registry, videos, bad, exceptions)


if __name__ == "__main__": unittest.main()
