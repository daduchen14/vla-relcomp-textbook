# Day 14 / Gate 3 参考答案（独立作答后再看）

1. recovery 的分母只包括 control 失败；damage 的分母只包括 control 成功。把总 pair 数同时当两者分母会回答不同问题。
2. language oracle 使用 BDDL goal/init 的 target、起始关系、终止关系和 reference，因此包含 privileged information；它只能定位瓶颈，不能直接成为不使用真值的最终方法。
3. oracle 后成功不能单独证明模型内部“理解了关系”。替代解释包括结构化文本缩短了指令、改变 token 分布、减少歧义或偶然执行差异。
4. control/oracle 必须固定 task/goal、seed/init、模型 revision、推理配置和 evaluator；只改变 `instruction_text`。结果必须成对并同时报告 recovery/damage。
5. Gate case 的 contact/lift=true、approach/relation=false 支持“问题发生在搬运到 reference 或终态”这一行为描述，但不能区分语言 grounding 与控制。答案 JSON 给出 language oracle 作为一个可证伪干预；visual hint 也可，只要只改一个字段并明确泄漏。

口述示例：A fixture 的 recovery 是 2/3，damage 是 1/2；这只是合成配对数据的计算演示。真实 oracle 若 recovery 上升而 damage 也高，不能只报好消息。我的 alternative explanations 是 reference/关系语言约束不足，以及理解正确但搬运控制失败。oracle 使用 BDDL 真值，存在 leakage，只能用于诊断。即使干预恢复成功，也 cannot prove 模型内部形成了抽象关系表示；还需配对重复、事件变化和另一种干预区分解释。
