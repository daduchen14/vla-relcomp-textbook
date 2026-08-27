# Day 11：线性回归——从数据、损失到参数更新

> 阶段 2 / Day 11 of 70　　建议用时：8—9 小时　　运行：PyTorch CPU

Day 10 会算梯度，今天让参数沿负梯度方向反复移动，第一次完成“数据→预测→loss→backward→更新→再预测”的训练闭环。任务是从 `fixture_` 点拟合 `y≈wx+b`。它不是 VLA，但动作回归同样要从输入预测连续数值并比较示范目标。

## 1. 学完后你能做什么

1. 区分 feature、target、prediction、parameter 与 hyperparameter；
2. 写出线性模型 `y_hat=wx+b` 和 MSE；
3. 解释 epoch、前向、反向和参数更新；
4. 手写全批量梯度下降，不依赖 optimizer；
5. 识别学习率过大、过小和梯度未清零；
6. 用 seed 复现合成噪声；
7. 用闭式解独立核对训练参数，保存 loss 历史。

## 2. 前置检查与产物

```bash
cd "$(git rev-parse --show-toplevel)"
.venv-day06/bin/python day10/code/autograd_lab.py
.venv-day06/bin/python -c 'import torch; print(torch.__version__)'
```

今天代码为 `minimal_linear_regression.py`、`train_linear_regression.py` 与测试。个人产物为逐 epoch CSV 和训练摘要 JSON。

开始前预测：若初始 w=b=0，真实关系 y=2x+1，训练后 w/b 应靠近什么？loss 下降是否自动表示测试任务 success 提高？

## 3. 今天学什么概念

### 3.1 数据中的角色

`x` 是 feature，`y` 是监督 target；模型根据 x 给 prediction。w、b 是从数据学习的 parameters；learning rate、epochs、noise scale 是人为设定的 hyperparameters。

本课生成 41 个 x，范围 [-2,2]：

```text
y = 2x + 1 + noise
```

`noise_scale=0` 时数据精确落在直线上；非零时更像现实测量。ID 与报告明确为 fixture，不能冒充模型实验。

### 3.2 线性模型与 bias

模型：

```text
y_hat = w*x + b
```

w 控制斜率，b 是 x=0 时截距。若省略 b，模型只能拟合穿过原点的线。深度网络中的 linear layer 同样含 weight 和可选 bias，只是输入输出维度更高。

### 3.3 MSE 连接预测与目标

```text
MSE = mean((y_hat-y)^2)
```

误差平方让正负不抵消，并对大误差惩罚更重。MSE 单位是 target 单位的平方；不同数据缩放下数值不可直接横比。

MSE 不是所有任务的万能 loss。VLA 动作可能各维尺度不同，还可能采用 L1、Huber、离散 token loss 或组合目标，必须遵循基线定义。

### 3.4 一个 epoch 的六步

本课每个 epoch 使用全部 41 样本：

1. `prediction=w*x+b`；
2. 计算标量 loss；
3. `loss.backward()`；
4. 记录 loss、参数、梯度；
5. `no_grad` 下按 `parameter -= lr*grad` 更新；
6. 清零 grad。

这叫 full-batch gradient descent。以后 DataLoader 会分 mini-batch；epoch 表示完整训练集大致被使用一遍，不等于一次参数更新。

### 3.5 为什么沿负梯度

梯度指向局部增长最快方向，所以减去 `lr*grad` 尝试降低 loss。learning rate 决定步长：过小收敛慢；适中稳定下降；过大可能越过谷底并振荡/发散。

梯度下降不是保证任何深度网络达到全局最优的魔法。这里只在简单凸问题上建立机械过程。

### 3.6 参数更新不应进入计算图

更新在：

```python
with torch.no_grad():
    w -= learning_rate * w.grad
```

因为更新是优化算法动作，不应成为下一轮被求导的模型前向。若直接对 requires_grad leaf 原地更新，PyTorch 会保护性报错。

### 3.7 seed 控制什么

