# Mainline Day 48：按预注册方案首次评测 L1/L2 泛化

今天把 held-out OOD 分为 L1 与 L2，预先冻结每层主指标和最低改善阈值，再读取配对结果。报告同时给 baseline/repair rate、failure→success、success→failure 与 net discordant；主结论不合并层级，也不挑最好 level。本地结果来自 synthetic fixture，不是模型泛化证据。

## 1. 真实项目产物

- `ood_report_a.json`：analysis config hash、L1/L2 分层结果和阈值结论；
- 每层配对成功率差及两个方向的 discordant counts；
- B 新 fixture/预注册 config 的报告与 `challenge_memo.md`。

## 2. 当前卡点

首次打开 held-out test 后再决定指标或阈值，相当于用测试集调分析。把 L1/L2 池化也会掩盖“简单层提升、困难层退化”；只报最好层则更直接地产生选择偏差。

本课要求 config 明写 `registered_before_results=true`、固定 levels、主指标与每层 minimum delta。两个 level 都通过才有 `all_levels_pass=true`；聚合只可作补充，不能替代分层主结论。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day48/code/minimal_stratified_delta.py
```

应分别看到 L1/L2 delta 与两个方向计数。若配对 transition 不熟回看 [Day 47](../day47/README.md)；JSON 汇总困难补 [F02](../../foundation_library/f02_csv_json/README.md)。

## 4. 即时知识

- **held-out OOD**：训练、选择和阈值制定期间未读取的分布外测试。
- **preregistered analysis**：看结果前固定层级、指标、阈值和失败处理。
- **stratified**：按 L1/L2 分层计算，不先混成一个总数。
- **paired success-rate delta**：同一 episodes 上 repair rate−baseline rate。
- **failure-to-success / success-to-failure**：改善与退化的两个方向。
- **minimum delta**：每层独立的最低实际改善标准。
- **pooling**：合并层级；本课禁止用于 primary conclusion。
- **best-level selection**：只挑表现最好层，属于结果后选择。

## 5. 成熟材料处方

- **中文主材料（Center for Open Science，10 分钟）**：[预注册快速指南（中文 PDF）](https://www.cos.io/hubfs/Preregistration/Preregistration_Quick_Guide_Chinese.pdf)。只读“分析计划应在观察结果前固定”的部分。
- **补充材料（scikit-learn 官方，8 分钟）**：[模型评估：交叉验证](https://scikit-learn.org/stable/modules/cross_validation.html)。只看训练/验证/测试隔离概念；本项目 OOD test 不参与交叉验证。
- **锁定项目定位（10 分钟）**：[SmolVLA Args 第 79–100 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L79-L100) 定义 task level、trials 和 initial-state selection；[run_task 第 391–425 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L391-L425) 按 episode index 取初始状态并调用 rollout。真实 L1/L2 比较必须锁定这些字段。

## 6. 最小实验

[minimal_stratified_delta.py](code/minimal_stratified_delta.py) 是完整 18 行代码：

```python
#!/usr/bin/env python3
"""最小例子：按 L1/L2 分层报告配对成功率差。"""

rows = [
    ("L1", True, True), ("L1", False, True),
    ("L1", False, False), ("L1", True, True),
    ("L2", True, False), ("L2", False, True),
    ("L2", False, True), ("L2", True, True),
]

for level in ("L1", "L2"):
    group = [row for row in rows if row[0] == level]
    baseline = sum(row[1] for row in group) / len(group)
    repair = sum(row[2] for row in group) / len(group)
    improved = sum(not row[1] and row[2] for row in group)
    regressed = sum(row[1] and not row[2] for row in group)
    print(f"{level}: delta={repair-baseline:+.3f} "
          f"improved={improved} regressed={regressed}")
```

长文件 [analyze_ood_results.py](code/analyze_ood_results.py) 负责 config 身份、分层指标、阈值和禁止 pooling/best-level 的边界。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day48/code/analyze_ood_results.py \
  --input shared/fixtures/day48_ood_a.json \
  --analysis-config mainline/day48/config/ood_analysis_a.json \
  --report learner_outputs/mainline/day48/ood_report_a.json
```

A synthetic L1/L2 delta 均为 +0.4，并通过预设 +0.2。真实操作只能在 Day 45–47 的 checkpoints 与 L0 保持合格后开始：封存 analysis config hash，再以相同 evaluator/seed/episode/initial state 分别跑 baseline 与 repair 的 L1/L2；失败/异常 episode 也按预注册规则保留。当前未打开真实 OOD test。

## 8. 独立挑战

用 B fixture/config 生成新 report。写 ≥260 字 memo，必须原样包含 `held-out OOD`、`preregistered`、`L1`、`L2`、`paired success-rate delta`、`baseline rate`、`repair rate`、`failure-to-success`、`success-to-failure`、`minimum delta`、`stratified`、`pooling`、`best-level selection`、`synthetic fixture`、`cannot claim`。正文不给 B 数值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day48.tests.test_day48_tools
.venv-day06/bin/python mainline/day48/code/check_day48.py \
  --example-input shared/fixtures/day48_ood_a.json --example-config mainline/day48/config/ood_analysis_a.json --example-report learner_outputs/mainline/day48/ood_report_a.json \
  --challenge-input shared/fixtures/day48_ood_b.json --challenge-config mainline/day48/config/ood_analysis_b.json --challenge-report learner_outputs/mainline/day48/ood_report_b.json \
  --challenge-memo learner_outputs/mainline/day48/challenge_memo.md
```

口述 10 分：held-out/preregistration 2；分层 2；paired delta 2；discordant counts 2；synthetic 边界 2。机器通过且 ≥8 进入 Day 49；看结果后定阈值、只报最好层、用 pooling 代替分层、遗漏退化方向或冒充模型结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic L1/L2 分层、delta、discordant counts 和预设阈值。
- 静态源码事实：锁定 evaluator 的 level/trials/init-state 参数和 episode 调用。
- 未运行：checkpoints、VLA-Arena、真实 held-out L1/L2、MuJoCo/GPU。
- 可以主张：分析器要求两个注册层分别达标，且禁止 best-level selection。
- 不能主张：repair 真实 OOD 泛化改善、达到统计显著或可进入最终结论。

自测题（答案在 `shared/answer_keys/day48.md`）：

1. 为什么 L1/L2 必须 stratified？
2. paired success-rate delta 与两个 discordant counts 如何关联？
3. 首次看结果前必须 preregister 哪些内容？
4. pooling 和 best-level selection 会隐藏什么？
5. synthetic fixture 通过能否视为真实 held-out OOD 证据？
