# Day 37 参考答案（挑战后再看）

1. L0-only 指 repair 数据输出只含 level 0；L1/L2 即使有标签和仿真真值也只能保留为 heldout_test。
2. validation 可以使用预先划分的 L0 行；不能用 L1/L2 validation 选 prompt、阈值、checkpoint 或早停。
3. data lineage 用 source_bddl_sha256、source_episode_sha256 与 dataset_row_sha256 连接任务、原 episode 和最终行。
4. split group 防止同一轨迹/近重复片段跨 train/validation；相同 content hash 则直接拒绝。
5. 不能。synthetic registry 只测试筛选与 leakage 规则，不是已收集 demonstration，也没有授权 training。

挑战 memo 示例：L0-only 输出仅含 train/validation；L1/L2 始终是 heldout_test。data lineage 保存 source_bddl_sha256、source_episode_sha256、dataset_row_sha256。split group 和 duplicate content 检查防 leakage。B 仍是 synthetic，不代表 training 数据已生成。
