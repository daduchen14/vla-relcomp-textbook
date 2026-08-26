"""VLA-RelComp Day 1：第一段可重复运行、会保存结果的 Python 程序。

本程序不加载模型，也不运行机器人仿真。它只演示科研程序最小的数据流：
命令行输入 -> Python 处理 -> 终端输出 -> 文件证据。
"""

# argparse 是 Python 标准库中的命令行参数解析器，不需要额外安装。
import argparse

# sys 让我们读取当前 Python 版本，并把错误输出到标准错误流。
import sys

# Path 用“路径对象”处理文件夹，比手工拼接斜杠更清楚。
from pathlib import Path


# 常量用大写命名，表示课程默认值；学习者仍可用命令行覆盖它。
DEFAULT_INSTRUCTION = "Move the red block to the left of the blue bowl."

# seed 是实验中控制随机性的编号；Day 1 只记录它，后续才真正使用随机数。
DEFAULT_SEED = 7


def build_parser() -> argparse.ArgumentParser:
    """创建并返回命令行解析器。"""

    # description 会显示在 `python3 first_run.py --help` 的开头。
    parser = argparse.ArgumentParser(
        description="Create the first VLA-RelComp teaching run record."
    )

    # --instruction 接收一段字符串，模拟未来 VLA 收到的自然语言指令。
    parser.add_argument(
        "--instruction",
        default=DEFAULT_INSTRUCTION,
        help="Natural-language robot instruction used in this teaching run.",
    )

    # type=int 要求 --seed 后面的文本能够转换为整数，否则 argparse 会报错。
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Integer identifier recorded for reproducibility.",
    )

    # 函数把已经配置好的解析器交还给调用者。
    return parser


def locate_paths() -> tuple[Path, Path]:
    """返回当前脚本的绝对路径，以及本课的个人输出目录。"""

    # __file__ 是当前源文件路径；resolve() 把它变成绝对路径。
    script_path = Path(__file__).resolve()

    # 源文件位于“教程/day01/code/”中，向上三级就是教程根目录。
    tutorial_root = script_path.parents[2]

    # / 运算符在 Path 中表示连接下一段路径，并不表示数学除法。
    output_dir = tutorial_root / "learner_outputs" / "day01"

    # 一次返回两个 Path；调用处会按相同顺序接收它们。
    return script_path, output_dir


def build_report(
    instruction: str,
    seed: int,
    python_version: str,
    script_path: Path,
) -> str:
    """把一次教学运行整理成可以保存的纯文本报告。"""

    # 列表保存多行文本；每个元素最终会成为文件中的一行。
    lines = [
        "course=VLA-RelComp 70-day textbook",
        "day=1",
        f"python_version={python_version}",
        f"instruction={instruction}",
        f"seed={seed}",
        "status=prepared",
        "result_type=synthetic teaching record; not a VLA experiment result",
        f"source_script={script_path}",
    ]

    # join 用换行符连接列表，并在文件末尾补一个换行，便于终端查看。
    return "\n".join(lines) + "\n"


def main() -> int:
    """组织完整流程，并用整数退出码告诉终端程序是否成功。"""

    # parse_args() 读取用户在终端中传入的 --instruction 和 --seed。
    args = build_parser().parse_args()

    # 元组拆包：locate_paths() 返回的两个值分别进入两个变量。
    script_path, output_dir = locate_paths()

    # sys.version 的第一段就是简洁的 Python 版本号，例如 3.12.13。
    python_version = sys.version.split()[0]

    # 把命令行输入和环境信息交给函数，生成即将保存的文本。
    report = build_report(
        instruction=args.instruction,
        seed=args.seed,
        python_version=python_version,
        script_path=script_path,
    )

    # 输出文件名固定，反复运行会更新同一份 Day 1 练习结果。
    output_path = output_dir / "first_run.txt"

    # 文件操作可能因权限或磁盘问题失败，所以用 try/except 给出清楚错误。
    try:
        # parents=True 会补齐缺失的上层目录；exist_ok=True 允许目录已存在。
        output_dir.mkdir(parents=True, exist_ok=True)

        # write_text 把字符串写入 UTF-8 文本；这也能正确保存中文。
        output_path.write_text(report, encoding="utf-8")
    except OSError as error:
        # file=sys.stderr 把错误和正常输出分开，便于脚本或日志工具识别。
        print(f"[ERROR] Could not write the teaching record: {error}", file=sys.stderr)

        # 非零退出码表示失败；终端可用 `echo $?` 查看它。
        return 1

    # 以下输出让学习者不打开文件也能确认程序接收了什么、做了什么。
    print("=== VLA-RelComp Day 1 ===")
    print(f"Python: {python_version}")
    print(f"Instruction: {args.instruction}")
    print(f"Seed: {args.seed}")
    print("Status: prepared (teaching record, not a VLA result)")
    print(f"Saved: {output_path}")

    # 0 是 Unix/Windows 命令行约定中的成功退出码。
    return 0


# 直接运行本文件时 __name__ 等于 "__main__"；被导入时则不会自动执行。
if __name__ == "__main__":
    # SystemExit 把 main() 的返回值交还给终端，形成真正的进程退出码。
    raise SystemExit(main())
