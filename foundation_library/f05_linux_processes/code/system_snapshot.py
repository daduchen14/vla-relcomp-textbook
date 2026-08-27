"""Day 5 工程版本：安全记录文件系统、进程和公开环境信息。

本脚本不读取全部环境变量，避免把 token 或密钥写入证据文件。
输出是本机环境元数据，不是 VLA 实验结果。
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


# 只读取明确允许公开的变量；不要改为 dict(os.environ)。
SAFE_ENVIRONMENT_KEYS = ("LANG", "SHELL", "TERM", "VIRTUAL_ENV")


class SnapshotError(RuntimeError):
    """无法可靠生成快照时抛出的领域错误。"""


@dataclass(frozen=True)
class CommandObservation:
    """一次无副作用子进程的三类可观察结果。"""

    command: tuple[str, ...]
    stdout: str
    stderr: str
    returncode: int


@dataclass(frozen=True)
class SystemSnapshot:
    """用于复现实验入口的最小、非敏感系统快照。"""

    snapshot_id: str
    result_type: str
    operating_system: str
    platform_release: str
    machine: str
    python_version: str
    python_executable: str
    current_directory: str
    repository_root: str
    free_bytes: int
    safe_environment: dict[str, str | None]
    probe: CommandObservation


def run_command(arguments: list[str]) -> CommandObservation:
    """直接启动参数列表，并分别保留 stdout、stderr 和退出码。"""
    result = subprocess.run(
        arguments,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandObservation(
        command=tuple(arguments),
        stdout=result.stdout.rstrip("\r\n"),
        stderr=result.stderr.rstrip("\r\n"),
        returncode=result.returncode,
    )


def find_repository_root(start: Path) -> Path:
    """通过只读 Git 命令定位仓库根；失败时拒绝猜测。"""
    observation = run_command(
        ["git", "-C", str(start.resolve()), "rev-parse", "--show-toplevel"]
    )
    if observation.returncode != 0:
        detail = observation.stderr or "当前位置不在 Git 仓库中"
        raise SnapshotError(detail)
    return Path(observation.stdout).resolve()


def safe_environment() -> dict[str, str | None]:
    """只返回白名单环境变量，并把不存在明确保存为 null。"""
    return {key: os.environ.get(key) for key in SAFE_ENVIRONMENT_KEYS}


def make_probe(exit_code: int) -> CommandObservation:
    """创建不依赖 shell、结果可预测的 Python 子进程。"""
    code = (
        "import sys; "
        "print('fixture_probe_stdout'); "
        "print('fixture_probe_stderr', file=sys.stderr); "
        f"raise SystemExit({exit_code})"
    )
    return run_command([sys.executable, "-c", code])


def collect_snapshot(start: Path, probe_exit_code: int) -> SystemSnapshot:
    """收集快照；磁盘空间针对仓库所在文件系统。"""
    repository_root = find_repository_root(start)
    disk = shutil.disk_usage(repository_root)
    probe = make_probe(probe_exit_code)
    return SystemSnapshot(
        snapshot_id="fixture_day05_local_system",
        result_type="local system metadata; not a VLA experiment result",
        operating_system=platform.system(),
        platform_release=platform.release(),
        machine=platform.machine(),
        python_version=platform.python_version(),
        python_executable=sys.executable,
        current_directory=str(start.resolve()),
        repository_root=str(repository_root),
        free_bytes=disk.free,
        safe_environment=safe_environment(),
        probe=probe,
    )


def write_snapshot(snapshot: SystemSnapshot, output: Path) -> None:
    """把 dataclass 递归转换成 JSON 可序列化字典。"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(snapshot), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def default_output() -> Path:
    """默认写入被 Git 忽略的学习者输出目录。"""
    repository_root = Path(__file__).resolve().parents[3]
    return repository_root / "learner_outputs/foundation_library/f05_linux_processes/system_snapshot.json"


def build_parser() -> argparse.ArgumentParser:
    """定义输入目录、探针退出码和输出路径。"""
    parser = argparse.ArgumentParser(
        description="记录非敏感系统信息，并观察一个可控子进程。"
    )
    parser.add_argument("--start", type=Path, default=Path.cwd(), help="仓库内起始目录")
    parser.add_argument(
        "--probe-exit-code",
        type=int,
        choices=range(0, 4),
        default=0,
        metavar="{0,1,2,3}",
        help="教学子进程返回的退出码",
    )
    parser.add_argument("--output", type=Path, default=default_output(), help="JSON 输出")
    return parser


def main() -> int:
    """生成快照；快照失败返回 2，探针退出码只被记录而不冒充主程序失败。"""
    args = build_parser().parse_args()
    try:
        snapshot = collect_snapshot(args.start, args.probe_exit_code)
        write_snapshot(snapshot, args.output)
    except (OSError, SnapshotError) as error:
        print(f"快照失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 5 ===")
    print(f"OS: {snapshot.operating_system} {snapshot.machine}")
    print(f"Python: {snapshot.python_version}")
    print(f"Probe return code: {snapshot.probe.returncode}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: local system metadata; not a VLA experiment result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
