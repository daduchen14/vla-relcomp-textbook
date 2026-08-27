# Day 8 自测参考答案

1. 2 个模型 × 3 个 level × 5 个 task × 5 个 seed/init = 150 个 planned episode；每模型 75 个。
2. 只有 `status=completed`、证据完整且 success 是真布尔值的 episode 才进入分母。基础设施错误和 completed 但证据缺失的记录都排除，但原记录不能删除。
3. 本课程先要求 75 个 pilot episode 的有效分母完整，再只用 L0 表现选模：25 个有效 L0、至少 10 个成功、5 个 task 都至少成功一次。L1/L2 的完成状态用于确认执行 Gate，成绩不参与选模；阈值不是 VLA-Arena 官方指标。
4. L1/L2 是预登记的研究切口 pilot；用它们选择模型或 checkpoint 会把测试表现反馈进研究设计，削弱后续保留测试边界。
5. 没有候选满足规则时输出“证据不足以选择”，下一步只补最小缺口；不能因为模型轻量或已有代码就强行指定。
