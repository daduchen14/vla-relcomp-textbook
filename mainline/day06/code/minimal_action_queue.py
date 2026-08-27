#!/usr/bin/env python3
"""用小数组演示 action chunk 何时推理、何时从队列取动作。"""

from collections import deque

import numpy as np


def rollout(num_steps: int = 7, chunk_size: int = 3) -> tuple[list[list[float]], int]:
    """每当队列为空就生成新 chunk；返回逐步动作和“推理”次数。"""
    queue: deque[np.ndarray] = deque()
    actions, model_calls = [], 0
    for step in range(num_steps):
        if not queue:
            # fixture 用确定数组代替模型；真实 SmolVLA chunk 形如 [batch, time, action_dim]。
            chunk = np.arange(chunk_size * 2, dtype=np.float32).reshape(chunk_size, 2)
            chunk += model_calls * 10
            queue.extend(chunk)
            model_calls += 1
        action = queue.popleft()
        actions.append(action.tolist())
        print(f"step={step} action={action.tolist()} remaining={len(queue)}")
    return actions, model_calls


if __name__ == "__main__":
    _, calls = rollout()
    print(f"model_calls={calls}")
