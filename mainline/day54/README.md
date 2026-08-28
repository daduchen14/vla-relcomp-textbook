# Mainline Day 54：重跑关键 counterfactual pairs 并锁住缺失处理

今天按 `pair_id × condition × arm` 重建关键反事实对：baseline/repair 各有 control 与 counterfactual，缺失或重复任一记录都 fail closed。完整后报告 paired success 与 outcome flip，比较 repair gain。本地只使用 synthetic records，不是 final pair data。

## 1. 真实项目产物

- `final_pair_report_a.json`：expected/observed 数、missing/duplicate、逐 pair 与条件汇总；
- 明确的 fail-closed missing policy；
- B 新 pairs/config 的报告与 `challenge_memo.md`。

## 2. 当前卡点

只统计成功返回的 episodes 会让超时、崩溃或缺文件从分母消失。只按 instruction 文本 join 也可能把重复描述错配；若 control/counterfactual initial state 不同，pair 差异无法归因于语言关系。

本课用冻结 pair_id、condition、arm 三元 key；expected set 与 observed set 必须完全相同、无重复。任何 missing 都直接使 run 无效，不做 complete-case 静默删除。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day54/code/minimal_pair_join.py
```

应看到 complete true、baseline false/repair true 和 fail_closed。若 join 不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；配对统计回看 [Day 47](../day47/README.md)。

## 4. 即时知识

- **counterfactual pair**：场景/初态固定，只改变目标关系表达的两条 arms。
- **control arm**：原始或中性指令。
- **counterfactual arm**：预注册的关系改写/反事实指令。
- **join key**：pair id + condition + arm 的唯一身份。
- **pair integrity**：所有 required cells 恰好出现一次。
- **fail closed**：缺失/重复时整体失败，不继续算主指标。
- **paired success**：同一 condition 下两 arms 都成功。
- **outcome flip**：两 arms 的 success 不一致，用于定位敏感性。

## 5. 成熟材料处方

- **中文主材料（pandas 中文指南，10 分钟）**：[合并、连接和拼接](https://pandas.pydata.org/docs/getting_started/intro_tutorials/08_combine_dataframes.html)。只理解 key-based merge 与 unmatched rows；本课代码不用 pandas。
- **补充材料（SQLBolt 中文，8 分钟）**：[SQL JOIN](https://sqlbolt.com/lesson/select_queries_with_joins)。只做 INNER/LEFT JOIN 区别，理解 inner join 会悄悄丢 missing arm。
- **锁定项目定位（10 分钟）**：[evaluator 第 247–255 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L247-L255) 应用 instruction replacement；[第 391–425 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L391-L425) 固定 episode/initial state 并调用 rollout。两 arms 必须复用同一选择参数。

## 6. 最小实验

[minimal_pair_join.py](code/minimal_pair_join.py) 是完整 23 行代码：

```python
#!/usr/bin/env python3
"""最小例子：按 pair/condition 检查两条 arm 都齐全。"""

rows = [
    ("p1", "baseline", "control", True),
    ("p1", "baseline", "counterfactual", False),
    ("p1", "repair", "control", True),
    ("p1", "repair", "counterfactual", True),
]
required_arms = {"control", "counterfactual"}

groups = {}
for pair_id, condition, arm, success in rows:
    groups.setdefault((pair_id, condition), {})[arm] = success

complete = all(set(arms) == required_arms for arms in groups.values())
scores = {
    condition: all(arms.values())
    for (_, condition), arms in groups.items()
}
print(f"complete={str(complete).lower()}")
print(f"paired_success={scores}")
print("missing_policy=fail_closed")
```

长文件 [analyze_final_pairs.py](code/analyze_final_pairs.py) 先建 expected key set，再计算四类 pair rows 与条件汇总。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day54/code/analyze_final_pairs.py \
  --input shared/fixtures/day54_pairs_a.json --config mainline/day54/config/final_pairs_a.json \
  --report learner_outputs/mainline/day54/final_pair_report_a.json
```

A synthetic 有 4 pairs、0 missing、repair paired gain +0.5。未来真实运行先由 Day 51 manifest 生成固定 pair registry，为 baseline/repair 两个 policy 对每个 pair arm 使用相同 initial-state index；无论 success、failure、timeout、exception 都写记录。待 expected/observed 完全一致后再分析。当前不运行。

## 8. 独立挑战

用 B records/config 生成新 report。写 ≥270 字 memo，必须原样包含 `counterfactual pair`、`control arm`、`counterfactual arm`、`baseline`、`repair`、`pair integrity`、`join key`、`missing record`、`duplicate`、`fail closed`、`paired success`、`outcome flip`、`same initial state`、`synthetic records`、`cannot claim`。正文不给 B gain。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day54.tests.test_day54_tools
.venv-day06/bin/python mainline/day54/code/check_day54.py \
  --example-input shared/fixtures/day54_pairs_a.json --example-config mainline/day54/config/final_pairs_a.json --example-report learner_outputs/mainline/day54/final_pair_report_a.json \
  --challenge-input shared/fixtures/day54_pairs_b.json --challenge-config mainline/day54/config/final_pairs_b.json --challenge-report learner_outputs/mainline/day54/final_pair_report_b.json \
  --challenge-memo learner_outputs/mainline/day54/challenge_memo.md
```

口述 10 分：pair/key 2；完整性 2；missing policy 2；paired metrics 2；synthetic 边界 2。机器通过且 ≥8 进入 Day 55；inner-join 丢失、重复 key、不同初态、只报平均或冒充 final data 均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic expected/observed keys、duplicate/missing 与 paired metrics。
- 静态源码事实：锁定 evaluator 的 replacement 与 initial-state episode 入口。
- 未运行：baseline/repair checkpoints、真实 pairs、VLA-Arena/GPU。
- 可以主张：分析器对缺失/重复 fail closed，且保留逐 pair 转换。
- 不能主张：repair 的真实 paired gain 为正或 final pair data 已产生。

自测题（答案在 `shared/answer_keys/day54.md`）：

1. 一个完整 pair 需要哪些 records？
2. 为什么 missing record 必须 fail closed？
3. paired success 与 outcome flip 分别定义什么？
4. 为什么两 arms 必须 same initial state？
5. synthetic gain 能否写成 final pair result？
