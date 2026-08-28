# Day 42 参考答案（挑战后再看）

1. one batch overfit 反复使用同一小 batch，目标是验证 pipeline/loss/gradient/optimizer/capacity 的闭环，不是泛化。
2. initial loss、final loss、reduction factor 与 target loss 必须同时报告，不能只截一段下降曲线。
3. adapter changed 证明 optimizer step 更新了允许参数；frozen hash 相同证明 backbone/head 字节未变。
4. 若不能 overfit，优先查 data pipeline、loss implementation、梯度、学习率与模块 capacity，而不是增加真实数据。
5. CPU toy 成功不代表 SmolVLA 能训练，也不产生 checkpoint、GPU 或 generalization 证据。

挑战 memo 示例：one batch overfit 应从 initial loss 降到 final loss，报告 reduction factor 与 target loss。optimizer step 使 adapter changed，而 frozen hash 不变。失败先查 data pipeline、loss implementation、capacity。当前只是 CPU toy，不是 SmolVLA/generalization。
