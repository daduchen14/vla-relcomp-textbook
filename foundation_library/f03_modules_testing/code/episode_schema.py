"""Day 3 工程版本：集中定义并校验合成 episode 的数据契约。

本模块只处理 fixture_ 教学数据，不产生或代表任何真实 VLA 实验结果。
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping


# 合法集合只在一处定义，避免读取、测试和命令行各写一份而逐渐不一致。
VALID_LEVEL_TEXT = frozenset({"0", "1", "2"})
VALID_SUCCESS_TEXT = frozenset({"0", "1"})

# CSV 的最小输入契约。集合适合检查“缺哪些列”，不依赖列的排列顺序。
REQUIRED_COLUMNS = frozenset(
    {"episode_id", "task_id", "level", "seed", "relation", "success", "steps"}
)


class SchemaError(ValueError):
    """输入数据违反 episode 契约时抛出的、可被上层明确捕获的异常。"""


@dataclass(frozen=True)
class Episode:
    """一条经过校验、类型明确的合成教学 episode。"""

    episode_id: str
    task_id: str
    level: str
    seed: int
    success: bool
    steps: int
    relation: str

    def to_record(self) -> dict[str, object]:
        """转换成可写入 JSON 的普通字典，并附加真实性声明。"""
        record = asdict(self)
        record["result_type"] = "synthetic teaching data; not a VLA result"
        return record


def require_non_empty(row: Mapping[str, str], field: str, row_number: int) -> str:
    """读取并清理必填文本；为空时给出行号和字段名。"""
    value = row.get(field, "").strip()
    if not value:
        raise SchemaError(f"第 {row_number} 行：{field} 不能为空")
    return value


def parse_non_negative_int(text: str, field: str, row_number: int) -> int:
    """把文本转成非负整数，同时把底层错误翻译成领域错误。"""
    try:
        value = int(text)
    except ValueError as error:
        raise SchemaError(
            f"第 {row_number} 行：{field}={text!r} 不是整数"
        ) from error
    if value < 0:
        raise SchemaError(f"第 {row_number} 行：{field} 不能为负数")
    return value


def parse_row(row: Mapping[str, str], row_number: int) -> Episode:
    """把 CSV 的一行字符串映射为经过校验的 Episode。"""
    episode_id = require_non_empty(row, "episode_id", row_number)
    if not episode_id.startswith("fixture_"):
        raise SchemaError(
            f"第 {row_number} 行：episode_id 必须以 fixture_ 开头"
        )

    task_id = require_non_empty(row, "task_id", row_number)
    if not task_id.startswith("fixture_"):
        raise SchemaError(f"第 {row_number} 行：task_id 必须以 fixture_ 开头")

    level_text = require_non_empty(row, "level", row_number)
    if level_text not in VALID_LEVEL_TEXT:
        raise SchemaError(
            f"第 {row_number} 行：level={level_text!r}，CSV 中只能是 0、1、2"
        )

    success_text = require_non_empty(row, "success", row_number)
    if success_text not in VALID_SUCCESS_TEXT:
        raise SchemaError(f"第 {row_number} 行：success 只能是 0 或 1")

    seed = parse_non_negative_int(
        require_non_empty(row, "seed", row_number), "seed", row_number
    )
    steps = parse_non_negative_int(
        require_non_empty(row, "steps", row_number), "steps", row_number
    )

    relation = require_non_empty(row, "relation", row_number)
    return Episode(
        episode_id=episode_id,
        task_id=task_id,
        level=f"L{level_text}",
        seed=seed,
        success=success_text == "1",
        steps=steps,
        relation=relation,
    )


def load_episodes(csv_path: Path) -> list[Episode]:
    """读取完整 CSV；先检查表头，再逐行解析。"""
    if not csv_path.is_file():
        raise SchemaError(f"输入文件不存在：{csv_path}")

    with csv_path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        actual_columns = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - actual_columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise SchemaError(f"CSV 缺少列：{missing}")

        # CSV 第 1 行是表头，因此第一条数据在人类看到的第 2 行。
        episodes = [parse_row(row, row_number) for row_number, row in enumerate(reader, 2)]

    if not episodes:
        raise SchemaError("CSV 只有表头，没有 episode 数据")
    return episodes


def ensure_unique_ids(episodes: Iterable[Episode]) -> None:
    """保证 episode_id 全局唯一，防止汇总时把重复行当成独立试验。"""
    seen: set[str] = set()
    for episode in episodes:
        if episode.episode_id in seen:
            raise SchemaError(f"episode_id 重复：{episode.episode_id}")
        seen.add(episode.episode_id)


def build_manifest(episodes: list[Episode], source: Path) -> dict[str, object]:
    """构造便于机器读取的校验清单。"""
    return {
        "result_type": "synthetic teaching data; not a VLA result",
        "source": str(source),
        "episode_count": len(episodes),
        "levels": sorted({episode.level for episode in episodes}),
        "episodes": [episode.to_record() for episode in episodes],
    }


def default_paths() -> tuple[Path, Path]:
    """返回默认输入与输出；路径不依赖 shell 当前目录。"""
    repo_root = Path(__file__).resolve().parents[3]
    input_path = repo_root / "foundation_library/f02_csv_json/data/mini_episodes.csv"
    output_path = repo_root / "learner_outputs/foundation_library/f03_modules_testing/validated_manifest.json"
    return input_path, output_path


def build_parser() -> argparse.ArgumentParser:
    """定义命令行接口，使输入输出可替换且有自动帮助。"""
    input_path, output_path = default_paths()
    parser = argparse.ArgumentParser(
        description="校验 fixture_ episode CSV 并生成 JSON 清单。"
    )
    parser.add_argument("--input", type=Path, default=input_path, help="输入 CSV 路径")
    parser.add_argument("--output", type=Path, default=output_path, help="输出 JSON 路径")
    return parser


def run(input_path: Path, output_path: Path) -> dict[str, object]:
    """组合读取、唯一性检查和写出，供命令行与测试共同调用。"""
    episodes = load_episodes(input_path)
    ensure_unique_ids(episodes)
    manifest = build_manifest(episodes, input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    """命令行主入口：成功返回 0，数据错误返回 2。"""
    args = build_parser().parse_args()
    try:
        manifest = run(args.input, args.output)
    except (OSError, SchemaError) as error:
        print(f"校验失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 3 ===")
    print("Result type: synthetic teaching data; not a VLA result")
    print(f"Validated episodes: {manifest['episode_count']}")
    print(f"Levels: {', '.join(manifest['levels'])}")
    print(f"Saved: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
