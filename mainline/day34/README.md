# Mainline Day 34：运行可撤销的视觉对象提示 oracle

今天用仿真真值为 target/reference 添加诊断框，只改变送给 policy 的 agent-view RGB 副本；原 instruction、initial state 和其余推理条件保持不变。你会验收提示来源、episode 后清理，并对 success/四段事件计算 recovery 与 damage。当前实际运行的仍是 synthetic 配对分析，不生成伪造图片或模型结果。

## 1. 真实项目产物

- `visual_oracle_pairs_a.csv`：每对 transition、首个变化阶段、overlay 与清理证据；
- `visual_oracle_report_a.json`：success/四阶段效果、特权来源与允许变化；
- B 新输入的同类产物与 `challenge_memo.md`。

## 2. 当前卡点

若视觉提示同时改写 instruction，就无法和 Day 33 的语言 oracle 区分。若直接在环境原始 observation 上原地画框，提示还可能泄漏到下一 episode 或污染保存的视频/日志。仅报告 oracle 恢复则会隐藏原成功被框破坏的 damage。

本课规定 control 图像无 overlay；oracle 只在 agent-view RGB 的副本上加入 `TARGET_BOX` 和 `REFERENCE_BOX`。框来自 simulator ground truth，属于特权信息；每对结束必须验证清理，原始 observation 和下一 control 不得残留。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day34/code/minimal_reversible_overlay.py
```

应看到提示只在 oracle 期间存在，随后 `cleanup_verified=true`。若字典副本卡住补 [F01](../../foundation_library/f01_terminal_python/README.md)；若配对 effect 不清楚回看 [Day 33](../day33/README.md)。

## 4. 即时知识

- **visual oracle**：用仿真真值突出正确 target/reference 的诊断干预。
- **RGB overlay**：在 policy 图像副本上画提示；不是环境物理状态变化。
- **privileged information**：target/reference 真值默认不属于公开模型输入。
- **instruction fixed**：control/oracle 使用完全相同自然指令，隔离视觉处理。
- **reversible**：干预可移除，不改变环境、原始帧或后续 episode。
- **cleanup**：每对结束验证 overlay/caches 均被清除并记录结果。
- **recovery/damage**：分别以 control failures/successes 为分母，四段事件也同样计算。

## 5. 成熟材料处方

- **中文主材料（8 分钟）**：[Python `copy` 官方中文文档](https://docs.python.org/zh-cn/3/library/copy.html)。理解为什么对 observation 容器复制后再添加提示；像素数组还需独立复制，浅拷贝并不自动复制嵌套数组。
- **因果补充（英文官方，10 分钟）**：[PyWhy DoWhy：Estimating Causal Effects](https://www.pywhy.org/dowhy/v0.13/user_guide/causal_tasks/estimating_causal_effects/index.html)。区分 treatment（overlay）与 outcomes（四段事件）；不安装依赖。
- **锁定项目定位（10 分钟）**：[SmolVLA evaluator 第 239–299 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/models/smolvla/evaluator.py#L239-L299) 从 initial state 得到 obs，并把 `agentview_image` 转成 `observation.images.image`、把 task description 独立放入 observation；真实 oracle 只在图像转换前处理副本。

## 6. 最小实验

[minimal_reversible_overlay.py](code/minimal_reversible_overlay.py) 是完整 17 行代码：

```python
#!/usr/bin/env python3
"""最小例子：提示层只存在于 oracle observation 副本。"""

base_observation = {
    "pixels": "raw_agentview_rgb",
    "task": "pick tomato and place on bowl",
}
oracle_observation = base_observation.copy()
oracle_observation["overlay"] = "TARGET_BOX=tomato_1 | REFERENCE_BOX=bowl_1"

assert "overlay" not in base_observation
print(f"during_oracle={oracle_observation['overlay']}")
del oracle_observation["overlay"]
assert oracle_observation == base_observation
print("cleanup_verified=true")
print("source=simulator_ground_truth")
print("use=diagnostic_only")
```

## 7. 真实 VLA-Arena 操作

```bash
.venv-day06/bin/python mainline/day34/code/analyze_visual_oracle.py \
  --input shared/fixtures/day34_visual_oracle_results_a.csv \
  --output learner_outputs/mainline/day34/visual_oracle_pairs_a.csv \
  --report learner_outputs/mainline/day34/visual_oracle_report_a.json
```

应看到 5 对 synthetic 结果，success recovery `2/3`、damage `1/2`，且 cleanup 为真。这些数字只验证分析器。

真实 pilot 前预注册框颜色/线宽/遮挡规则；从仿真对象 ID 得到 target/reference 的投影框，复制 agentview array 后绘制，保存 raw frame 与 overlay frame 的对应 hash。control 跳过绘制；两臂加载同一 initial state、同一 instruction。episode 后销毁 overlay buffer 并用下一 control 的 raw hash 验证无残留。当前没有渲染图片、MuJoCo、模型/GPU 或视频结果。

## 8. 独立挑战

用 B input 生成新 summary/report。写 ≥240 字 memo，必须原样包含 `visual oracle`、`TARGET_BOX`、`REFERENCE_BOX`、`simulator ground truth`、`RGB overlay`、`instruction fixed`、`reversible`、`cleanup`、`recovery`、`damage`、`leakage`、`synthetic`、`causal`。解释输入唯一变化、清理证据、B 分母与至少两个替代解释。正文不给 B 数值。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day34.tests.test_day34_tools
.venv-day06/bin/python mainline/day34/code/check_day34.py \
  --example-input shared/fixtures/day34_visual_oracle_results_a.csv --example-output learner_outputs/mainline/day34/visual_oracle_pairs_a.csv --example-report learner_outputs/mainline/day34/visual_oracle_report_a.json \
  --challenge-input shared/fixtures/day34_visual_oracle_results_b.csv --challenge-output learner_outputs/mainline/day34/visual_oracle_pairs_b.csv --challenge-report learner_outputs/mainline/day34/visual_oracle_report_b.json \
  --challenge-memo learner_outputs/mainline/day34/challenge_memo.md
```

口述 10 分：提示/真值来源 2；instruction/初态固定 2；reversible/cleanup 2；recovery/damage 2；leakage/causal 边界 2。机器通过且 ≥8 进入 Day 35；改写 instruction、原地污染 raw obs、缺清理、只报恢复或把 synthetic 数字当模型结果均不通过。

## 10. 证据复盘

- 已运行：A/B synthetic visual-oracle 配对、overlay schema、清理字段与阶段效果严格重建。
- 静态源码事实：锁定 evaluator 从 agentview image 构造 policy 图像输入，并单独提供 task text。
- 未运行：真实投影框/渲染、MuJoCo、模型/GPU、视频与 buffer hash。
- 可以主张：分析契约隔离视觉提示，并同时核对特权来源、恢复、损伤和清理。
- 不能主张：真实 visual oracle 有效、视觉 grounding 是瓶颈，或提示可作为最终方法。

自测题（答案在 `shared/answer_keys/day34.md`）：

1. visual oracle 使用了什么 privileged information？
2. 为什么 instruction 必须 fixed？
3. reversible 与 cleanup 具体要求什么？
4. recovery 高且 damage 高时如何解释？
5. 视觉提示恢复能否唯一证明 grounding 的 causal 机制？
