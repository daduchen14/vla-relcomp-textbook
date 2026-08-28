# Day 70 参考答案与复盘

仅在提交 Gate 8 限时版本后阅读。完整参考模块见 `day70_reference.py`。

1. observation summary 应数据驱动地保留每个 key 的 shape/dtype，不能硬编码 A。
2. funnel 的后续阶段通过要求此前所有阶段也通过，分母保持同一 repair cohort。
3. 配对四格方向为 baseline→repair：n01 recovery、n10 damage。
4. 首个失败按 episode_id 稳定排序，并定位第一个 false stage。
5. 参数只改变 `meets_threshold` 的决策边界，不改变原始 delta；synthetic evidence 仍不能支持正式项目主张。
6. Machine rehearsal 通过不等于 Gate 8；fresh clone 限时、禁止答案、live oral 和现场改参必须由学习者完成。
