# Mainline Day 28：完善抓取与持续抬升探针

今天把“抓取成功”拆成三条独立证据：左右 gripper 都接触目标、目标脱离原支撑面、目标相对 episode 初始 z 连续抬高。输出不仅给 lift 布尔值，还生成多阈值敏感性 CSV 与 SVG 图，暴露结论是否依赖单一高度阈值。

## 1. 真实项目产物

- `lift_summary_a.csv`：双指接触、首次持续抬升、支撑释放与 probe status；
- `lift_sensitivity_a.csv` 和 `lift_sensitivity_a.svg`：阈值扫描数据与可视化；
- `lift_report_a.json`；
- B 新 trace/config 的同类产物与 `challenge_memo.md`。

## 2. 当前卡点

夹爪碰到目标不代表抓稳；目标 z 短暂升高可能来自碰撞弹跳；z 升高但仍接触支撑面可能是斜面或坐标噪声；单指接触也可能伴随物体被推飞。若只看 z 或只看 contact，会把不同失败路径混在一起。

本课把物理 lift 定义为：相对 step 0 的高度增益达到阈值、支撑接触为 false，并连续维持 k 步。双指接触单独记录；`grasp_then_lift` 还要求双指事件不晚于 lift。两路信号冲突保留为 probe gap，不强行修成一致。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day28/code/minimal_sustained_lift.py
```

应看到 `first_lift_step=2`。最后一帧掉回支撑面不抹掉此前已经连续两步成立的事件。若 `zip`/布尔组合不熟补 [F02](../../foundation_library/f02_csv_json/README.md)；目标 contact 回看 [Day 27](../day27/README.md)。

## 4. 即时知识

- **baseline z**：episode step 0 的目标 body z；本课计算相对增益，不跨物体比较绝对高度。
- **bilateral contact**：左右指端/碰撞 geom 同步接触目标；是抓取证据，不是充分条件。
- **support surface**：目标仍与原支撑对象接触时，不能只凭 z 上升宣布 lift。
- **height gain**：`z_t-z_0`，单位 m；阈值与采样频率必须写入报告。
- **sustained lift**：height 与 support 两条件连续 k 步同时成立。
- **probe gap**：lift 成立但没有双指信号，可能是推/勾起、接触日志缺口或非典型抓取。
- **sensitivity plot**：阈值横轴、被判 lift 的 episode 数纵轴；不是性能曲线。

## 5. 成熟材料处方

- **中文主材料（6 分钟）**：[Python `zip()` 官方中文文档](https://docs.python.org/zh-cn/3/library/functions.html#zip)。只读并行迭代；对应 height/support 同步逐步检查。
- **补充材料（10 分钟）**：[MuJoCo Overview 的 body/geom/contact 区分](https://mujoco.readthedocs.io/en/stable/overview.html#geom)。确认 body 位姿和碰撞 geom 是不同层次。
- **锁定项目定位（10 分钟）**：[object state 第 199–225 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/object_states/base_object_states.py#L199-L225) 与 [gripper contact 第 1535–1554 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/envs/bddl_base_domain.py#L1535-L1554)。前者展示对象状态读取 sim body 数据并路由 gripper contact，后者把 gripper collision geoms 与目标 geoms 配对。

## 6. 最小实验

[minimal_sustained_lift.py](code/minimal_sustained_lift.py) 是完整 19 行代码：

```python
#!/usr/bin/env python3
"""最小例子：抬升要求高度与离开支撑面连续同时成立。"""

heights_m = [0.000, 0.010, 0.031, 0.042, 0.018]
support_contacts = [True, True, False, False, True]
threshold_m = 0.025
sustained_steps = 2

run = 0
first_lift_step = None
for step, (height, supported) in enumerate(zip(heights_m, support_contacts)):
    passed = height >= threshold_m and not supported
    run = run + 1 if passed else 0
    if run == sustained_steps:
        first_lift_step = step - sustained_steps + 1
        break

