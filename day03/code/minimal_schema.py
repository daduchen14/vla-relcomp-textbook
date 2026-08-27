"""Day 3 最小版本：把一行 CSV 字典转换成类型正确的 episode。"""

import csv
from pathlib import Path


def parse_row(row: dict[str, str]) -> dict[str, object]:
    """检查最少字段，并把 seed、success、steps 转成正确类型。"""
    if not row["episode_id"].startswith("fixture_"):
        raise ValueError("episode_id 必须以 fixture_ 开头")
    if row["level"] not in {"0", "1", "2"}:
        raise ValueError("CSV 中的 level 只能是 0、1 或 2")
    if row["success"] not in {"0", "1"}:
        raise ValueError("success 只能是 0 或 1")
    return {
        "episode_id": row["episode_id"],
        "level": f"L{row['level']}",
        "seed": int(row["seed"]),
        "success": row["success"] == "1",
        "steps": int(row["steps"]),
    }


if __name__ == "__main__":
    # __file__ 指当前脚本；parents[2] 从 day03/code 回到仓库根目录。
    csv_path = Path(__file__).resolve().parents[2] / "day02/data/mini_episodes.csv"
    with csv_path.open(encoding="utf-8", newline="") as file:
        first_row = next(csv.DictReader(file))
    print(parse_row(first_row))
