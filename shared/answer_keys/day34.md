# Day 34 参考答案（挑战后再看）

1. visual oracle 用 simulator ground truth 生成 TARGET_BOX 与 REFERENCE_BOX，再作为 RGB overlay 送入 policy；默认观察中没有这些框。
2. instruction fixed 是为了不把语言规范化效果混进视觉提示效果；初态、模型、seed/config 也必须固定。
3. reversible 要求 overlay 只作用于 oracle observation 副本，episode 后 cleanup，后续 control 不得残留提示或缓存。
4. recovery 高而 damage 也高表示提示改变行为但不稳定，不能只选恢复案例，更不能直接部署。
5. 不能。提示可能改变显著性、遮挡像素或 token/action 分布；即使 matched，也不是内部视觉 grounding 的唯一 causal 证明。

挑战 memo 示例：visual oracle 以 simulator ground truth 生成 TARGET_BOX、REFERENCE_BOX，仅改变 RGB overlay，保持 instruction fixed。干预必须 reversible 并记录 cleanup。对 synthetic 配对同时报告 recovery 与 damage；leakage 和像素遮挡等替代解释仍在，不能作 causal 内部机制结论。
