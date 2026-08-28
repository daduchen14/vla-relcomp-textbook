# Day 46 参考答案

1. **重复运行允许改变什么？** 只改变预注册 seed、run id 和隔离 output dir；recipe、split、commit 与评测规则必须相同。
2. **为什么报告样本标准差？** 三个 seed 是随机过程的样本，样本标准差用 `n−1` 校正描述其离散度；仍须同时展示每 seed 值。
3. **为什么不能只选最好 seed？** 这会系统性高估方法效果并隐藏不稳定性。
4. **总预算怎样算？** 各 repeat 的 `max_gpu_hours` 相加，必须不超过冻结 cap；真实消耗仍要运行后测量。
5. **本日有哪些 checkpoint？** 只有 checkpoint 2–3 合同，状态 NOT_RUN；没有真实文件或方差结果。
