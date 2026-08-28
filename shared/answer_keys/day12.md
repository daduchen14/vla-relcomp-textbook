# Day 12 参考答案（独立挑战后再看）

1. raw state 是某一帧的布尔量/数值；event 是按预登记规则首次满足后锁存的 episode 事实。单帧 contact=true 不一定成为 `target_contacted`。
2. A 的 first steps 依次是 contact=2、lift=4、approach=7、relation=8。lift 以第 0 帧 target_z 为基线，approach 以首次 lift 帧的 XY 距离为基线。
3. 连续两帧可减少接触抖动造成的 false positive，却会漏掉真实但只有一帧的短接触，增加 false negative；因此阈值必须冻结并人工抽查，而不是声称没有误差。
4. `relation_satisfied` 必须直接记录 `info.success`，不能要求前三个 probe 先触发。否则前序 probe 的 false negative 会抹掉真实成功，违背实验协议中“终态不证明前三段”的边界。
5. B 的 contact 闪烁在 step 1 被过滤，稳定 contact 与 lift 均在 step 5；approach 的连续条件在 step 7 被打断，直到 step 9 才触发。relation 在 step 8 已成立，所以应保留 `relation_before_reference_approached`，不能改日志迎合阶段顺序。

挑战说明示例：两帧 contact 规则降低单帧抖动的 false positive，但短暂真实接触会变成 false negative。B 的 lift 在稳定 contact 之后才记；approach 以 lift 时距离为基线，step 7 回升会清零连续计数。relation 直接来自 success，因此 step 8 独立保留，早于 step 9 的 approach 并不是应被删除的数据，而是需要人工回放核查的 probe 分歧。
