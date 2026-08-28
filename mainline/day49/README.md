# Mainline Day 49：最小消融与成本匹配对照

今天用 baseline、完整 repair、`ablation_no_normalization` 三条件隔离关系规范化的增量作用。repair 与 ablation 必须只差一个字段，并对每个 seed 使用相同 split、steps 和近似 GPU-hours；所有 seed 都进入均值/样本标准差。当前输入是 synthetic ledger，不是正式训练结果。

## 1. 真实项目产物

- `ablation_report_a.json`：条件签名差异、逐 seed gain/effect/cost gap 与汇总；
- 单变量和成本匹配机器结论；
- B 新 ledger/config 的报告与 `challenge_memo.md`。

## 2. 当前卡点

完整 repair 优于 baseline，只说明整个方案相关，不能说明关系规范化是原因。如果 ablation 同时换 loss、数据或训练预算，差值仍不可归因；成本明显较低也会形成不公平对照。

本课把 primary effect 定义为 `repair−ablation`，签名只允许 `relation_normalization` 改变。baseline 用于报告总 repair gain；三个条件都保留全部 seed，禁止挑选结果。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day49/code/minimal_ablation.py
```

应看到唯一 changed factor、effect +0.110、cost gap 0.020。若方差不熟回看 [Day 46](../day46/README.md)；JSON 表格补 [F02](../../foundation_library/f02_csv_json/README.md)。

## 4. 即时知识

- **minimal ablation**：只移除一个目标组件，其余条件保持不变。
- **single variable**：repair/ablation 签名恰有一个变化字段。
- **baseline gain**：repair−baseline，表示完整方案总差异。
- **component effect**：repair−ablation，表示目标组件的增量差异。
- **cost matched**：steps、split、seed 一致，实际成本差在预设容差内。
- **relative cost gap**：`|repair cost−ablation cost| / repair cost`。
- **paired seeds**：同一 seed 下先比较条件，再汇总全部 seed。
- **causal caution**：即便设计干净，小样本和执行偏差仍限制因果主张。

## 5. 成熟材料处方

- **中文主材料（Google ML，10 分钟）**：[机器学习规则：启动和迭代](https://developers.google.com/machine-learning/guides/rules-of-ml?hl=zh-cn)。只读一次只验证清晰改动、先建立可靠基线的原则。
- **补充材料（Google PAIR，8 分钟）**：[What-If Tool：比较模型](https://pair-code.github.io/what-if-tool/learn/)。只理解一致输入上的对照思想；本课不用该工具。
- **锁定项目定位（8 分钟）**：[SmolVLA 默认 train config 第 5–18 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/configs/train/smolvla.yaml#L5-L18) 给出 policy、lr、batch、steps、output 与 save；正式 repair/ablation 必须从同一冻结配置派生，仅关闭目标组件。[trainer 第 237–265 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/src/lerobot/scripts/train.py#L237-L265) 是相同步数与 logging/save 判断的真实循环。

## 6. 最小实验

[minimal_ablation.py](code/minimal_ablation.py) 是完整 19 行代码：

```python
#!/usr/bin/env python3
"""最小例子：成本匹配时用 repair−ablation 隔离单一组件。"""

repair = {"score": 0.62, "gpu_hours": 5.0,
          "normalization": True, "adapter": True}
ablation = {"score": 0.51, "gpu_hours": 4.9,
            "normalization": False, "adapter": True}

changed = [
    key for key in ("normalization", "adapter")
    if repair[key] != ablation[key]
]
cost_gap = abs(repair["gpu_hours"] - ablation["gpu_hours"])
cost_gap /= repair["gpu_hours"]

print(f"changed_factors={changed}")
print(f"component_effect={repair['score']-ablation['score']:+.3f}")
print(f"relative_cost_gap={cost_gap:.3f}")
print(f"single_variable={str(changed == ['normalization']).lower()}")
```

长文件 [analyze_cost_matched_ablation.py](code/analyze_cost_matched_ablation.py) 逐层检查 conditions、seed 完整性、签名差异、split/steps 与成本。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day49/code/analyze_cost_matched_ablation.py \
  --input shared/fixtures/day49_ablation_a.json --config mainline/day49/config/ablation_config_a.json \
  --report learner_outputs/mainline/day49/ablation_report_a.json
```

A synthetic mean component effect 约 +0.103，所有 cost gap 约 2%。真实消融须等正式 checkpoints/results 存在后，从同一 recipe 复制配置，仅关闭 normalization；按相同 seeds/split/steps 训练，记录实际 GPU-hours 和失败，随后用真实 held-out 指标替换 score。不能为追求匹配而事后删 seed。

## 8. 独立挑战

用 B ledger/config 生成新 report。写 ≥260 字 memo，必须原样包含 `minimal ablation`、`single variable`、`relation normalization`、`repair`、`ablation`、`baseline`、`same split`、`same steps`、`cost matched`、`GPU-hours`、`relative cost gap`、`component effect`、`all seeds`、`cherry-picking`、`synthetic ledger`。正文不给 B effect。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day49.tests.test_day49_tools
.venv-day06/bin/python mainline/day49/code/check_day49.py \
  --example-input shared/fixtures/day49_ablation_a.json --example-config mainline/day49/config/ablation_config_a.json --example-report learner_outputs/mainline/day49/ablation_report_a.json \
  --challenge-input shared/fixtures/day49_ablation_b.json --challenge-config mainline/day49/config/ablation_config_b.json --challenge-report learner_outputs/mainline/day49/ablation_report_b.json \
  --challenge-memo learner_outputs/mainline/day49/challenge_memo.md
```

口述 10 分：三条件 2；单变量 2；成本公平 2；多 seed 2；synthetic 边界 2。机器通过且 ≥8 进入 Day 50；多变量、split/steps 不同、cost gap 超限、挑 seed 或冒充正式因果证据均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic ledger 的签名、配对 seed、成本与 effect 汇总。
- 静态源码事实：锁定训练配置和 trainer loop 的 steps/save 入口。
- 未运行：baseline/repair/ablation checkpoints、GPU、VLA-Arena 与真实 cost。
- 可以主张：分析器只接受单变量且成本匹配的全部 seed 对照。
- 不能主张：relation normalization 对真实模型有 +0.103 因果效果。

自测题（答案在 `shared/answer_keys/day49.md`）：

1. minimal ablation 的 primary comparison 是什么？
2. baseline 在三条件设计中提供什么？
3. cost matched 至少要求哪些量一致或接近？
4. repair 与 ablation 同时改变两个字段会怎样？
5. synthetic ledger 结果能否支持正式因果结论？
