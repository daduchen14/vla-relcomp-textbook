"""Day 4 工程版本：只读采集 Git 状态，输出可追溯 JSON 证据。

程序不会 add、commit、push、merge 或修改仓库。它记录的是 Git 元数据，不是 VLA 结果。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


class GitEvidenceError(RuntimeError):
    """Git 命令无法提供所需只读证据时使用的异常。"""


@dataclass(frozen=True)
class GitEvidence:
    """一次 Git 状态快照；只保存文本元数据，不保存文件内容。"""

    repository_root: str
    branch: str
    head_commit: str
    upstream: str | None
    ahead: int | None
    behind: int | None
    changed_paths: tuple[str, ...]
    result_type: str = "repository metadata; not a VLA experiment result"


def run_git(repo: Path, *arguments: str, allow_failure: bool = False) -> str | None:
    """以参数列表运行 Git，避免让 shell 解释用户输入。"""
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        # 只移除行尾；porcelain 状态开头的空格是 XY 格式的一部分，不能 strip 掉。
        return result.stdout.rstrip("\r\n")
    if allow_failure:
        return None
    detail = result.stderr.strip() or "unknown git error"
    raise GitEvidenceError(f"git {' '.join(arguments)} 失败：{detail}")


def find_repo_root(start: Path) -> Path:
    """让 Git 判断根目录，避免通过目录名字猜测。"""
    root_text = run_git(start.resolve(), "rev-parse", "--show-toplevel")
    if root_text is None:
        raise GitEvidenceError("Git 没有返回仓库根目录")
    return Path(root_text).resolve()


def parse_ahead_behind(text: str | None) -> tuple[int | None, int | None]:
    """把 `behind ahead` 两个计数转为整数；没有 upstream 时返回未知。"""
    if text is None:
        return None, None
    pieces = text.split()
    if len(pieces) != 2:
        raise GitEvidenceError(f"无法解析 ahead/behind：{text!r}")
    behind, ahead = (int(piece) for piece in pieces)
    return ahead, behind


def collect_evidence(start: Path) -> GitEvidence:
    """从仓库读取分支、提交、上游和变更路径。"""
    repo = find_repo_root(start)
    branch = run_git(repo, "branch", "--show-current") or "DETACHED_HEAD"
    commit = run_git(repo, "rev-parse", "HEAD")
    if commit is None:
        raise GitEvidenceError("Git 没有返回 HEAD commit")

    upstream = run_git(
        repo,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
        allow_failure=True,
    )
    counts = None
    if upstream is not None:
        counts = run_git(
            repo,
            "rev-list",
            "--left-right",
            "--count",
            f"{upstream}...HEAD",
        )
    ahead, behind = parse_ahead_behind(counts)

    status = run_git(repo, "status", "--porcelain=v1") or ""
    # porcelain 每行前 3 个字符是状态与空格，其余为相对路径。
    changed_paths = tuple(line[3:] for line in status.splitlines() if len(line) >= 4)
    return GitEvidence(
        repository_root=str(repo),
        branch=branch,
        head_commit=commit,
        upstream=upstream,
        ahead=ahead,
        behind=behind,
        changed_paths=changed_paths,
    )


def write_evidence(evidence: GitEvidence, output: Path) -> None:
    """把状态快照写成稳定、可读的 JSON。"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(evidence), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def default_output() -> Path:
    """根据教材脚本位置选择被 Git 忽略的个人输出目录。"""
    root = Path(__file__).resolve().parents[2]
    return root / "learner_outputs/day04/git_evidence.json"


def build_parser() -> argparse.ArgumentParser:
    """定义可查看的命令行契约。"""
    parser = argparse.ArgumentParser(description="只读记录当前 Git 仓库状态。")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="仓库内任意目录")
    parser.add_argument("--output", type=Path, default=default_output(), help="JSON 输出")
    return parser


def main() -> int:
    """采集并报告证据；预期错误使用退出码 2。"""
    args = build_parser().parse_args()
    try:
        evidence = collect_evidence(args.repo)
        write_evidence(evidence, args.output)
    except (OSError, ValueError, GitEvidenceError) as error:
        print(f"采集失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 4 ===")
    print(f"Branch: {evidence.branch}")
    print(f"Commit: {evidence.head_commit[:12]}")
    print(f"Changed paths: {len(evidence.changed_paths)}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: repository metadata; not a VLA experiment result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
