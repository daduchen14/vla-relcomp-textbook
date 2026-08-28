# Mainline Day 27：完善目标接近与接触探针

今天把 Day 12 的粗粒度 `target_contacted` 拆成两个可审计信号：末端到目标的连续近距事件，以及 MuJoCo contact geoms 确认的目标接触。探针同时记录首次碰到的对象，避免“碰到了某物”被误写成“选中了目标”。

## 1. 真实项目产物

- `target_summary_a.csv`：每个 episode 的最小距离、首次连续近距、首次目标接触、首次接触对象与 probe status；
- `target_sensitivity_a.csv`：多个距离阈值下的 near 结果；
- `target_report_a.json`：状态计数与 `near ≠ contact` 边界；
- B 新 trace/config 的三项产物和 `challenge_memo.md`。

## 2. 当前卡点

单帧距离低于阈值可能只是掠过；物体中心距离不能代表表面真的接触；gripper 碰到干扰物也不能算目标接触。若只保留一个布尔值，目标定位、错误对象选择、接近后未接触会被混在一起。

本课固定 target object ID，near 要连续满足若干步；contact 必须来自 gripper collision geoms 与目标 contact geoms。首次接触非目标单列 `wrong_object_first`。阈值敏感性表用于发现结论是否依赖单一距离阈值，但不替代视频抽查。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day27/code/minimal_sustained_near.py
```

应看到 `first_near_step=3`，因为 step 1 的 0.07 后被 0.09 打断，只有 step 3–4 连续通过。若循环/`enumerate` 不熟，补 [F02](../../foundation_library/f02_csv_json/README.md)；对象状态回看 [Day 11](../day11/README.md)。

## 4. 即时知识

- **target distance**：末端代表点到目标代表点/表面的预注册距离；必须固定测量定义和单位 m。
- **threshold**：`distance <= τ` 才算该帧 near；τ 不是接触判定。
- **sustained event**：连续 `k` 帧通过才触发，减少单帧抖动假阳。
- **contact geom**：MuJoCo 用参与碰撞的 geom pair 记录接触；visual geom 不应自动算碰撞。
- **object selection error**：首次 gripper contact 不含 target，哪怕后来碰到目标也要保留。
- **sensitivity**：在预注册阈值网格上重算 near；若标签随微小阈值剧变，先检查度量/视频。
- **probe status**：可观察行为分流，不是视觉 grounding 的 causal 结论。

## 5. 成熟材料处方

- **中文主材料（6 分钟）**：[Python `enumerate()` 官方中文文档](https://docs.python.org/zh-cn/3/library/functions.html#enumerate)。只读计数与元素的配对；对应连续步扫描。
- **补充材料（12 分钟）**：[MuJoCo Computation：Contact 与 collision detection](https://mujoco.readthedocs.io/en/stable/computation/#contact)。重点读 contact 由 geom pair/距离/margin 定义，以及 `mjData.contact`；不要把任意欧氏距离等同 contact。
- **锁定项目定位（10 分钟）**：[VLA-Arena `_check_contact` 与 `check_gripper_contact` 第 1465–1554 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/bddl_base_domain.py#L1465-L1554)。确认它遍历 `sim.data.contact`、把 geom ID 还原为名称，并用 gripper collision geoms 对指定 object geoms 做双向匹配。

## 6. 最小实验

[minimal_sustained_near.py](code/minimal_sustained_near.py) 是完整 18 行代码：

```python
#!/usr/bin/env python3
"""最小例子：连续近距事件不同于单帧越阈值。"""

distances = [0.14, 0.07, 0.09, 0.06, 0.05]
threshold = 0.08
sustained_steps = 2

run = 0
first_near_step = None
for step, distance in enumerate(distances):
    run = run + 1 if distance <= threshold else 0
    if run == sustained_steps:
        first_near_step = step - sustained_steps + 1
        break

