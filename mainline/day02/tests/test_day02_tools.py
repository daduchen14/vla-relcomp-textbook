import tempfile
import unittest
from pathlib import Path

from mainline.day02.code.trace_config import extract_task_map, parse_simple_yaml


class Day02ToolTests(unittest.TestCase):
    def test_simple_yaml_preserves_bool_int_and_string(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.yaml"
            path.write_text("suite: target\nlevel: 2\nlocal: false\n", encoding="utf-8")
            self.assertEqual(parse_simple_yaml(path), {"suite": "target", "level": 2, "local": False})

    def test_task_map_is_read_without_importing_torch(self):
        source = "vla_arena_task_map = {'suite': {0: ['a'], 1: ['b'], 2: ['c']}}\n"
        self.assertEqual(extract_task_map(source)["suite"][2], ["c"])

    def test_missing_task_map_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "找不到"):
            extract_task_map("OTHER = {}\n")


if __name__ == "__main__":
    unittest.main()
