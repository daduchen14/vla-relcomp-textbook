# Day 45 参考答案

1. **为什么正式训练阶段仍不能读 test？** test 只用于最终无偏估计；用它选 checkpoint、调阈值或排错都会泄漏。
2. **资源 budget 与 measurement 有何区别？** budget 是运行前上限，measurement 是运行后由计时/设备/存储记录得到的事实；未运行时必须为空。
3. **launch packet 绑定哪些身份？** run id、seed、锁定 commit、split hash、frozen recipe hash、配置路径和预算。
4. **checkpoint contract 为什么不是 checkpoint？** 它只规定路径与必含状态；没有真实文件 hash、完成 step 和运行日志就没有 checkpoint 证据。
5. **本日能否声称 seed 1 正式训练完成？** 不能；状态明确是 `NOT_RUN_NO_GPU_AUTHORIZATION`。
