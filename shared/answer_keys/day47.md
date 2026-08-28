# Day 47 参考答案

1. **retention rate 的分母是什么？** baseline 成功的配对 episodes；分子是这些 episodes 中 repair 仍成功的数量。
2. **为何还要报告总体 success-rate delta？** retention 只看旧成功是否保留；delta 同时包含旧失败被修复的 recovery。
3. **catastrophic regression 是什么？** 同一初始状态下 baseline 成功、repair 失败的 episode，必须逐 ID 报告。
4. **为什么必须配对？** 不同初始状态会把任务难度差异混入模型差异。
5. **synthetic 通过能否说明真实 L0 保持？** 不能；它只验证统计和验收代码。