`torch.Generator().manual_seed(seed)` 控制本课 noise 的伪随机序列。同 seed、同版本/算法/平台通常得到相同 fixture。seed 不消除随机性，也不保证所有硬件算子位级确定。

本课将 generator 显式传给 `randn`，避免修改进程全局随机状态；这使函数更容易测试。

### 3.8 训练记录的时间口径

history 在更新前记录本 epoch 的参数、loss 和梯度。因此最后一行 loss 对应“最后一次更新之前”，而报告 `final_loss` 会用更新后的最终参数重新前向。二者可略有不同。记录顺序必须写清，否则曲线与 checkpoint 对不上。

### 3.9 闭式解是独立核对

一元最小二乘有直接公式：

```text
w = Σ(x-x̄)(y-ȳ) / Σ(x-x̄)^2
b = ȳ - w*x̄
```

梯度下降应接近它。闭式解不用于大型网络，但在教学小问题上提供独立 oracle：若二者差很多，先查训练循环，不要庆祝“发现新方法”。

### 3.10 训练 loss 与研究指标

loss 下降证明优化器在当前训练目标/数据上找到更低值，不证明闭环 success、L1/L2 泛化或空间关系理解。真实项目必须分开保存 L0 训练 loss 与保留测试的行为结果。

## 4. 最小可运行代码

```bash
sed -n '1,180p' day11/code/minimal_linear_regression.py
.venv-day06/bin/python day11/code/minimal_linear_regression.py
```

预期 w≈2、b≈1。逐行指认前向、loss、backward、更新、清零。若删掉清零，先预测再运行个人副本，参数会因累积梯度偏离预期。

## 5. 完整训练程序

完整代码在 [`code/train_linear_regression.py`](code/train_linear_regression.py)。阅读数据→loss→校验→train→closed form→artifacts→CLI：

```bash
sed -n '1,150p' day11/code/train_linear_regression.py
sed -n '151,330p' day11/code/train_linear_regression.py
.venv-day06/bin/python day11/code/train_linear_regression.py --help
.venv-day06/bin/python day11/code/train_linear_regression.py
echo $?
```

默认预期 initial loss 明显大于 final loss，w 约 2、b 约 1，并接近 closed form；退出码 0。精确噪声结果以本机报告为准。

```bash
sed -n '1,15p' learner_outputs/day11/fixture_training_history.csv
sed -n '1,180p' learner_outputs/day11/fixture_training_report.json
```

CSV 每行一个 epoch；JSON 保存 seed、噪声、学习率、样本数、初末 loss、学习参数和闭式参数。

## 6. 自动化测试

```bash
.venv-day06/bin/python -m unittest -v day11.tests.test_train_linear_regression
.venv-day06/bin/python -m py_compile \
  day11/code/minimal_linear_regression.py \
  day11/code/train_linear_regression.py \
  day11/tests/test_train_linear_regression.py
```

4 项测试验证同 seed 数据一致、梯度下降接近闭式解、无噪声恢复 2/1、非正学习率被拒绝。

## 7. 动手实验

### 实验 A：零噪声

```bash
.venv-day06/bin/python day11/code/train_linear_regression.py \
  --noise-scale 0 --output-dir learner_outputs/day11/no_noise
```

先预测 w/b。预期非常接近 2/1，final loss 接近 0；这只是合成可解问题。

### 实验 B：相同 seed

用 noise=0.3、seed=7 连续运行到两个不同目录，预测报告是否一致。再只把 seed 改 8，预测数据/参数变化。相同 seed 验证复跑，两个 seed 不是“两个独立模型结论”的充分样本。

### 实验 C：学习率过小

运行 lr=0.001、epochs=20。预测 loss 下降但参数距离闭式解较远。含义是预算内学习不足，不能直接说模型容量不足。

### 实验 D：学习率过大

运行 lr=1、epochs=20。先预测可能振荡/发散。若 loss 非有限，程序拒绝；若有限但最终更差，退出码可能 1。记录实际轨迹，不手改结果。

### 实验 E：画最小 ASCII 趋势

写个人脚本读取 CSV，每隔 10 epoch 打印 epoch/loss。先预测单调趋势，再核对。默认简单问题通常下降；深度网络 loss 不保证逐 batch 单调。

