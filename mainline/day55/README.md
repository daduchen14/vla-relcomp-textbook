# Mainline Day 55：重跑关键 oracle，并与最终方法严格分栏

今天把 baseline/repair 放入 deployable results，把 language/visual oracle 放入 diagnostic-only results。每个 oracle 明示 privileged information，分别计算 repair failures 的 recovery、repair successes 的 damage 和 headroom；oracle 永不进入 primary result。本地仅分析 synthetic records。

## 1. 真实项目产物

- `final_oracle_report_a.json`：可部署/诊断两栏、特权来源、recovery/damage/headroom；
- 完整 condition×episode 检查与 oracle role 边界；
- B 新 records/config 的报告与 `challenge_memo.md`。

## 2. 当前卡点

oracle 往往比 repair 表现更好，但它知道 ground-truth relation 或 object boxes。若把它混进主平均、写成“我们的方法”，会把诊断上界冒充可部署能力。只报 recovery 还会隐藏 oracle 破坏 repair 成功的 damage。

本课要求每个 episode 同时有 baseline、repair、language oracle、visual oracle。deployable 与 diagnostic JSON 树完全分离，oracle 的 deployable/primary flags 固定为 false。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day55/code/minimal_oracle_partition.py
```

应看到 deployable 与 diagnostic_only 两个字典和 `oracle_in_primary_result=false`。若分母不熟回看 [Day 33](../day33/README.md)；视觉特权信息回看 [Day 34](../day34/README.md)。

## 4. 即时知识

- **oracle**：使用额外真值的诊断干预，不是常规输入下的方法。
- **diagnostic only**：只用于定位瓶颈/估计上界。
- **deployable method**：推理时只依赖允许观测与模型资产。
- **privileged information**：部署时不可得的 BDDL/模拟器真值。
- **recovery rate**：repair 失败中 oracle 转成功的比例。
- **damage rate**：repair 成功中 oracle 转失败的比例。
- **headroom**：oracle success rate−repair success rate。
- **separate column**：表格、JSON 与论文措辞均独立，不参与主方法聚合。

## 5. 成熟材料处方

- **中文主材料（Google ML，8 分钟）**：[生产机器学习系统：监控](https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring?hl=zh-cn)。只读“检查标签泄漏”，理解部署时不可用信息为何会造成虚高；oracle 是有意的诊断泄漏，必须显式标注。
- **补充材料（Distill，10 分钟）**：[Building Blocks of Interpretability](https://distill.pub/2018/building-blocks/)。只读把诊断工具与模型能力区分的思想；不要求复现视觉化。
- **锁定项目定位（10 分钟）**：[evaluator 第 247–255 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L247-L255) 改写 instruction；[第 264–299 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L264-L299) 构造图像/state/task observation。language oracle 只改 task，visual oracle 只改图像副本，且都需显式特权来源。

## 6. 最小实验

[minimal_oracle_partition.py](code/minimal_oracle_partition.py) 是完整 23 行代码：

```python
#!/usr/bin/env python3
"""最小例子：把可部署结果与特权 oracle 诊断分栏。"""

records = {
    "baseline": [0, 1, 0, 1],
    "repair": [1, 1, 0, 1],
    "language_oracle": [1, 1, 1, 1],
}

deployable = {
    name: sum(values) / len(values)
    for name, values in records.items()
    if name in {"baseline", "repair"}
}
diagnostic = {
    name: sum(values) / len(values)
    for name, values in records.items()
    if name.endswith("oracle")
}

print(f"deployable={deployable}")
print(f"diagnostic_only={diagnostic}")
print("oracle_in_primary_result=false")
```

长文件 [analyze_final_oracles.py](code/analyze_final_oracles.py) 先检查四条件完整性，再按 repair success/failure 分母计算 diagnostic 指标。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day55/code/analyze_final_oracles.py \
  --input shared/fixtures/day55_oracle_a.json --config mainline/day55/config/final_oracle_a.json \
  --report learner_outputs/mainline/day55/final_oracle_report_a.json
```

A 应得到 2 deployable、2 diagnostic，primary false。未来真实运行按 Day 51 oracle registry，用 Day 52/53 同 episode/initial state 运行 control 与两个 oracle；记录 privileged source、可逆清理、异常和逐 episode transition。输出仍放诊断表，不能并入 final repair score。当前不运行。

## 8. 独立挑战

用 B records/config 生成新 report。写 ≥270 字 memo，必须原样包含 `oracle`、`diagnostic only`、`deployable method`、`baseline`、`repair`、`language oracle`、`visual oracle`、`privileged information`、`recovery`、`damage`、`headroom`、`primary result`、`separate column`、`synthetic records`、`cannot claim`。正文不给 B 数值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day55.tests.test_day55_tools
.venv-day06/bin/python mainline/day55/code/check_day55.py \
  --example-input shared/fixtures/day55_oracle_a.json --example-config mainline/day55/config/final_oracle_a.json --example-report learner_outputs/mainline/day55/final_oracle_report_a.json \
  --challenge-input shared/fixtures/day55_oracle_b.json --challenge-config mainline/day55/config/final_oracle_b.json --challenge-report learner_outputs/mainline/day55/final_oracle_report_b.json \
  --challenge-memo learner_outputs/mainline/day55/challenge_memo.md
```

口述 10 分：oracle/特权 2；分栏 2；recovery 2；damage/headroom 2；synthetic 边界 2。机器通过且 ≥8 进入 Day 56；混入主结果、隐藏特权、错分母、只报 recovery 或冒充 final oracle data 均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic 四条件完整性、分栏与 oracle 指标。
- 静态源码事实：锁定 evaluator 的 instruction 与 observation 构造入口。
- 未运行：真实 checkpoints、oracle intervention、VLA-Arena/GPU。
- 可以主张：报告结构阻止 oracle 混入 deployable primary results。
- 不能主张：真实 oracle 恢复、机制被唯一定位或 oracle 可部署。

自测题（答案在 `shared/answer_keys/day55.md`）：

1. 为什么 oracle 必须与 deployable method 分栏？
2. recovery 与 damage 的分母分别是什么？
3. headroom 能说明什么、不能唯一说明什么？
4. oracle 能否进入 primary method 平均？
5. synthetic oracle 报告通过后可以主张什么？
