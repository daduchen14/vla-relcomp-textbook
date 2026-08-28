# Day 25 参考答案（挑战后再看）

1. empty 目录排除旧 manifest、缓存统计和手工 registry 被误用；程序不应自动删除历史证据，而应要求新 clean path。
2. SHA-256 能高概率发现指定 bytes 是否变化并辅助逐字节重建；不能证明文件来源、签名身份、运行诚实性或科学 claim 正确。
3. spec 是锁定 commit、model、protocol lock、task×trial、seed/init 的单一来源；手填 manifest 会引入不可追踪状态，使输入与计划分叉。
4. rehearsal 只有 deterministic synthetic adapter、无 GPU；formal Gate 4 要接真实 VLA-Arena adapter，保存日志/视频/异常，主动中断并 resume，再生成真实 task_stats/evidence。
5. 比较中断前后 checkpoint/registry：已 COMPLETED episode 的 execution count 不增加、episode_id 不重复、未完成行才继续；再核对日志和 receipt。

挑战 memo 示例：B 必须从一个 empty 目录开始，由 spec 的 commit、model revision 和 protocol lock 生成 manifest；synthetic adapter 只回填教学 registry，再由 registry 生成 task_stats/report，最后对指定产物写 SHA-256 receipt。Gate 4 的 CPU rehearsal 能证明这条管线可重建，但 hash 不证明科学 claim，也不证明真实模型运行。正式 Gate 还要在授权 GPU 上接真实 adapter，保留视频/异常并演示中断 resume；本课不能把 synthetic 成功位冒充 baseline。
