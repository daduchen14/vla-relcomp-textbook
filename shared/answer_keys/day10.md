# Day 10 参考答案（独立挑战后再看）

1. `done` 表示环境要求 episode 结束；锁定环境把 `success or timeout_done` 赋给 done。因此 timeout 可以 done=true、success=false。
2. evaluator 调 `bool(info.get('success', done))`：只要 `info.success` 存在就以它为准；只有旧式/缺字段环境才退回 done。
3. 本套件 15 个 goal 都是 `On(target, reference)`。运行时 `reference.check_ontop(target)` 要求 reference_z ≤ target_z、两物体接触、XY 距离严格 `<0.07`。
4. 精确等于 `0.07` 不通过，因为源码用 `<` 而非 `<=`；只满足高度和距离、没有 contact 也不通过。
5. 数值 fixture 只复现锁定布尔公式，不能证明 MuJoCo 的 body position/contact、对象 ID 映射或真实 episode success。

挑战 B：`exact_xy_boundary` 与 `target_below_reference` 的 On 都为 false；后者因 timeout 而 done=true 但 success=false。`success_on_horizon` 的 On 为 true，所以 done/success 都为 true，`info.timeout=false`，即使输入中的 `timeout_done` 同时为 true。
