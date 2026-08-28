# Mainline Day 29：检测搬运是否接近正确参照区域

今天只分析 Day 28 lift 之后的轨迹，回答三个不同问题：目标是否持续进入正确参照物的邻域、是否只是朝它取得进展、是否反而被错误参照物吸引。这样不会把“搬运方向对但没到位”与“选错参照物”混为一谈。

## 1. 真实项目产物

- `approach_summary_a.csv`：正确参照距离、净进展、下降比例、进入 step、错误参照物与状态；
- `approach_report_a.json`；
- B 新轨迹的同类产物与 `challenge_memo.md`。

## 2. 当前卡点

只看终点距离会丢掉轨迹方向；只看距离下降又可能始终没进入可操作区域。更糟的是目标可能持续靠近场景中的另一个容器。没有 lift 时，所谓“搬运接近”也没有定义。

本课以 task table 的 `reference_object_id` 为唯一正确参照，只保留 lifted segment。正确参照需连续 k 步进入阈值；否则再看 minimum net progress；错误参照物需连续进入自己的阈值。`decrease_fraction` 描述局部趋势，但不单独决定成功。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day29/code/minimal_progress.py
```

应看到 `net_progress_m=0.220`、`entered=False`、`status=PROGRESS_NO_ENTRY`。若 `zip`/差分不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；lifted segment 回看 [Day 28](../day28/README.md)。

## 4. 即时知识

- **lifted segment**：只从 lift=true 的帧分析搬运，保留原始 step。
- **distance trajectory**：目标与预注册参照物的逐步距离序列，单位 m。
- **net progress**：第一帧距离减最小距离；说明曾经靠近多少，不保证保持。
- **decrease fraction**：相邻步中下降超过 epsilon 的比例；短轨迹只作描述。
- **entry threshold**：距离连续 k 步不大于阈值才是 approach event。
- **wrong reference**：最近其他对象持续进入错误阈值；不能用它替换正确参照 ID。
- **observable ≠ causal**：错误吸引是轨迹模式，不自动证明 relation grounding 失败。

## 5. 成熟材料处方

- **中文主材料（6 分钟）**：[Python `zip()` 官方中文文档](https://docs.python.org/zh-cn/3/library/functions.html#zip)。理解相邻距离配对与差分。
- **补充材料（10 分钟）**：[NIST Run-Sequence Plot](https://www.itl.nist.gov/div898/handbook/eda/section3/eda33p.htm)。只读按时间索引画 response 以观察 shift/trend；本课的 decrease fraction 不是显著性检验。
- **锁定项目定位（10 分钟）**：[object state 第 99–130 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/object_states/base_object_states.py#L99-L130)。确认关系状态从 `obj_body_id` 对应的 `sim.data.body_xpos` 读取两个对象位置；真实 detector 必须使用 task 指定对象，而非最近物体猜测。

## 6. 最小实验

[minimal_progress.py](code/minimal_progress.py) 是完整 18 行代码：

```python
#!/usr/bin/env python3
"""最小例子：进入区域与朝区域取得进展是两个事件。"""

distances_m = [0.42, 0.33, 0.25, 0.20]
entry_threshold_m = 0.12
minimum_progress_m = 0.08

decreases = [before - after for before, after in zip(distances_m, distances_m[1:])]
net_progress = distances_m[0] - min(distances_m)
decrease_fraction = sum(delta > 0 for delta in decreases) / len(decreases)
entered = min(distances_m) <= entry_threshold_m
progressed = net_progress >= minimum_progress_m

print(f"net_progress_m={net_progress:.3f}")
print(f"decrease_fraction={decrease_fraction:.3f}")
print(f"entered={entered}")
print(f"progressed={progressed}")
print("status=PROGRESS_NO_ENTRY" if progressed and not entered else "status=OTHER")
```

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day29/code/analyze_approach_probe.py \
  --trace shared/fixtures/day29_approach_trace_a.csv --config shared/fixtures/day29_approach_config_a.json \
  --output learner_outputs/mainline/day29/approach_summary_a.csv \
  --report learner_outputs/mainline/day29/approach_report_a.json
```

应看到 4 个 episode，覆盖正确进入、错误参照吸引、只有进展和无 lifted segment。它们都是 synthetic。

真实采集把 Day 9 的 reference object ID 与 Day 28 lifted bit join 到每步状态；读取 target/reference body position 计算同一距离定义，并对其他候选 reference 记录最近 ID/距离。不要让“最近对象”覆盖 task ground truth。优先检查 ID、单位、step、lift join 与动态参照物；真实 MuJoCo/GPU 未运行。

## 8. 独立挑战

用 B trace/config 生成新 summary/report。写 ≥220 字 memo，必须原样包含 `lifted segment`、`reference_object_id`、`distance trajectory`、`net progress`、`entry threshold`、`sustained`、`wrong reference`、`decrease fraction`、`approach`、`causal`、`synthetic`。正文不给 B 状态计数。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day29.tests.test_day29_tools
.venv-day06/bin/python mainline/day29/code/check_day29.py \
  --example-trace shared/fixtures/day29_approach_trace_a.csv --example-config shared/fixtures/day29_approach_config_a.json --example-output learner_outputs/mainline/day29/approach_summary_a.csv --example-report learner_outputs/mainline/day29/approach_report_a.json \
  --challenge-trace shared/fixtures/day29_approach_trace_b.csv --challenge-config shared/fixtures/day29_approach_config_b.json --challenge-output learner_outputs/mainline/day29/approach_summary_b.csv --challenge-report learner_outputs/mainline/day29/approach_report_b.json \
  --challenge-memo learner_outputs/mainline/day29/challenge_memo.md
```

口述 10 分：lifted/reference 2；trajectory/progress 2；threshold/sustained 2；wrong reference/trend 2；synthetic/causal 2。机器通过且 ≥8 进入 Day 30；终点冒充轨迹、最近物体冒充正确参照或伪造结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic trajectory 与四种状态、连续 step 和严格重建。
- 静态源码事实：锁定 object states 通过 body ID 读取对象位置。
- 未运行：真实 MuJoCo trajectory、视频、模型/GPU。
- 可以主张：approach detector 区分正确进入、进展不足与错误参照吸引。
- 不能主张：真实 relation grounding 或控制机制。

自测题（答案在 `shared/answer_keys/day29.md`）：

1. net progress 与 entry 有何不同？
2. 为什么只分析 lifted segment？
3. nearest other 能否替换 reference ID？
4. decrease fraction 能否单独判 approach？
5. wrong-reference attraction 能否直接证明语言错误？
