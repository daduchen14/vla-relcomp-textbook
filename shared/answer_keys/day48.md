# Day 48 参考答案

1. **为什么 L1/L2 分层？** 两层代表不同 OOD 难度或关系变化，合并会让样本更多的层支配结论并隐藏异质性。
2. **paired success-rate delta 怎么算？** 同层 repair 成功率减 baseline 成功率；配对转换还需分别报告 failure→success 与 success→failure。
3. **预注册什么？** 层级、主指标、每层最低 delta、是否允许 pooling、缺失与失败处理规则。
4. **为什么不能挑最好 level？** 看完结果后只报改善层会造成选择偏差。
5. **synthetic 结果能否视为 held-out OOD 证据？** 不能；它只验证分层分析实现。
