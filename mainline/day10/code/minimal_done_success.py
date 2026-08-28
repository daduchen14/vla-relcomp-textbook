#!/usr/bin/env python3
"""最小例子：episode 结束（done）不等于任务成功。"""

def evaluator_success(done: bool, info: dict) -> bool:
    """复现锁定 `is_success_done`: 优先读取 info.success。"""
    return bool(info.get("success", done))


CASES = [
    ("goal", True, {"success": True, "timeout": False}),
    ("timeout", True, {"success": False, "timeout": True}),
    ("running", False, {"success": False, "timeout": False}),
    ("legacy_no_success_key", True, {"timeout": False}),
]


if __name__ == "__main__":
    for name, done, info in CASES:
        success = evaluator_success(done, info)
        print(f"{name}: done={done} success={success} info={info}")
