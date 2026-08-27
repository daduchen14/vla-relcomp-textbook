"""Day 4 最小版本：只读地取得当前 Git 分支和工作区状态。"""

import subprocess


def git(*arguments: str) -> str:
    """运行一条只读 Git 子命令，失败时保留错误并终止。"""
    result = subprocess.run(
        ["git", *arguments],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    print(f"branch={git('branch', '--show-current')}")
    print(f"commit={git('rev-parse', '--short', 'HEAD')}")
    status = git("status", "--short")
    print("working_tree=clean" if not status else "working_tree=changed")
