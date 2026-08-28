# Day 36 参考答案（挑战后再看）

1. decision matrix 把 evidence alignment、benefit、cost、leakage、L0 damage 与 falsifiability 放在同一冻结口径下，避免只看预期收益。
2. evidence gate 在排序前生效；未通过时，无论某个候选分数多高，都选择 STOP_NO_REPAIR。
3. unique repair 要求唯一最高候选超过冻结阈值；并列或不达阈值都停止，不能同时扩两个模块。
4. negative result 或证据不足是有效项目结论，能阻止无依据训练并保留后续 falsifier。
5. 不能。`authorized_for_training=false` 表示课程决策演练没有授予 GPU、数据生成或正式训练权限。

挑战 memo 示例：decision matrix 先检查 evidence gate，再在 unique repair 与 STOP_NO_REPAIR 中选一项。benefit 与 falsifiability 加分，implementation cost、leakage risk、L0 damage 扣分。B 应接受 negative result；authorized_for_training 仍为 false。所有输入是 synthetic，不能作 causal 研究结论。
