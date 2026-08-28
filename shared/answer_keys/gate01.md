# Gate 1 教师要点（挑战后再看）

- 新输入必须是 Gate B：L0 task 1、seed 19、init state 0；任何 Gate A 的 task 0/seed 7 registry 都应失败。
- `success=false` 仍可证明完整 episode 执行；`status=infrastructure_error`、零 frame 或空视频不可进入分母。
- 口述必须说明：observation 是决策资料袋；random policy 产生 7 维连续动作；`BDDLBaseDomain.step` 把 success 与 timeout 合成 done；最终成功优先读 `info['success']`。
- 当前教材作者没有运行此 Gate。只有学习者未来在合格机器留下真实证据后，才可把 Gate 标为通过。
