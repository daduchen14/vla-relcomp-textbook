# Day 39 参考答案（挑战后再看）

1. balanced sampling 让每个 relation 的选中数相同，避免多数关系主导 loss；它不代表对象组合和难度也已完全平衡。
2. contrast pair 的 control/normalized 两臂共享 same action target、source episode 与对象，只改变 instruction 表达。
3. pair label 明确两臂属于同一监督目标；sample weight 当前固定 1.0，未来改权重必须另行冻结并报告。
4. sampling seed 使 outcome-free 选择可复算；不能用模型成功/失败挑“最有效”的训练样本。
5. incomplete pair 必须拒绝或单独报告，不能让一臂独自进入对比训练；全程仍是 L0-only。

挑战 memo 示例：balanced sampling 固定 relation coverage 与 sampling seed，且选择 outcome-free。每个 contrast pair 含 control、normalized，两臂有 same action target、pair label、sample weight。incomplete pair 不进入输出。当前是 synthetic L0-only manifest，不是 training 结果。
