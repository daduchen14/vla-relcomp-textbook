# Day 59 参考答案

1. **planned/attempted 有何区别？** planned 是 manifest 中全部 runs；attempted 排除从未启动的 not-run。
2. **failure rate 分母是什么？** failed/attempted，不是 failed/planned 或 failed/completed。
3. **失败运行资源是否计成本？** 必须计；资源已消耗，删除会系统性低估方法成本。
4. **peak memory 怎样汇总？** 报所有 attempted runs 的最大峰值，并保留 per-run 值/测量来源。
5. **synthetic ledger 能否当云账单？** 不能；真实表需设备监控、墙钟、退出码和账单/单价版本。
