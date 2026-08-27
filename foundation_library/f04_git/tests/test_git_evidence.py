"""Day 4 测试：在临时仓库验证 Git 状态读取，不改教材仓库。"""

import subprocess
import tempfile
import unittest
from pathlib import Path

from foundation_library.f04_git.code.git_evidence import collect_evidence


def git(repo: Path, *arguments: str) -> None:
    """测试辅助函数：在隔离临时目录执行确定的 Git 命令。"""
    subprocess.run(["git", "-C", str(repo), *arguments], check=True, capture_output=True)


class GitEvidenceTests(unittest.TestCase):
    def test_clean_repo_and_changed_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            git(repo, "init", "-q")
            git(repo, "config", "user.name", "Fixture Learner")
            git(repo, "config", "user.email", "fixture@example.invalid")
            note = repo / "fixture_note.txt"
            note.write_text("version 1\n", encoding="utf-8")
            git(repo, "add", "--", "fixture_note.txt")
            git(repo, "commit", "-q", "-m", "fixture: initial version")

            clean = collect_evidence(repo)
            self.assertEqual(clean.changed_paths, ())
            self.assertEqual(len(clean.head_commit), 40)

            note.write_text("version 2\n", encoding="utf-8")
            changed = collect_evidence(repo)
            self.assertEqual(changed.changed_paths, ("fixture_note.txt",))


if __name__ == "__main__":
    unittest.main()
