# Day 30 参考答案（挑战后再看）

1. `On(target, reference)` 表示目标在参照物上；参数顺序反转会成为另一个命题，不能由距离自动纠正。
2. 单帧谓词可能由碰撞、弹跳或临界几何短暂触发；连续窗口才定义课程中的稳定终态。
3. 因为夹爪仍接触目标时，关系可能依赖机械臂支撑或约束，尚不能视为释放后的终态。
4. 不能。geometric proxy 只用于发现实现或阈值冲突，正式关系仍由锁定项目的 BDDL predicate 决定。
5. 不能。冲突也可能来自 proxy 定义、日志同步、对象 ID、接触边界或动态场景，需回看 trace 与视频。

挑战 memo 示例：先固定 On 或 In、target 与 reference，再以 official predicate 为权威信号。terminal relation 必须在 gripper release 后满足 sustained 窗口；geometric proxy 只标出 signal conflict。B 输入是 synthetic，不能把 detector 输出直接解释成模型失败的 causal 证据。