print(f"first_lift_step={first_lift_step}")
print("grasp_status=requires_separate_bilateral_contact_signal")
```

把 step 3 的 support 改成 true，持续窗口会失败；这说明 height 与支撑释放必须同时保持。

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day28/code/analyze_lift_probe.py \
  --trace shared/fixtures/day28_lift_trace_a.csv --config shared/fixtures/day28_lift_config_a.json \
  --summary learner_outputs/mainline/day28/lift_summary_a.csv \
  --sensitivity learner_outputs/mainline/day28/lift_sensitivity_a.csv \
  --plot learner_outputs/mainline/day28/lift_sensitivity_a.svg \
  --report learner_outputs/mainline/day28/lift_report_a.json
```

应看到 `episodes=4 sensitivity_rows=12 bilateral_is_not_lift=true`。SVG 可直接用浏览器打开；它来自 synthetic trace。

真实采集在每个 evaluator step 记录 target body z、左右指端对 target contact、target 对原支撑面的 contact。baseline 必须是同 episode 的稳定后 step 0；若 warm-up 仍在移动，应把“分析 step 0”定义为等待结束后的第一帧。真实左右指 geom 名需从锁定 robot/gripper 配置解析，不能用 fixture 的布尔位替代。

优先排错：z 跳变先核对 body ID/坐标；support 永不释放先检查支撑对象与 contact margin；双指永远 false 先检查 geom group；SVG 与 CSV 不同则验收会失败。未启动 MuJoCo/GPU，真实阈值仍需视频抽查。

## 8. 独立挑战

用 B trace/config 生成 summary、sensitivity、SVG、report。写 ≥220 字 memo，必须原样包含 `bilateral contact`、`support surface`、`baseline z`、`height gain`、`threshold`、`sustained`、`sensitivity`、`lift`、`probe gap`、`causal`、`synthetic`。

解释一个只维持两步却不满足 B 三步窗口的 episode，以及一个 lift 与 bilateral signal 冲突的 episode；不得复制 A 图或计数。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day28.tests.test_day28_tools
.venv-day06/bin/python mainline/day28/code/check_day28.py \
  --example-trace shared/fixtures/day28_lift_trace_a.csv --example-config shared/fixtures/day28_lift_config_a.json --example-summary learner_outputs/mainline/day28/lift_summary_a.csv --example-sensitivity learner_outputs/mainline/day28/lift_sensitivity_a.csv --example-plot learner_outputs/mainline/day28/lift_sensitivity_a.svg --example-report learner_outputs/mainline/day28/lift_report_a.json \
  --challenge-trace shared/fixtures/day28_lift_trace_b.csv --challenge-config shared/fixtures/day28_lift_config_b.json --challenge-summary learner_outputs/mainline/day28/lift_summary_b.csv --challenge-sensitivity learner_outputs/mainline/day28/lift_sensitivity_b.csv --challenge-plot learner_outputs/mainline/day28/lift_sensitivity_b.svg --challenge-report learner_outputs/mainline/day28/lift_report_b.json \
  --challenge-memo learner_outputs/mainline/day28/challenge_memo.md
```

口述 10 分：bilateral/support 2；baseline/gain 2；threshold/sustained 2；sensitivity/probe gap 2；synthetic/causal 边界 2。机器通过且 ≥8 进入 Day 29；单指当抓取、弹跳当 lift、忽略支撑或伪造图均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic z/contact trace、持续窗口、四类状态、阈值 CSV/SVG 精确重建。
- 静态源码事实：锁定 VLA-Arena 可由 object state 路由到真实 gripper contact，并从 sim body data 读取位姿。
- 未运行：真实 MuJoCo z/contact、视频校准、模型/GPU。
- 可以主张：lift detector 分离双指接触、支撑释放与持续高度增益。
- 不能主张：真实模型抓取瓶颈或任何阈值已适用于真实任务。

自测题（答案在 `shared/answer_keys/day28.md`）：

1. 为什么 bilateral contact 不等于 lift？
2. 为什么用相对 baseline z？
3. support contact 在定义中起什么作用？
4. probe gap 应如何处理？
5. sensitivity SVG 能否证明 causal 机制？
