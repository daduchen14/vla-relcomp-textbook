# Day 33 参考答案（挑战后再看）

1. normalized instruction 把 BDDL truth 按固定 TARGET、START、ACTION、GOAL 顺序暴露，减少表面表达差异，但属于特权诊断输入。
2. recovery 的分母是 control failures；damage 的分母是 control successes。两个分母不同，必须同时给原始计数。
3. stage effect 能指出干预后最早出现系统差异的可观测阶段；它不能直接识别模型内部模块。
4. oracle 文本更长、token 分布不同，也可能改变 policy 行为，因此恢复不只存在“语义变清楚”一个解释。
5. 不能。L1/L2 BDDL truth 用作 diagnostic oracle 有 leakage 边界，不能直接变成最终训练或部署特征。

挑战 memo 示例：normalized instruction 固定 TARGET、START、ACTION、GOAL，并使用 BDDL truth。对 paired outcome 同时报 recovery、damage 和每个 stage effect。该 synthetic 演示没有模型运行；oracle leakage、文本长度等替代解释仍在，不能作 causal 内部机制证明。
