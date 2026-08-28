# Mainline Day 51：冻结最终矩阵与停止规则

今天把 condition、seed、L0/L1/L2、suite、trials、pair/oracle、指标阈值与停止规则汇成 canonical final manifest。任何语义变化都会产生新 SHA-256。由于 Gate 6 没有正式证据，本日只冻结计划，状态为 `FROZEN_PLAN_NOT_AUTHORIZED`，不启动 GPU。

## 1. 真实项目产物

- `final_manifest_a.json`：完整矩阵、预计 rollouts、阈值、停止规则和身份 hash；
- 失败/缺失 run 与负结果处理策略；
- B 新矩阵的 manifest 与 `challenge_memo.md`。

## 2. 当前卡点

进入最终实验后再加条件、换 seed 或延长预算，会把 confirmatory 实验变成结果导向探索。只列矩阵不列停止规则，也无法判断何时必须接受负结果。

本课要求 conditions 顺序固定为 baseline/repair/ablation，seeds 为 1–3，levels 为 L0–L2；停止规则必须覆盖预算、post-hoc 条件、failed runs、negative result 和 test-driven tuning。canonical hash 锁定整份语义。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day51/code/minimal_manifest_hash.py
```

应看到固定 SHA-256 和 `frozen_plan_not_authorized=true`。若 JSON/hash 不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；决策边界回看 [Day 50](../day50/README.md)。

## 4. 即时知识

- **final matrix**：最终要运行的全部条件笛卡尔积。
- **preregistration**：在结果前固定问题、设计、指标与规则。
- **stop rule**：规定预算耗尽、失败或不改善时何时停止。
- **negative result acceptance**：阈值不通过也按计划报告，不无限追加实验。
- **missing-run policy**：保留失败/缺失，不用新 seed 偷换。
- **canonical JSON**：排序 key、固定分隔符后的唯一序列化。
- **manifest hash**：canonical bytes 的 SHA-256，作为计划身份。
- **frozen ≠ authorized**：内容不可静默变更，不代表可以消耗资源。

## 5. 成熟材料处方

- **中文主材料（Open for Science，10 分钟）**：[早期职业研究人员开放科学指南（中文 PDF）](https://open4science.cn/static/ECR_OpenScience_Guide_CN.pdf)。重点核对研究问题、方法、分析和排除规则是否在结果前写清。
- **补充材料（Python 官方，6 分钟）**：[json：基本用法](https://docs.python.org/zh-cn/3/library/json.html#basic-usage)。只看 `sort_keys` 与 separators；hash 是身份工具，不是签名认证。
- **锁定项目定位（8 分钟）**：[SmolVLA Args 第 79–139 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L79-L139) 显示真实 level/trials/init-state/seed/replacement 字段；[默认 train config 第 1–18 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/configs/train/smolvla.yaml#L1-L18) 给出训练数据、模型、步数和 checkpoint 字段。final manifest 必须映射而非修改这些锁定文件。

## 6. 最小实验

[minimal_manifest_hash.py](code/minimal_manifest_hash.py) 是完整 22 行代码：

```python
#!/usr/bin/env python3
"""最小例子：canonical JSON 让任何计划变动产生新 hash。"""

import hashlib
import json

manifest = {
    "conditions": ["baseline", "repair", "ablation"],
    "levels": ["L0", "L1", "L2"],
    "seeds": [1, 2, 3],
    "max_gpu_hours": 36,
    "authorized": False,
}

canonical = json.dumps(
    manifest,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
print(f"manifest_sha256={hashlib.sha256(canonical).hexdigest()}")
print("frozen_plan_not_authorized=true")
```

长文件 [freeze_final_manifest.py](code/freeze_final_manifest.py) 依次验证矩阵轴、stop rules、rollout 数与 canonical hash。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day51/code/freeze_final_manifest.py \
  --config mainline/day51/config/final_matrix_a.json \
  --manifest learner_outputs/mainline/day51/final_manifest_a.json
```

A 应展开为 270 个计划 episode rollouts 并输出 frozen/not-authorized。未来若 Gate 6 获正式通过和资源授权，先把 manifest 的 suite/threshold/path 映射成具体 evaluator/train config，逐 cell 生成 run id；执行前记录 manifest hash。任何必要改动都新建 manifest version、说明原因并重新批准，不能覆盖旧 hash。

## 8. 独立挑战

用 B config 生成新 manifest。写 ≥270 字 memo，必须原样包含 `final manifest`、`preregistration`、`matrix`、`baseline`、`repair`、`ablation`、`seed`、`L0/L1/L2`、`stop rule`、`budget exhaustion`、`failed run`、`negative result`、`canonical hash`、`frozen`、`not authorized`。正文不给 B rollout 数/hash。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day51.tests.test_day51_tools
.venv-day06/bin/python mainline/day51/code/check_day51.py \
  --example-config mainline/day51/config/final_matrix_a.json --example-manifest learner_outputs/mainline/day51/final_manifest_a.json \
  --challenge-config mainline/day51/config/final_matrix_b.json --challenge-manifest learner_outputs/mainline/day51/final_manifest_b.json \
  --challenge-memo learner_outputs/mainline/day51/challenge_memo.md
```

口述 10 分：matrix 2；preregistration 2；stop rules 2；hash/version 2；authorization boundary 2。机器通过且 ≥8 进入 Day 52；遗漏轴、事后追加、替换 failed seed、无预算停止或把 frozen 当 authorized 均不通过。

## 10. 证据复盘

- 已运行：A/B final matrix、rollout 数、stop rules 与 canonical hash。
- 静态源码事实：锁定 evaluator/train config 的真实映射字段。
- 未运行：任何 final experiment、GPU、checkpoint、episode 或结果。
- 可以主张：最终实验计划与停止规则已有不可静默变化的身份。
- 不能主张：矩阵获授权、实验已开始或预计 rollouts 已完成。

自测题（答案在 `shared/answer_keys/day51.md`）：

1. final matrix 的 rollout 数由哪些轴相乘？
2. 为什么 stop rules 必须在结果前冻结？
3. failed run 应如何处理？
4. canonical manifest hash 能防止什么？
5. frozen 是否等于 authorized，为什么？
