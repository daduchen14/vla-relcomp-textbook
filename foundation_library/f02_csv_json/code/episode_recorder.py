"""VLA-RelComp Day 2：读取合成 episode CSV，并输出规范 CSV 与 JSON 摘要。

输入数据全部以 fixture_ 开头，只用于学习 Python 数据结构和实验记录。
本程序的输出不能被当作 VLA-Arena 或任何模型的真实实验结果。
"""

# argparse 负责 --input-csv 与 --output-dir 两个命令行参数。
import argparse

# csv 负责遵循 CSV 引号和分隔规则，避免手工 split(",") 的错误。
import csv

# json 负责把 Python 的列表、字典、数字和布尔值序列化为 JSON。
import json

# sys 用于把清晰的错误信息输出到标准错误流。
import sys

# Path 提供跨平台、可读的文件路径操作。
from pathlib import Path


# 这些字段构成 Day 2 教学数据的最小 schema（结构约定）。
FIELDNAMES = [
    "episode_id",
    "level",
    "task_id",
    "seed",
    "relation",
    "success",
    "steps",
]


def tutorial_root() -> Path:
    """根据当前源文件位置定位 70 天教程根目录。"""

    # 本文件位于“教程/foundation_library/f02_csv_json/code/”，所以向上三级得到教程根目录。
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    """创建命令行接口，并提供可直接运行的默认路径。"""

    # 先算出教材自带的输入数据和学习者输出目录。
    root = tutorial_root()
    default_input = root / "foundation_library" / "f02_csv_json" / "data" / "mini_episodes.csv"
    default_output = root / "learner_outputs" / "foundation_library" / "f02_csv_json"

    # description 会出现在 --help 中，告诉使用者程序的唯一职责。
    parser = argparse.ArgumentParser(
        description="Summarize synthetic VLA-RelComp teaching episodes."
    )

    # type=Path 让 argparse 直接把输入字符串转换成 Path 对象。
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=default_input,
        help="CSV file containing synthetic episode rows.",
    )

    # 输出目录可以由学习者覆盖，默认则写入已忽略的 learner_outputs。
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output,
        help="Directory for normalized CSV and JSON summary.",
    )

    # 返回解析器，而不是在函数内部立刻读取参数，便于后续测试和复用。
    return parser


def parse_integer(text: str, field: str, row_number: int) -> int:
    """把 CSV 文本转为非负整数；失败时指出具体行和字段。"""

    # CSV 文件读出来的每个单元格最初都是字符串，所以要显式转换。
    try:
        value = int(text)
    except ValueError as error:
        # raise ... from error 保留原始异常原因，同时给初学者更清楚的说明。
        raise ValueError(
            f"row {row_number}: field '{field}' must be an integer, got {text!r}"
        ) from error

    # level、seed、steps 在本课中都不允许是负数。
    if value < 0:
        raise ValueError(
            f"row {row_number}: field '{field}' must be non-negative, got {value}"
        )

    # 检查通过后返回真正的 int，而不是原来的字符串。
    return value


def parse_success(text: str, row_number: int) -> bool:
    """把 CSV 中的 0/1 严格转换为 Python 布尔值。"""

    # 这里只接受两个明确值，避免把任意非空字符串都误判为 True。
    if text == "1":
        return True
    if text == "0":
        return False

    # 错误数据必须停止，而不是被静默“修好”。
    raise ValueError(
        f"row {row_number}: field 'success' must be 0 or 1, got {text!r}"
    )


