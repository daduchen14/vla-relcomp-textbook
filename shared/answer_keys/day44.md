# Day 44 参考答案

1. **为什么固定模型初始化、改变训练 seed？** 真实微调底座相同；本课要测 mini-batch 顺序等随机性，不应把不同底座混进 seed 方差。
2. **梯度裁剪记录哪个 norm？** 记录裁剪前 norm 和是否超过阈值；仅记录裁剪后的值无法看到异常幅度。
3. **NaN 注入怎样才算安全通过？** 在 backward/optimizer step 前发现，停止运行，且 adapter hash 不变。
4. **recipe hash 有什么作用？** 把输入、超参数和边界绑定；任何改动都会产生新 hash，防止正式运行前静默漂移。
5. **为什么 recipe 仍写未授权？** toy 稳定性只是教学证据，不能替代真实 SmolVLA/CUDA pilot 与正式训练授权。
