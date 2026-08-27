# Day 7 参考答案（独立挑战后再看）

1. action token 是语言模型词表末端的一组离散 ID；`predict_action` 把 ID 映射到 255 个 bin center，再用 checkpoint 的 `q01/q99` 统计反归一化，最终得到 7 维连续动作。
2. 锁定 OpenVLA adapter 的 policy 实际读取 agent-view RGB 与语言 prompt。`prepare_observation` 虽构造 8 维 state，但 `get_vla_action` 没有把 state 传给 processor 或 `predict_action`；不能因为 dict 中存在 state 就声称模型使用了它。
3. 公平比较至少固定 VLA-Arena commit、suite、level、task_id、seed、init_state、trial 数和 max steps；同时分别固定两个模型 checkpoint。接口/模型大小可以不同，因为它们正是被比较对象。
4. 两个 planned manifest 只能比较接口、配置和资源需求；在两边真实 completed registry 出现前，success 必须留空，不能推出谁更强。
5. `unnorm_key` 选择训练数据对应的动作统计。key 错误可能直接触发断言；即使 shape 仍为 7，错误统计也会改变每个动作维度的物理尺度。

独立挑战：唯一公平的是 `pair_alpha`。`pair_beta` 混入 seed 差异，`pair_gamma` 混入 task_id 差异；两者都不能把观测差异只归因于模型。
