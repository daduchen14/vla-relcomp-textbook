"""Day 11 最小版本：用 autograd 和梯度下降拟合 y=2x+1。"""

import torch


# 五个确定性 fixture 样本；没有噪声，便于手算和观察收敛。
x = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0])
y = 2.0 * x + 1.0

# w、b 是待学习参数；初值故意与真值不同。
w = torch.tensor(0.0, requires_grad=True)
b = torch.tensor(0.0, requires_grad=True)

learning_rate = 0.1
for epoch in range(50):
    prediction = w * x + b
    loss = ((prediction - y) ** 2).mean()
    loss.backward()

    # 参数更新不应进入下一轮计算图，所以放入 no_grad。
    with torch.no_grad():
        w -= learning_rate * w.grad
        b -= learning_rate * b.grad

    # backward 默认累积，下一轮前必须清零。
    w.grad.zero_()
    b.grad.zero_()

# 日志数值先 detach，明确不把显示操作接到训练图。
print(f"w={float(w.detach()):.4f}, b={float(b.detach()):.4f}")
print("expected approximately w=2, b=1")
print("synthetic regression; not a VLA experiment result")
