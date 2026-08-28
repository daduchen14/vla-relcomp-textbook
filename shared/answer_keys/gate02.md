# Gate 2 参考答案（提交后再看）

应选择 `candidate_cobalt`。它有完整的 25 个 L0 有效分母、13 个 L0 成功，并覆盖全部 5 个 task。`candidate_amber` 的 L1/L2 表面成功更多，但不能参与选模；其 L0 只有 24 个有效 episode 且成功数不足。

应排除：

- `candidate_amber-L0-T0-S101`：`infrastructure_error`；
- `candidate_amber-L2-T4-S113`：虽然 status 写 completed，但 `evidence_complete=false`。

有效分母：`candidate_amber` 为 L0 24、L1 25、L2 24；`candidate_cobalt` 三个 level 都是 25。

可接受的下一步最小实验示例：固定 `candidate_cobalt`、L0 task 0、seed 101 与对应 init state，不新增模型或 suite；解析任务文件并建立对象/关系结构表，为 Day 9 的只读行为诊断准备输入。
