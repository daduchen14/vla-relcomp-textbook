# Day 51 参考答案

1. **final matrix 展开哪些轴？** condition × seed × level × suite × trials；pair/oracle 是另行标记的评测维度。
2. **为什么先写 stop rules？** 防止看到结果或资源消耗后随意加条件、换 seed、延长预算。
3. **failed run 应怎样处理？** 保留失败/缺失状态，按统一重试规则处理，不能换一个更好 seed。
4. **canonical hash 有何意义？** 字段排序和空白不影响身份，任何语义字段变化都会改变 hash。
5. **frozen 是否等于 authorized？** 不等于；当前只冻结计划，Gate 6 未通过且 GPU 未授权。
