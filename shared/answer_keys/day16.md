# Day 16 参考答案（挑战后再看）

1. `run_id` 标识共同的 protocol/model/config/suite/level 批次；`episode_id` 标识其中一个 task×seed×init。episode 通过 `run_id` foreign key 归属 run。
2. CSV 行号会随排序、筛选和合并变化，不能当 primary key；规范化身份的 hash 可重算并检测错配。
3. `PLANNED` 的空 `success` 表示 missing / 尚未观察；`success=0` 表示实际运行后失败。混用会把没跑的 episode 污染进分母。
4. evidence path 同时包含 run_id/episode_id，使 result、events、video、exception 不能在不同 episode 间静默串线。
5. `COMPLETED` 必须有 success/steps/wall_seconds；环境异常应进入 INVALID 或 FAILED 与 exception 证据，不得补 success=0。

挑战 memo 示例：B 的 run_id 是 run-level primary key，episode_id 是 episode primary key，episodes.run_id 是 foreign key。PLANNED 行的结果保持 missing，不能写 success=0，因为 0 是真实失败。每条 evidence 路径都嵌入两级 ID。进入 COMPLETED 前必须补结果；异常要保留日志并改变状态。这样排序或续跑不会改变身份，也不会把未运行样本塞进成功率分母。
