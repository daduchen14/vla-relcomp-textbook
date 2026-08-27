#!/usr/bin/env python3
"""最小进程探针：把 stdout、stderr、退出码分开保存。"""

import argparse
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
# 故意让子进程同时写 stdout/stderr；退出码 4 是数据，不是 Python 异常。
command = [
    "python3", "-c",
    "import sys; print('renderer=fixture'); print('gpu=not-used', file=sys.stderr); sys.exit(4)",
]
result = subprocess.run(command, text=True, capture_output=True)
report = {
    "command": command,
    "stdout": result.stdout.strip(),
    "stderr": result.stderr.strip(),
    "returncode": result.returncode,
    "source_kind": "local_process_fixture",
}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(f"returncode={result.returncode}")
print(f"Saved: {args.output}")
