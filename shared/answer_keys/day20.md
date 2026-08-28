# Day 20 参考答案（挑战后再看）

1. L2 是 strong OOD/report-only 测试；它与 L0 共享冻结 model、seed/init、protocol lock 和 taxonomy。
2. first unmet 标签定位可观测链最早断点，不是 causal 机制结论；`REFERENCE_APPROACH_FAILURE` 不能直接等同“语言关系没理解”。
3. ENV_INVALID 与模型失败分开；success 为空是允许的，且不进入模型分母。
4. success=true 但前序 probe=false 记 `SUCCESS_WITH_PROBE_GAP`；success=false 但四 probe 全 true 记 `INCONSISTENT_SUCCESS_SIGNAL`，两者都需视频/日志复核。
5. 当前分类来自 synthetic fixture，不能推断真实 L2 失败占比或模型 OOD 能力。

挑战 memo 示例：B 的 L2 strong OOD 计划与 L0 冻结口径一致。分类器按 first unmet event 给行为标签，ENV_INVALID 不算模型失败。若 success 与 probe gap 冲突，必须保留异常并查视频，不能强行修顺序。所有标签都是 behavioral 描述，不是语言、视觉或控制的 causal 结论；真实机制要靠 Day 26 之后的反事实和 oracle 区分。
