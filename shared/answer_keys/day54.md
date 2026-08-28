# Day 54 参考答案

1. **完整 pair 需要哪些记录？** 每个 pair id × baseline/repair × control/counterfactual，恰好四条且 join key 唯一。
2. **为什么 missing 要 fail closed？** 静默丢弃困难/失败 arm 会人为抬高 paired 指标并破坏预注册样本。
3. **paired success 与 outcome flip 是什么？** 两 arm 都成功；两 arm success 值不同。
4. **为什么要 same initial state？** 让 arm 之间只有指令/关系反事实变化，而非场景难度变化。
5. **synthetic gain 能否写成 final pair result？** 不能，只验证 join 和统计。
