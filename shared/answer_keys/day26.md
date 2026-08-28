# Day 26 参考答案（挑战后再看）

1. observable 是可重复测量的事件，如 contact；“理解失败”是潜在机制解释，不能直接从状态读取。
2. 同一比例在 1/2 与 50/100 下证据不同，且分母定义决定哪些 pair 被排除；只报百分比不可审计。
3. 不能。falsifier 只让当前 prediction 与观察冲突；替代解释仍需自己的 intervention 和 prediction。
4. 防止把一个行为模式绑定到唯一故事，并迫使设计能区分 probe 缺陷、视觉、语言与控制等竞争解释。
5. 不应。spec 保持 pre_registered_untested；结果写到独立表并按 hypothesis_id 连接，否则会污染预注册记录。

挑战 memo 示例：每个 hypothesis 必须先写 prediction 与 falsifier，把机制词落到 observable stage。metric 明确 numerator 和 denominator，intervention 只改一个因素，control 固定 task/seed/init/model/protocol。至少两个 alternative 解释提醒我们一次恢复不是唯一 causal 证明。B 仍是 synthetic 设计，没有观察结果；运行后应另建结果表，不能回写 spec。
