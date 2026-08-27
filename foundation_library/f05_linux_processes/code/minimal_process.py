"""Day 5 最小版本：启动子进程并观察 stdout、stderr 与退出码。"""

import subprocess
import sys


def run_child(exit_code: int) -> subprocess.CompletedProcess[str]:
    """用当前 Python 启动一个可控的子进程。"""
    child_code = (
        "import sys; "
        "print('fixture_stdout'); "
        "print('fixture_stderr', file=sys.stderr); "
        f"raise SystemExit({exit_code})"
    )
    return subprocess.run(
        [sys.executable, "-c", child_code],
        text=True,
        capture_output=True,
        check=False,
    )


if __name__ == "__main__":
    result = run_child(exit_code=0)
    print(f"stdout={result.stdout.strip()}")
    print(f"stderr={result.stderr.strip()}")
    print(f"returncode={result.returncode}")
