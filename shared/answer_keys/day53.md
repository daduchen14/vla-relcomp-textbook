# Day 53 参考答案

1. **checkpoint provenance 至少包含什么？** checkpoint/parent base/recipe/split hash、seed、step、完成状态和内容清单。
2. **为何保存 optimizer/scheduler？** 它们证明训练状态完整并支持恢复审计；评测通常只加载 policy，但 provenance 不能因此删掉训练状态。
3. **repair/baseline 评测允许什么差异？** policy artifact/condition 和对应 run id；evaluator、levels、trials、initial states、seed、成功定义必须相同。
4. **metadata hash 等于验证真实 bytes 吗？** 不等于；真实操作必须对 checkpoint bytes/目录 manifest 计算强 hash并试加载。
5. **packet 通过是否有 final repair data？** 没有，records 为 null，状态 NOT_RUN。
