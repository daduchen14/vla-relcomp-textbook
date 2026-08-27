# Day 5 参考答案（独立挑战后再看）

1. 两路图像都从 HWC uint8 先反转 H/W，再除以 255、permute 为 CHW、转 float32、移到 device、增加 batch 轴。
2. state 是 3 维末端位置、3 维 axis-angle 和 2 维夹爪位置，共 8 维；raw 四元数的 4 维不会原样拼接。
3. `torch.inference_mode()` 关闭 autograd 记录以服务推理；`policy.eval()` 切换模块的训练/评测行为，两者不是同一件事。
4. 锁定 SmolVLA policy 输入 key 是两路 image、state 和 task；`select_action` 返回 tensor，adapter 取 `.cpu().numpy()[0]` 交给 env。
5. CPU fixture 只验证预处理和 action 接口 shape，不证明权重可下载、CUDA 可用或模型动作有效。

挑战 B 正确图像 shape 分别为 `[1,3,3,2]` 和 `[1,3,2,1]`，state `[1,8]`，action `[1,7]`。评分器会从 B 的非单位四元数重新计算 axis-angle 和数值范围，复制 A 后改 form_id 不通过。
