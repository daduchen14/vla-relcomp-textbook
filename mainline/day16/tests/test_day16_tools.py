"""Day 16 免费 CPU 测试。"""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from mainline.day16.code.build_registry import EPISODE_FIELDS, RUN_FIELDS, build, write_csv
from mainline.day16.code.validate_registry import read, validate

ROOT = Path(__file__).resolve().parents[3]
SPEC = ROOT / "shared/fixtures/day16_registry_spec_a.json"


def materialize(root: Path):
    runs, episodes, contract = build(SPEC); rp, ep, sp = root/"runs.csv", root/"episodes.csv", root/"schema.json"
    write_csv(rp, RUN_FIELDS, runs); write_csv(ep, EPISODE_FIELDS, episodes); sp.write_text(json.dumps(contract))
    return rp, ep, sp


class Day16Tests(unittest.TestCase):
    def test_valid_planned_registry(self):
        with tempfile.TemporaryDirectory() as tmp: result = validate(*materialize(Path(tmp)))
        self.assertEqual(result["planned_count"], 3)

    def test_duplicate_episode_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(SPEC.read_text()); data["episodes"].append(dict(data["episodes"][0]))
            path = Path(tmp)/"spec.json"; path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): build(path)

    def test_planned_success_zero_is_not_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            rp, ep, sp = materialize(Path(tmp)); rows = read(ep); rows[0]["success"] = "0"; write_csv(ep, EPISODE_FIELDS, rows)
            with self.assertRaises(ValueError): validate(rp, ep, sp)

    def test_dangling_run_foreign_key_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rp, ep, sp = materialize(Path(tmp)); rows = read(ep); rows[0]["run_id"] = "run-missing"; write_csv(ep, EPISODE_FIELDS, rows)
            with self.assertRaises(ValueError): validate(rp, ep, sp)

    def test_completed_requires_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            rp, ep, sp = materialize(Path(tmp)); rows = read(ep); rows[0]["status"] = "COMPLETED"; write_csv(ep, EPISODE_FIELDS, rows)
            with self.assertRaises(ValueError): validate(rp, ep, sp)


if __name__ == "__main__": unittest.main()
