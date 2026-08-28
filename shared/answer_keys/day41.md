# Day 41 参考答案（挑战后再看）

1. global batch = micro batch × gradient accumulation × world size；显存主要受 micro batch 影响，统计节奏还受 global batch 影响。
2. mixed precision 可降低部分权重/激活占用，但 optimizer state、算子支持与数值稳定仍需实测。
3. LoRA 是低秩参数高效微调方法；本课 single repair 已选 adapter-only，因此 LoRA 明确关闭，不能叠加第二项修复。
4. memory estimate 基于规划参数量、每参数字节、激活与 safety factor；not profiled 表示它不能替代 CUDA 峰值测量。
5. checkpoint/save_every/keep_last/resume 与 max steps 共同限制损失范围；authorized=false 意味着配置通过仍不能启动 CUDA。

挑战 memo 示例：adapter-only 遵守 single repair，LoRA 关闭。micro batch、gradient accumulation 决定 global batch；mixed precision 进入 memory estimate，并保留至少 20% headroom。checkpoint 支持 resume 且受 max steps 限制。当前 not profiled、未 authorized，不能启动 CUDA。
