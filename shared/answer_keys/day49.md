# Day 49 参考答案

1. **最小消融比较什么？** repair 与“只关闭目标组件”的 ablation；二者差值估计该组件的增量作用。
2. **为什么 baseline 仍保留？** 它给出完整 repair 相对未修复系统的总收益，但不单独识别组件贡献。
3. **成本如何匹配？** 相同 split、seeds、steps/预算，并让实际 GPU-hours 相对差在冻结容差内。
4. **多变量变化有什么问题？** repair−ablation 无法归因到某一个组件。
5. **synthetic ledger 能否支持因果模型结论？** 不能，只验证分析与公平性规则。
