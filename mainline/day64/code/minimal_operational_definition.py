#!/usr/bin/env python3
"""最小例子：把抽象问题改写为可执行的操作定义。"""

definitions = {
    "observation": "进入 policy.select_action 的图像、状态与任务字典",
    "action": "policy 输出并传给 env.step 的数值向量",
    "success": "episode done 且 is_success_done 为真，并满足 safety cost 条件",
}

required_terms = {
    "observation": ("policy.select_action", "字典"),
    "action": ("env.step", "向量"),
    "success": ("is_success_done", "cost"),
}

for name, definition in definitions.items():
    complete = all(term in definition for term in required_terms[name])
    print(f"{name}: operational={complete}")
