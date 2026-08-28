# Day 57 参考答案

1. **Wilson interval 为什么优于简单 Wald？** 在小样本或接近 0/1 时覆盖更稳健，区间不会轻易越出 `[0,1]`。
2. **n01/n10 分别是什么？** baseline fail→repair success（recovery）与 baseline success→repair fail（damage）。
3. **McNemar 使用哪些格？** 只使用 discordant pairs `n01+n10`，检验两个方向是否对称。
4. **p>alpha 能否说无效果？** 不能，只表示当前数据不足以拒绝等边际；仍需报告 effect 和 interval。
5. **为什么必须从 raw episodes 重建 counts？** 防止转移方向错、漏 episode 或摘要篡改。
