# Day 32 参考答案（挑战后再看）

1. relation 必须固定，否则行为差异同时可能来自关系与对象组合，无法区分两种处理。
2. object multiset 相同只说明场景包含同一批对象；active target/reference、姿态、遮挡和可达性仍需分别匹配。
3. matching stratum 是按尺寸、形状、可见性和可达性等预登记属性分层，不代表真实动力学与视觉难度完全相同。
4. coverage 应报告每个 relation/slot 和对象组合的原始计数；组合数多不等于样本充分或模型泛化。
5. 不能。不同物体固有外观、抓取和碰撞差异仍是 confound，需靠多对重复、分层和后续敏感性分析限制结论。

挑战 defense 示例：object combination 是 target/reference 的配对变化，relation fixed；object multiset、matching stratum、visibility 与 reachability 用来约束 confound 并描述 coverage。当前 synthetic 清单仍是 planned，不含模型 outcome，不能作 causal 结论。