## 8. 常见错误与止损

| 现象 | 先检查 | 止损时间 |
|---|---|---:|
| loss 不变 | 参数 requires_grad、更新、lr 是否为零 | 20 分钟 |
| 梯度越来越大 | 是否清零、lr 是否过大 | 15 分钟 |
| 原地更新报错 | 更新是否在 no_grad | 15 分钟 |
| shape 被广播却结果怪 | prediction/target shape 是否完全相同 | 20 分钟 |
| 两次结果不同 | seed、版本、数据生成器 | 15 分钟 |
| loss NaN/inf | 首次非有限 epoch，停止而非继续写文件 | 20 分钟 |
| 只看最终 loss 不知过程 | 查看逐 epoch CSV | 10 分钟 |

不要为“收敛”不断试学习率后只报告最好一次；真实实验的超参数搜索范围要预先记录，L1/L2 不参与选择。

## 9. 与 VLA-RelComp 的连接

行为克隆把简单 x 换成图像/state/instruction 表示，把 y 换成示范 action，把 `wx+b` 换成网络。训练循环仍是预测、loss、backward、step、记录。模型更复杂不改变实验纪律。

修复阶段只允许 L0 数据进入训练。L1/L2 指标不能像本课 closed form 一样被训练过程反复查看和调参。训练 loss、checkpoint 与行为 success 必须通过 run ID/commit 关联但保持概念分离。

Day 12 将用 `nn.Module`/`nn.Linear` 封装同一映射，学习参数注册、`state_dict` 和前向方法。

## 10. 检查点与答案

### 题 1

parameter 和 hyperparameter 有何区别？

**答案：** w/b 由训练梯度学习；learning rate/epochs 等由实验者设定，后者不能根据保留测试随意挑选。

### 题 2

为什么更新用负梯度？

**答案：** 梯度指向局部增长最快方向，负梯度是局部下降方向；learning rate 控制步长。

### 题 3

epoch 是否等于一次参数更新？

**答案：** 本课 full batch 时恰好一次；mini-batch 训练中一个 epoch 通常包含多次更新。

### 题 4

闭式解与梯度下降接近能证明什么？

**答案：** 对这个简单 fixture 目标，训练实现接近独立最小二乘解；不能证明深度模型、数据或 VLA 行为正确。

### 题 5

loss 下降为何不等于 L1/L2 success 提高？

**答案：** loss 衡量训练目标与训练数据拟合，保留环境中的闭环行为与组合泛化是不同指标。

## 11. 完成标准

**最低完成线：** 两个训练脚本、4 项测试通过；能解释完整 epoch 六步及 w/b。

**标准完成线：** 完成 A—E；比较梯度下降/闭式解、学习率/噪声/seed；保存 CSV、JSON 和个人趋势笔记。

**当天产物：** 教材训练代码与测试；个人训练历史、报告和五项对照实验。

## 12. 精确外部材料

| 材料 | 精确范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [D2L §3.1 Linear Regression](https://d2l.ai/chapter_linear-regression/linear-regression.html) | §3.1.1–3.1.4，45 分钟 | 模型、loss、解析解、minibatch 直觉 | 正态分布推导细节 |
| [D2L §3.2 Linear Regression Implementation from Scratch](https://d2l.ai/chapter_linear-regression/linear-regression-scratch.html) | 从生成数据读到训练结束，45 分钟 | 对照手写参数和 SGD | d2l 工具封装细节 |
| [PyTorch `torch.no_grad`](https://docs.pytorch.org/docs/stable/generated/torch.no_grad.html) | 描述与前两个例子，15 分钟 | 参数更新为何不建图 | forward-mode AD note |
| [PyTorch Reproducibility Notes](https://docs.pytorch.org/docs/stable/notes/randomness.html) | 开头与 Controlling sources of randomness，25 分钟 | seed 能/不能保证什么 | CUDA 算法细节暂跳 |

先独立完成本课最小循环，再对照 D2L；不要直接复制其封装而跳过梯度清零与参数更新。
