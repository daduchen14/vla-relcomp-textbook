import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mainline.day01.code.build_project_map import FILES, LOCKED, SUITE, build_map
from mainline.day01.code.check_day01 import top_level_symbols


class Day01ToolTests(unittest.TestCase):
    def test_build_map_requires_every_real_node(self):
        with tempfile.TemporaryDirectory() as tmp, patch(
            "mainline.day01.code.build_project_map.git_head", return_value=LOCKED
        ):
            root = Path(tmp)
            for path in FILES.values():
                target = root / path
                target.mkdir(parents=True, exist_ok=True) if path == FILES["tasks"] else target.parent.mkdir(parents=True, exist_ok=True)
                if path != FILES["tasks"]:
                    target.write_text(f"{SUITE}\nrun_episode\n", encoding="utf-8")
            payload = build_map(root)
            self.assertEqual(payload["commit"], LOCKED)
            self.assertEqual(len(payload["nodes"]), 7)

    def test_wrong_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, patch(
            "mainline.day01.code.build_project_map.git_head", return_value="0" * 40
        ):
            with self.assertRaisesRegex(ValueError, "版本不匹配"):
                build_map(Path(tmp))

    def test_symbol_reader_only_uses_top_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "adapter.py"
            source.write_text("class Args: pass\ndef main(): pass\n", encoding="utf-8")
            self.assertEqual(top_level_symbols(source), {"Args", "main"})


if __name__ == "__main__":
    unittest.main()