def load_episodes(input_path: Path) -> list[dict[str, object]]:
    """读取、检查并类型化全部 episode 记录。"""

    # 这个列表将依次保存每一行转换后的字典。
    episodes: list[dict[str, object]] = []

    # newline="" 是 csv 官方文档建议的打开方式；encoding 明确使用 UTF-8。
    with input_path.open("r", encoding="utf-8", newline="") as csv_file:
        # DictReader 用首行表头作为 key，因此每条记录自然成为一个字典。
        reader = csv.DictReader(csv_file)

        # fieldnames 可能是 None，因此先转成空集合再检查必需字段。
        actual_fields = set(reader.fieldnames or [])
        missing_fields = set(FIELDNAMES) - actual_fields

        # 少字段时立即给出明确列表，避免到后面才出现难懂的 KeyError。
        if missing_fields:
            missing_text = ", ".join(sorted(missing_fields))
            raise ValueError(f"CSV is missing required fields: {missing_text}")

        # enumerate 从 2 开始，因为 CSV 第 1 行是表头，第一条数据在第 2 行。
        for row_number, row in enumerate(reader, start=2):
            # episode_id 为空会破坏记录的唯一身份，所以必须拒绝。
            episode_id = row["episode_id"].strip()
            if not episode_id:
                raise ValueError(f"row {row_number}: episode_id must not be empty")

            # fixture_ 前缀把合成教学数据与未来真实实验数据清楚分开。
            if not episode_id.startswith("fixture_"):
                raise ValueError(
                    f"row {row_number}: teaching episode_id must start with 'fixture_'"
                )

            # 字典把同一 episode 的不同属性绑定在有名称的 key 上。
            episode = {
                "episode_id": episode_id,
                "level": parse_integer(row["level"], "level", row_number),
                "task_id": row["task_id"].strip(),
                "seed": parse_integer(row["seed"], "seed", row_number),
                "relation": row["relation"].strip(),
                "success": parse_success(row["success"], row_number),
                "steps": parse_integer(row["steps"], "steps", row_number),
            }

            # append 把当前字典加到列表末尾，保持 CSV 中的原始顺序。
            episodes.append(episode)

    # 空文件虽然语法可能合法，但无法计算成功率，所以明确拒绝。
    if not episodes:
        raise ValueError("CSV contains no episode rows")

    # 把完整列表交给汇总与写文件步骤。
    return episodes


def summarize(episodes: list[dict[str, object]]) -> dict[str, object]:
    """计算总体和分 level 成功率，返回可直接写成 JSON 的字典。"""

    # len 给出 episode 总数。
    total_episodes = len(episodes)

    # bool 是 int 的子类；True 可作为 1 相加，因此能直接统计成功条数。
    total_successes = sum(bool(item["success"]) for item in episodes)

    # steps 已在读取时转为 int；int(...) 让静态含义对初学者更直观。
    total_steps = sum(int(item["steps"]) for item in episodes)

    # levels 的 key 是 level 编号，value 是该组的计数器字典。
    levels: dict[int, dict[str, int]] = {}

    # 逐条扫描 episode，把它累加到自己的 level 分组。
    for episode in episodes:
        level = int(episode["level"])

        # setdefault 在 level 第一次出现时创建两个从 0 开始的计数器。
        bucket = levels.setdefault(level, {"episodes": 0, "successes": 0})

        # 当前组总 episode 数加一。
        bucket["episodes"] += 1

        # 成功时加一，失败时加零。
        bucket["successes"] += int(bool(episode["success"]))

    # JSON 对象的 key 最终是字符串；显式写成 L0/L1/L2 更便于阅读。
    level_summaries: dict[str, dict[str, object]] = {}

    # sorted 保证输出按 L0、L1、L2 的数字顺序排列。
    for level, counts in sorted(levels.items()):
        episode_count = counts["episodes"]
        success_count = counts["successes"]

        # 分母一定大于 0，因为 bucket 只会在真实 episode 出现时创建。
        success_rate = success_count / episode_count

        # 组装该 level 的三项指标。
        level_summaries[f"L{level}"] = {
            "episodes": episode_count,
            "successes": success_count,
            "success_rate": success_rate,
        }

    # 顶层字典既标明数据性质，也保存总体和分组汇总。
    return {
        "dataset_kind": "synthetic teaching fixture; not a VLA result",
        "total_episodes": total_episodes,
        "total_successes": total_successes,
        "overall_success_rate": total_successes / total_episodes,
        "total_steps": total_steps,
        "levels": level_summaries,
    }


