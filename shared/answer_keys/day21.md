# Day 21 参考答案（挑战后再看）

1. seed 控制随机流，init state 决定实际场景起点；任一漂移都会把“重复执行差异”和“输入条件差异”混在一起。还必须固定 task、模型 revision、协议锁与 BDDL。
2. success match 只比较两次终态成功位；exact match 还要求 contact、lift、approach、relation 四段全部匹配。两次都失败也可能 stage 路径不同。
3. 看过结果再挑 episode 会产生选择偏差，得到的一致率只描述被结果筛过的样本。预注册边界任务/seed strata，并保留 mismatch，才能说明分母是什么。
4. 不能。4/4 只表示这 4 个有效 pair 在所定义指标上匹配；样本小、任务覆盖有限，而且 exact match 也不是逐帧相同。应报告 `4/4`，而非只写 100%。
5. NIST 将高度受控、短期同条件变化归入 repeatability；reproducibility 常涉及日期、仪器、实验室或其他条件变化。文件沿项目口径命名，但证据主张必须使用更窄含义。

挑战 memo 示例：B 先预注册新任务，再为每个 source episode 生成 original/repeat；每个 pair 都冻结 seed、init_state、模型和协议。统计同时保留 success match、逐 stage match、exact match 与 mismatch pair，且报告原始分子/分母。success 相同但 stage 不同说明行为链不完全重复，success 不同则说明终态也不稳定；二者都不能直接归因于语言、视觉或控制。这里的 reproducibility 文件只验证 synthetic fixture 和分析管线，没有真实 GPU/VLA-Arena 重跑，因此不能声称模型已经可复现。
