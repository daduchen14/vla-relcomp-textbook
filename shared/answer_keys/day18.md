# Day 18 参考答案（挑战后再看）

1. L0 五个 task 必须分别报告并拥有相同 planned denominator；宏平均不能掩盖某 task 少跑。
2. seed 控制随机序列，init_state_index 指定实际初态位置；两者同时写入 episode 身份。
3. PLANNED video path 是将来证据地址，`video_exists=false` 是诚实状态；空文件或假 mp4 不能变成 evidence。
4. COMPLETED 必须对应非空 `.mp4`、bytes 与 sha256；环境异常用 INVALID/exception，不补 success=0。
5. 当前只建立 L0 registry/index，未加载模型，不能报告 baseline success、失败分布或可诊断样本量。

挑战 memo 示例：B 是 L0 五个 task 各 3 次的等 denominator 计划；每个 episode 的 seed 和 init_state 都进入稳定身份。所有状态仍是 PLANNED，video 路径只是登记目标，exists=false 不代表模型失败。真实 runner 完成后必须检查非空 mp4、hash 与 task 对应关系；环境异常不能进入模型失败分母。当前产物只能证明计划覆盖，不能称为 L0 baseline 结果。
