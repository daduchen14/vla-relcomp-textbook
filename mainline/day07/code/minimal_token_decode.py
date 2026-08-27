#!/usr/bin/env python3
"""最小 action token → 归一化连续动作 → 数据尺度动作。"""

import numpy as np


def decode(token_ids: np.ndarray, vocab_size: int, q01: np.ndarray, q99: np.ndarray) -> np.ndarray:
    """复现锁定 OpenVLA `predict_action` 的核心解码公式。"""
    bins = np.linspace(-1.0, 1.0, 256)
    centers = (bins[:-1] + bins[1:]) / 2.0
    discrete = vocab_size - token_ids
    indices = np.clip(discrete - 1, 0, len(centers) - 1)
    normalized = centers[indices]
    return 0.5 * (normalized + 1.0) * (q99 - q01) + q01


if __name__ == "__main__":
    # fixture 的 vocab/q01/q99 是教学数值，不是 checkpoint 统计。
    ids = np.array([999, 936, 872, 808, 744, 680, 999])
    low = np.array([-0.1] * 6 + [0.0])
    high = np.array([0.1] * 6 + [1.0])
    action = decode(ids, vocab_size=1000, q01=low, q99=high)
    action[-1] = -np.sign(2 * action[-1] - 1)  # evaluator 的 gripper normalize + invert。
    print("token_ids", ids.tolist())
    print("continuous_action", np.round(action, 4).tolist())
