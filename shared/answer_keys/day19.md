# Day 19 参考答案（挑战后再看）

1. L1 是 held-out 泛化评估；它可以被报告，不能用于选择 checkpoint、threshold、prompt 或超参数。
2. Day 19 guard 要求 L1 与 L0 的 model/revision、protocol lock、seed base、init_state_indices 完全相同，只有 level 与 batch/source 身份变化。
3. 即使只是“看一眼”L1 再改 prompt，也形成 leakage；改后的方法需要新的未见测试集，原 L1 不再是最终 held-out。
4. `report_only` 不等于结果不可分析；可以计算预登记统计和失败分类，但不能让分析结果反馈到当前方法选择。
5. 当前 L1 registry 全是 PLANNED/synthetic，不能声称 OOD 下降、任务失败或模型泛化能力。

挑战 memo 示例：B 的 L1 held-out registry 从对应 L0 冻结 spec 派生，model/checkpoint revision、seed/init、protocol lock 均未漂移。held-out_use 是 report_only；任何根据 L1 选择 checkpoint、调整 threshold 或改 prompt 都是 leakage。当前只生成计划，结果字段为空。即使未来看到失败，也必须按冻结分析报告，不能边看边调并继续称同一 L1 为最终测试。