def write_normalized_csv(
    episodes: list[dict[str, object]], output_path: Path
) -> None:
    """把类型检查后的记录重新写成列顺序固定的 CSV。"""

    # 以写入模式打开文件；newline="" 仍遵循 csv 模块的官方约定。
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        # extrasaction="raise" 能在代码意外多出字段时立即报错。
        writer = csv.DictWriter(
            csv_file,
            fieldnames=FIELDNAMES,
            extrasaction="raise",
        )

        # 先写列名，再写每条 episode。
        writer.writeheader()

        # CSV 中用 0/1 表示 success，避免写成大小写可能混乱的 True/False。
        for episode in episodes:
            row = dict(episode)
            row["success"] = int(bool(episode["success"]))
            writer.writerow(row)


def write_summary_json(summary: dict[str, object], output_path: Path) -> None:
    """把汇总字典保存成便于人和程序共同读取的 JSON。"""

    # 打开文本文件并明确 UTF-8，保证中文注释未来也可安全保存。
    with output_path.open("w", encoding="utf-8") as json_file:
        # ensure_ascii=False 保留非 ASCII 字符；indent=2 产生两空格缩进。
        json.dump(summary, json_file, ensure_ascii=False, indent=2)

        # JSON 标准不强制末尾换行，但文本工具通常更喜欢有换行的文件。
        json_file.write("\n")


def print_summary(summary: dict[str, object]) -> None:
    """把最重要的指标用人类可读格式打印到终端。"""

    # 读取顶层字典中的计数和比率。
    total = int(summary["total_episodes"])
    successes = int(summary["total_successes"])
    overall_rate = float(summary["overall_success_rate"])

    # :.1% 把 0.5 格式化为 50.0%。
    print(f"Loaded {total} synthetic teaching episodes.")
    print(f"Overall success: {successes}/{total} = {overall_rate:.1%}")

    # levels 的实际值是字典；这里按 L0/L1/L2 的插入顺序遍历。
    levels = summary["levels"]
    if not isinstance(levels, dict):
        raise TypeError("summary['levels'] must be a dictionary")

    # items() 同时取得组名和组内统计。
    for level_name, raw_counts in levels.items():
        if not isinstance(raw_counts, dict):
            raise TypeError(f"summary['levels'][{level_name!r}] must be a dictionary")

        episode_count = int(raw_counts["episodes"])
        success_count = int(raw_counts["successes"])
        success_rate = float(raw_counts["success_rate"])

        # 每个 level 单独一行，避免总体平均掩盖分布外层级差异。
        print(
            f"{level_name}: {success_count}/{episode_count} "
            f"= {success_rate:.1%}"
        )


def main() -> int:
    """串起参数解析、读取、汇总、保存和终端展示。"""

    # 解析命令行参数；默认值允许学习者第一遍不传任何参数。
    args = build_parser().parse_args()

    # expanduser 支持用户传入 ~/...；resolve 让错误和输出都显示绝对路径。
    input_path = args.input_csv.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()

    # 用一个 try/except 把常见的数据和文件错误转换成简洁的命令行信息。
    try:
        # 读取并类型化 CSV。
        episodes = load_episodes(input_path)

        # 用真正的 int/bool 计算汇总。
        summary = summarize(episodes)

        # 创建输出目录；重复执行时目录已经存在也不报错。
        output_dir.mkdir(parents=True, exist_ok=True)

        # 两种输出各有用途：CSV 保存逐条记录，JSON 保存嵌套汇总。
        normalized_path = output_dir / "normalized_episodes.csv"
        summary_path = output_dir / "summary.json"

        # 调用两个职责单一的函数完成写入。
        write_normalized_csv(episodes, normalized_path)
        write_summary_json(summary, summary_path)
    except (FileNotFoundError, OSError, ValueError, TypeError) as error:
        # [ERROR] 前缀和 stderr 使失败在长日志中更容易定位。
        print(f"[ERROR] {error}", file=sys.stderr)

        # 返回 1，告诉终端这次运行没有成功完成。
        return 1

    # 只有所有文件成功写完以后，才打印成功摘要和产物路径。
    print_summary(summary)
    print(f"Saved normalized CSV: {normalized_path}")
    print(f"Saved summary JSON: {summary_path}")

    # 0 表示完整流程成功。
    return 0


# 直接运行时进入 main；未来被测试代码 import 时不会偷偷执行。
if __name__ == "__main__":
    # 将 main 返回值交给操作系统作为退出码。
    raise SystemExit(main())
