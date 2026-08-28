# Day 13 参考答案（独立挑战后再看）

1. `pair_id` 把同一实验单位的 A/B 两臂连在一起；它由固定字段和两条 instruction 重算，能发现错配或静默手改。
2. seed 只控制伪随机序列，不保证两个独立 reset 得到完全相同状态。配对还必须固定 `init_state_index`，并在 evaluator 中加载同一份 initial state。
3. 本日唯一允许变化的是 `instruction_text`；suite/task/BDDL、goal、target/reference、模型与 revision、推理配置 hash、seed/init 都固定。
4. 两句话看起来像同义改写不等于语义自动等价。机器只能验证结构匹配，仍需 human review 对照 BDDL goal 和起始关系，排除 target/reference 偷换或歧义。
5. pair 一臂缺失时不能把剩余一臂当独立样本计算配对差；应标记 pair incomplete、补跑或在预登记缺失规则下排除，并报告原始缺失数。

挑战设计说明示例：B manifest 的 pair_id 由 L1T1 固定键与 A/B instruction 共同生成；两臂的 seed 和 init_state_index 完全相同，且 goal、target/reference、模型 revision 与推理 hash 未变。唯一处理变量是 instruction surface。semantic 等价不能由字符串或 validator 证明，必须 human review 对照锁定语言、初态与 goal 后，才能进入真实运行。
