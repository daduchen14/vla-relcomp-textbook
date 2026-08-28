# Day 40 参考答案（挑战后再看）

1. action loss 让 control/normalized 都预测同一动作 target；pair consistency 直接惩罚两臂预测差异，两者解决的问题不同。
2. loss weight 冻结两项相对贡献；看完验证结果再改权重会引入选择偏差。
3. 只有 relation_adapter.weight 的 requires_grad 为真；backbone 与 action_head 都属于 frozen parameter group。
4. frozen 参数的 gradient 应为 None；adapter gradient 非零只证明 toy backward 连通，不证明训练有效。
5. 本日没有 optimizer step；CPU toy 不是 SmolVLA forward，更不是 training evidence。

挑战 memo 示例：action loss 与 pair consistency 按冻结 loss weight 相加。parameter group 只让 relation_adapter requires_grad；backbone、action_head frozen 且无 gradient。本日不做 optimizer step，只运行 CPU toy，不是 SmolVLA 或 training evidence。
