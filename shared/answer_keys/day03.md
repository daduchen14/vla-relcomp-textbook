# Day 3 参考答案（完成独立挑战后再看）

## 自测题答案

1. observation 是环境在某一步交给 policy 的信息集合；它是“决策输入”，不是摄像头图片的同义词。真实 evaluator 同时使用两路图像和机器人 state。
2. shape 描述轴长度，dtype 描述元素编码；`(256, 256, 3) uint8` 不能只凭 shape 推断数值是否已归一化。
3. `done=True` 可能来自 success，也可能来自 timeout。锁定实现先在 `BDDLBaseDomain.step` 写 `info['success']`，`is_success_done` 优先读取它。
4. `env.step` 是运行时分派：evaluator 只看到环境接口，实际 BDDL 环境的 `step` 再调用 `_check_success`。

## 独立挑战参考要点

- challenge fixture 的 `agentview_image` shape 是 `[2, 3, 3]`、dtype 是 `uint8`；腕部图像是 `[3, 1, 3]`。
- 三个 state 原始分量分别是 `[3]`、`[4]`、`[2]`；真实 `prepare_observation` 会把四元数转成 3 维 axis-angle，所以准备后的 state 契约是 8 维，而不是直接拼成 9 维。
- 正确答案保留 `source_kind=local_fixture_not_vla_arena_run`，不能把 fixture 摘要称为真实 episode observation。
- 调用链必须包含 `env.step` 到 `BDDLBaseDomain.step` 的运行时分派，并把 `done` 与 `info['success']` 分开解释。

口述达到“独立”需要：不看正文逐步命令，也能从锁定源码重新定位至少三个关键函数，并说明每条边是静态直接调用还是运行时分派。
