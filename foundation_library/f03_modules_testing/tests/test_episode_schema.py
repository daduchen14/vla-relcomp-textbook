"""Day 3 单元测试：用极小输入验证 episode 数据契约。"""

import csv
import tempfile
import unittest
from pathlib import Path

# 测试命令从仓库根目录运行，所以可以直接导入 foundation_library 包中的模块。
from foundation_library.f03_modules_testing.code.episode_schema import SchemaError, load_episodes, run


FIELDNAMES = ["episode_id", "level", "task_id", "seed", "relation", "success", "steps"]


def valid_row() -> dict[str, str]:
    """每次返回新字典，避免某个测试的修改污染其他测试。"""
    return {
        "episode_id": "fixture_test_001",
        "task_id": "fixture_left_of",
        "level": "1",
        "seed": "7",
        "success": "1",
        "steps": "42",
        "relation": "left",
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """把测试输入写入临时目录，不污染教材或学习者输出。"""
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


class EpisodeSchemaTests(unittest.TestCase):
    """每个方法只验证一条容易说清楚的规则。"""

    def test_valid_csv_converts_types_and_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "episodes.csv"
            output_path = Path(directory) / "manifest.json"
            write_csv(input_path, [valid_row()])

            manifest = run(input_path, output_path)

            self.assertEqual(manifest["episode_count"], 1)
            self.assertIs(manifest["episodes"][0]["success"], True)
            self.assertEqual(manifest["episodes"][0]["seed"], 7)
            self.assertTrue(output_path.is_file())

    def test_non_fixture_episode_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "episodes.csv"
            row = valid_row()
            row["episode_id"] = "real_looking_id"
            write_csv(input_path, [row])

            with self.assertRaisesRegex(SchemaError, "fixture_"):
                load_episodes(input_path)

    def test_invalid_level_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "episodes.csv"
            row = valid_row()
            row["level"] = "9"
            write_csv(input_path, [row])

            with self.assertRaisesRegex(SchemaError, "level"):
                load_episodes(input_path)

    def test_duplicate_episode_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "episodes.csv"
            output_path = Path(directory) / "manifest.json"
            row = valid_row()
            write_csv(input_path, [row, row])

            with self.assertRaisesRegex(SchemaError, "重复"):
                run(input_path, output_path)


if __name__ == "__main__":
    unittest.main()
