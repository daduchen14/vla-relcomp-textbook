"""Day 6 工程版本：检查解释器、虚拟环境和声明的 Python 依赖。

只读取 fixture_ 依赖清单；不会安装、升级或删除任何包。
"""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class EnvironmentCheckError(RuntimeError):
    """清单无效或无法可靠检查环境时使用的异常。"""


@dataclass(frozen=True)
class DependencyObservation:
    """一项声明依赖在当前解释器中的实际状态。"""

    module: str
    distribution: str | None
    required: bool
    available: bool
    version: str | None
    reason: str


def load_manifest(path: Path) -> dict[str, Any]:
    """读取 fixture 清单，并检查最基本的真实性边界。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EnvironmentCheckError(f"无法读取依赖清单：{error}") from error
    manifest_id = data.get("manifest_id", "")
    if not isinstance(manifest_id, str) or not manifest_id.startswith("fixture_"):
        raise EnvironmentCheckError("manifest_id 必须以 fixture_ 开头")
    requirements = data.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise EnvironmentCheckError("requirements 必须是非空列表")
    return data


def distribution_version(distribution: str | None) -> str | None:
    """标准库没有 distribution；第三方包已安装时读取其元数据版本。"""
    if distribution is None:
        return None
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def inspect_requirement(item: dict[str, Any]) -> DependencyObservation:
    """把一条 JSON 声明转换成类型明确的观察记录。"""
    module = item.get("module")
    if not isinstance(module, str) or not module:
        raise EnvironmentCheckError("每项 requirement 必须有非空 module")
    distribution = item.get("distribution")
    if distribution is not None and not isinstance(distribution, str):
        raise EnvironmentCheckError(f"{module} 的 distribution 必须是字符串或 null")
    required = item.get("required")
    if not isinstance(required, bool):
        raise EnvironmentCheckError(f"{module} 的 required 必须是布尔值")
    reason = item.get("reason")
    if not isinstance(reason, str) or not reason:
        raise EnvironmentCheckError(f"{module} 必须说明 reason")

    available = importlib.util.find_spec(module) is not None
    return DependencyObservation(
        module=module,
        distribution=distribution,
        required=required,
        available=available,
        version=distribution_version(distribution) if available else None,
        reason=reason,
    )


def pip_identity() -> dict[str, object]:
    """用当前解释器调用 pip，避免误用 PATH 中另一个 pip。"""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "--version"],
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": [sys.executable, "-m", "pip", "--version"],
        "returncode": result.returncode,
        "stdout": result.stdout.rstrip("\r\n"),
        "stderr": result.stderr.rstrip("\r\n"),
    }


def build_report(manifest: dict[str, Any]) -> dict[str, object]:
    """检查所有依赖，并汇总当前解释器与虚拟环境边界。"""
    observations = [inspect_requirement(item) for item in manifest["requirements"]]
    missing_required = [item.module for item in observations if item.required and not item.available]
    return {
        "report_id": "fixture_day06_environment_report",
        "result_type": "local dependency metadata; not a VLA experiment result",
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "prefix": sys.prefix,
        "base_prefix": sys.base_prefix,
        "inside_virtual_environment": sys.prefix != sys.base_prefix,
        "pip": pip_identity(),
        "dependencies": [asdict(item) for item in observations],
        "missing_required": missing_required,
        "ready": not missing_required,
    }


def default_paths() -> tuple[Path, Path]:
    """根据脚本位置返回教材清单与个人输出路径。"""
    root = Path(__file__).resolve().parents[2]
    manifest = root / "day06/config/fixture_requirements.json"
    output = root / "learner_outputs/day06/environment_report.json"
    return manifest, output


def build_parser() -> argparse.ArgumentParser:
    """定义只读检查器的命令行接口。"""
    manifest, output = default_paths()
    parser = argparse.ArgumentParser(description="检查当前 Python 与 fixture 依赖清单。")
    parser.add_argument("--manifest", type=Path, default=manifest, help="依赖清单 JSON")
    parser.add_argument("--output", type=Path, default=output, help="检查报告 JSON")
    return parser


def main() -> int:
    """成功检查且无必需依赖缺失时返回 0，否则返回 2。"""
    args = build_parser().parse_args()
    try:
        report = build_report(load_manifest(args.manifest))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except EnvironmentCheckError as error:
        print(f"环境检查失败：{error}", file=sys.stderr)
        return 2

    print("=== VLA-RelComp Day 6 ===")
    print(f"Python: {report['python_executable']}")
    print(f"Virtual environment: {report['inside_virtual_environment']}")
    print(f"Missing required: {len(report['missing_required'])}")
    print(f"Saved: {args.output.resolve()}")
    print("Result type: local dependency metadata; not a VLA experiment result")
    return 0 if report["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
