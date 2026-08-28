# Day 58 参考答案

1. **为什么按 strata 配额？** 确保稳定成功、恢复、损伤、稳定失败都出现，不让多数/好看类型挤掉反例。
2. **salted hash 解决什么？** 在 stratum 内给出可重建且难以按结果手选的顺序。
3. **能否人工替换“不清楚”的视频？** 不能静默替换；应记录不可用并按预注册 fallback 或保留缺失。
4. **casebook 需要哪些链接？** episode ID/hash、baseline/repair video、selection rank、stratum 与审阅状态。
5. **synthetic path 能否当视频证据？** 不能，必须真实文件存在、hash 匹配并完成双人/规则审阅。