print(f"threshold_m={threshold}")
print(f"first_near_step={first_near_step}")
print("contact_detected=unknown_without_contact_geoms")
```

把 `sustained_steps` 改成 1，会得到 step 1；这说明持续窗口是操作定义的一部分，必须随结果保存。

## 7. 真实 VLA-Arena 操作

先运行免费合成 trace：

```bash
.venv-day06/bin/python mainline/day27/code/analyze_target_probe.py \
  --trace shared/fixtures/day27_target_trace_a.csv \
  --config shared/fixtures/day27_target_config_a.json \
  --summary learner_outputs/mainline/day27/target_summary_a.csv \
  --sensitivity learner_outputs/mainline/day27/target_sensitivity_a.csv \
  --report learner_outputs/mainline/day27/target_report_a.json
```

应看到 `episodes=3 sensitivity_rows=9 near_is_not_contact=true`。A 中包含目标接触、先碰错对象、单帧近距但不持续三类 synthetic 情形。

真实采集需在锁定 evaluator 的 episode loop 每步读取：Day 9 task table 的 target object、末端/目标的固定位置定义，以及 `env.check_gripper_contact(target_object)`；同时遍历候选对象记录首次实际 contact object。每行写 episode_id、连续 step、target ID、距离和 contact object IDs，再离线运行本脚本。不能为凑标签创建接触，也不能把 fixture object 名复制到真实任务。

优先排错：step 不连续先修 logger；target ID 变化先修 task join；距离单位异常先核对坐标系；near 无 contact 看视频与 geom 定义；wrong-object-first 保留原始对象名，不事后改成 target。当前环境没有启动 MuJoCo/GPU，因此这些真实命令与证据尚未执行。

## 8. 独立挑战

使用 B trace/config 生成新 summary/sensitivity/report，不给出结果。写 ≥220 字 memo，必须原样包含 `target_object_id`、`distance`、`threshold`、`sustained`、`contact geom`、`wrong object`、`sensitivity`、`near`、`contact`、`causal`、`synthetic`。

解释至少一个“先碰错对象后碰目标”和一个“距离越阈但不满足持续窗口”的 episode；不得复制 A 状态计数或答案段落。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day27.tests.test_day27_tools
.venv-day06/bin/python mainline/day27/code/check_day27.py \
  --example-trace shared/fixtures/day27_target_trace_a.csv --example-config shared/fixtures/day27_target_config_a.json \
  --example-summary learner_outputs/mainline/day27/target_summary_a.csv --example-sensitivity learner_outputs/mainline/day27/target_sensitivity_a.csv --example-report learner_outputs/mainline/day27/target_report_a.json \
  --challenge-trace shared/fixtures/day27_target_trace_b.csv --challenge-config shared/fixtures/day27_target_config_b.json \
  --challenge-summary learner_outputs/mainline/day27/target_summary_b.csv --challenge-sensitivity learner_outputs/mainline/day27/target_sensitivity_b.csv --challenge-report learner_outputs/mainline/day27/target_report_b.json \
  --challenge-memo learner_outputs/mainline/day27/challenge_memo.md
```

口述 10 分：target/distance 2；threshold/sustained 2；contact geom 2；wrong object/sensitivity 2；synthetic/causal 边界 2。机器通过且 ≥8 进入 Day 28；单帧即 near、距离冒充 contact、忽略错对象或伪造 MuJoCo 结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic trace、连续窗口、对象首次接触、阈值敏感性和非法 step 测试。
- 静态源码事实：锁定 VLA-Arena 的 gripper contact 由 `sim.data.contact` 与 collision geom 名匹配。
- 未运行：真实 MuJoCo trace、视频阈值抽查、模型/GPU。
- 可以主张：target detector 能把 near、target contact 与 wrong-object-first 分开。
- 不能主张：真实模型存在目标 grounding 问题或某阈值已被视频校准。

自测题（答案在 `shared/answer_keys/day27.md`）：

1. near 与 contact 为什么必须分开？
2. sustained window 解决什么问题？
3. 为何记录 first contact object？
4. sensitivity 表能证明阈值正确吗？
5. target contact 失败能否直接说明视觉 grounding 失败？
