"""Day 25 免费 CPU 测试。"""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from mainline.day25.code.reproduce_mini_baseline import ARTIFACTS, reproduce

ROOT = Path(__file__).resolve().parents[3]; FIX = ROOT / "shared/fixtures"
A = FIX / "day25_mini_spec_a.json"; B = FIX / "day25_mini_spec_b.json"


class Day25Tests(unittest.TestCase):
    def test_a_builds_package_from_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = reproduce(A, Path(tmp) / "out")
        self.assertEqual((receipt["task_count"], receipt["episode_count"]), (2, 4))

    def test_nonempty_directory_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"; output.mkdir(); (output / "old.txt").write_text("old")
            with self.assertRaises(ValueError): reproduce(A, output)

    def test_receipt_hashes_every_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"; receipt = reproduce(A, output)
            actual = {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in ARTIFACTS}
        self.assertEqual(receipt["artifact_sha256"], actual)

    def test_b_changes_tasks_and_episode_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = reproduce(B, Path(tmp) / "out")
        self.assertEqual((receipt["task_count"], receipt["episode_count"]), (2, 6))

    def test_wrong_locked_commit_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(A.read_text(encoding="utf-8")); data["locked_commit"] = "wrong"
            spec = Path(tmp) / "spec.json"; spec.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError): reproduce(spec, Path(tmp) / "out")


if __name__ == "__main__": unittest.main()
