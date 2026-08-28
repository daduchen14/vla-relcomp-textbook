# Day 11 参考答案（独立挑战后再看）

1. target/reference 必须来自 BDDL `goal_predicate` 的第 2/3 项，而不是 `obj_of_interest`、字典首项或离机器人最近的对象。锁定 `On(target, reference)` 随后执行 `reference.check_ontop(target)`。
2. `body_id` 是当前 MuJoCo model 用来索引 `body_xpos/body_xquat` 的整数，不是跨 task、跨环境都稳定的语义 ID；语义身份仍由 BDDL 对象名承担。
3. `ObjectState.get_geom_state()` 直接返回 `body_xquat`，其存储顺序是 `wxyz`；锁定 observable sensor 另行 `convert_quat(..., to='xyzw')`。字段名必须把顺序写清，不能混用。
4. relation snapshot 至少由 target/reference 的位姿、接触与相对量组成。本课的 On 关系还要求 reference_z ≤ target_z、contact 和 XY 距离严格 `<0.07`。
5. 真值位姿和 contact 属于 privileged evaluator state。它们可用于诊断和打标签，但除非实验协议明确把它们列为模型 observation，否则送入 policy 会造成信息泄漏并改变被评估系统。

挑战 B 的 target 是 `tomato_2`、reference 是 `porcelain_bowl_2`，body_id 分别来自 B fixture 的 105/204。四元数按 `wxyz` 保存。两者虽有 contact 且 XY 很近，但 target_z 低于 reference_z，所以 `on_by_locked_formula=false`。此 privileged state 只能做 evaluator 诊断，不能偷偷加入 policy 输入。
