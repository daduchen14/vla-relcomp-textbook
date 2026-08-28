# Day 31 参考答案（挑战后再看）

1. 一个关系处理必须同步改变关系标签、自然语言和实现该关系的初态几何；三列共同编码一个 effective factor，不是三个独立处理。
2. seed 只控制随机序列，不能证明除关系几何外的对象姿态、相机和资产完全一致，因此还需 matched-state group 与逐项差分。
3. 不能。机器只验证 schema、hash 和变化白名单；goal 是否同步、任务是否可达必须经 BDDL/CBDDL 审查和人工 replay。
4. pair asymmetry 是真实完整 pair 中仅一臂成功的比例；计划行没有 outcome，分子和分母都不存在。
5. 一臂缺失的 pair 不进入配对效果分母，必须报告缺失原因并重跑或标无效，不能把它当失败。

挑战 defense 示例：本 relation pair 的 effective factor 由 relation、instruction 与 init_state 同步实现；matched state 用 hash 约束 fixed fields。goal sync 仍待人审，reachability 仍待 replay。当前是 synthetic、planned 清单，没有 pair asymmetry，更不能作 causal 模型结论。
