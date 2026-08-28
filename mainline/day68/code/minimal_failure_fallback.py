#!/usr/bin/env python3
"""最小例子：入口命令失败时给下一条可执行回退。"""

checks = [
    {"name": "route", "exit_code": 0, "fallback": "打开 Day 0"},
    {"name": "table", "exit_code": 2, "fallback": "核对 input/expected hash"},
]

for check in checks:
    if check["exit_code"] == 0:
        status = "PASS"
        next_action = "继续下一步"
    else:
        status = "FAIL"
        next_action = check["fallback"]
    print(f"{check['name']}: {status}; next={next_action}")
