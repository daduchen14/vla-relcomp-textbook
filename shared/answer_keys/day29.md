# Day 29 参考答案（挑战后再看）

1. net progress 表示曾缩短多少距离；entry 要连续进入预注册半径。可以有大量进展但仍未到区域。
2. 未抬起时目标可能仍在原处，被机械臂靠近/推动；这不是搬运阶段，混入会污染解释。
3. 不能。正确参照来自任务语义；nearest other 只用于发现错误吸引模式。
4. 不能。它不保证最终进入、保持或距离足够小，且短序列不稳定。
5. 不能。也可能是视觉对象选择、控制轨迹、动态障碍或日志/probe 错误，需 oracle 干预。

挑战 memo 示例：先由 lifted segment 限定搬运阶段，再固定 reference_object_id 并分析 distance trajectory。net progress 和 decrease fraction 描述趋势，approach 仍需 entry threshold 的 sustained 窗口。若另一个对象持续更近，标记 wrong reference，但不直接作 causal 语言结论。B 是 synthetic trace，不是模型结果。
