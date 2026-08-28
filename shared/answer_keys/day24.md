# Day 24 参考答案（挑战后再看）

1. 相同 task 的 valid_n 一致，才不会让候选因不同样本量/缺失 pattern 获得不同权重；最好进一步共享 task×seed×init episode blocks。
2. primary metric 对所有 eligible 候选先排序；只有它完全相同时才看第一 tie-break，再平才继续。不能看完结果后重排层级。
3. macro 给每个任务相同权重，避免 episode 更多的任务主导选择；同时报告 worst_task 与 micro，暴露任务塌陷和 pooled 表现。
4. 不能。L1/L2 是 held-out report-only；用它们回换会泄漏测试信息。差就如实报告，若要新选择需开启新研究周期并重新定义边界。
5. 至少保存 model ID、immutable revision、L0 scope、eligible 列表、完整 ranking/tie-break、最低 valid_n、protocol lock、policy hash 和 held-out 规则。

挑战 memo 示例：B 只允许 L0 候选进入选择；先按每任务 valid_n 判断 eligible，delta 因样本不足被排除。其余候选共享任务与分母，再按 macro 主指标、worst_task、micro 和 model ID tie-break 排序。decision 必须 freeze 模型 revision、协议与 policy hash。L1、L2 始终 held-out，不能用于回换模型。所有数字都是 synthetic fixture，只验证选择管线，不能声称真实模型已冻结。
