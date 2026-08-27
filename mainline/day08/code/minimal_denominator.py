#!/usr/bin/env python3
"""最小例子：基础设施错误不进入模型成功率分母。"""

ROWS = [
    {"episode": "e1", "status": "completed", "evidence": True, "success": True},
    {"episode": "e2", "status": "completed", "evidence": True, "success": False},
    {"episode": "e3", "status": "infrastructure_error", "evidence": False, "success": None},
    {"episode": "e4", "status": "completed", "evidence": False, "success": True},
]


def summarize(rows: list[dict]) -> tuple[int, int, list[str]]:
    valid, excluded = [], []
    for row in rows:
        if row["status"] == "completed" and row["evidence"] and isinstance(row["success"], bool):
            valid.append(row)
        else:
            excluded.append(row["episode"])
    successes = sum(row["success"] for row in valid)
    return successes, len(valid), excluded


if __name__ == "__main__":
    successes, denominator, excluded = summarize(ROWS)
    print(f"success_rate={successes}/{denominator}={successes / denominator:.1%}")
    print(f"excluded={excluded}")
