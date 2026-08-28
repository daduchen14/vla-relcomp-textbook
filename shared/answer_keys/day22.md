# Day 22 参考答案（挑战后再看）

1. 0/5 只是有限样本中没观察到成功，未知成功概率仍可能大于零。Wald 在边界退化；Wilson 会保留正上界，表达小样本不确定性。
2. macro 对任务等权：先算各 task rate 再平均；micro 对有效 episode 等权：先加 successes 和 valid_n 再相除。分母不等时两者通常不同。
3. ERROR 可能是环境、I/O、资源或 adapter 故障，不等价于策略完成了 episode 且失败。它进入 planned/missing 计数，修复后重跑；若项目另有保守口径，应与 complete-case 结果并列而不是偷偷改值。
4. 不表示“参数有 95% 后验概率位于本次固定区间”，也不表示 95% episode 会成功。它描述该构造方法在重复抽样下的长期覆盖性质。
5. 不能。Wilson 处理给定有效二项样本的抽样不确定性；若 missing 与难任务或失败倾向相关，点估计本身可能有选择偏差，需要缺失诊断/敏感性分析。

挑战 memo 示例：B 的每任务表必须同时保留 successes、valid_n 和 95% Wilson，不能只抄百分比。micro 把所有有效 episode 合并，macro 对每个任务等权，因此分母不均时两者不同。ERROR 只进入 missing，不自动算失败；否则运行故障会改变模型指标。区间描述有效二项样本的抽样不确定性，不能修复非随机缺失。当前输入是 synthetic fixture，只能验收计算管线，不能声称真实 VLA-Arena baseline 已统计完成。
