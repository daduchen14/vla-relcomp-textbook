# Day 15：图像张量、卷积和 CNN

> 建议用时：7—9 小时
>
> 前置知识：Day 9 的 tensor/shape，Day 12 的 `nn.Module`，Day 13 的训练循环，Day 14 的 `Dataset`/`DataLoader`
>
> 今日目标：看懂图像的四维形状，亲手观察卷积核滑动，并在免费 CPU 上训练一个最小图像分类 CNN
>
> 数据声明：本课图像与结果全部由程序合成，ID 均以 `fixture_` 开头，不是 VLA 或 VLA-Arena 实验结果

## 完成标准与当天产物

**最低完成线**：运行 `minimal_convolution.py`，能指出输入、卷积核和输出的 shape，并解释为什么输出空间尺寸从 `5×5` 变成 `3×3`。

**标准完成线**：再运行完整 CNN、通过 5 个测试，完成至少两个变量实验，并用自己的话解释“卷积提局部特征，分类头把特征变成类别分数”。

当天产物：

- `day15/code/minimal_convolution.py`：固定卷积核的最小可运行例子；
- `day15/code/cnn_lab.py`：fixture 图像数据集、CNN、训练、评测和 JSON 证据；
- `day15/tests/test_cnn_lab.py`：数据、shape、错误输入、学习能力与复现测试；
- `learner_outputs/day15/cnn_report.json`：本机运行后生成的个人练习结果，不提交 Git。

这些知识会在 Day 19 用于把图像切成视觉 token；CNN 与 Transformer 处理图像的方式不同，但二者都必须先严格管理 shape。

## 一、今天学什么概念

### 1. 计算机眼里的图片不是“画面”，而是一组数字

人看一张相机图像，会直接看到杯子、桌面和机械臂。程序首先看到的却是像素数组。灰度图每个位置通常只有一个强度值；RGB 彩色图每个位置有红、绿、蓝三个通道。在 PyTorch 中，一批图像通常写成：

```text
[N, C, H, W]
 N: batch 中有几张图
 C: 通道数，灰度常为 1，RGB 常为 3
 H: 高度
 W: 宽度
```

例如 `(8, 3, 224, 224)` 表示 8 张 RGB 图，每张高宽都是 224。顺序不能凭感觉猜。把 `[N,H,W,C]` 误送给期待 `[N,C,H,W]` 的网络，即便总元素数相同，语义也完全错了。

本课使用 `(N,1,8,8)` 的极小灰度图。类别 0 是横向亮带，类别 1 是竖向亮带。任务很简单，是为了把注意力放在数据流上，而不是追求成绩。

### 2. 为什么不能把每个像素直接交给一个巨大线性层

图像有两个有用特点：相邻像素通常相关；同一种局部形状可能出现在不同位置。若把 `224×224×3` 个像素直接连到大量神经元，参数很多，而且没有显式利用“邻近”和“平移”结构。

卷积层使用一个小窗口，也叫卷积核或 kernel，在图像上逐位置滑动。同一组核参数会在所有位置重复使用，这叫**权重共享**。它带来两种直觉：

1. 一个 3×3 小核只先看局部邻域；
2. 学到的“边缘探测方法”可以在图片左边或右边复用。

严格地说，PyTorch 的 `Conv2d` 实现的是深度学习里通常称为 cross-correlation 的运算：它不会先把核翻转。工程上仍统一叫卷积。今天只需记住，每个输出位置等于一个局部窗口与卷积核逐元素相乘再求和，若有 bias 再加 bias。

### 3. 卷积输出尺寸怎样计算

只看一个空间方向，输入大小为 `I`，核大小为 `K`，padding 为 `P`，stride 为 `S`，dilation 暂设为 1，则输出大小为：

```text
floor((I + 2P - K) / S) + 1
```

最小脚本中 `I=5, K=3, P=0, S=1`，所以输出为 `(5-3)/1+1=3`，二维结果就是 `3×3`。完整 CNN 使用 `padding=1`，使 3×3 卷积前后的高宽保持 8；接着 `MaxPool2d(2)` 每 2×2 取最大值，高宽从 8 变 4。

不要死背最终数字。每经过一层，都写出 shape：

```text
[N, 1, 8, 8]
 -> Conv2d(1, 4, 3, padding=1): [N, 4, 8, 8]
 -> ReLU:                         [N, 4, 8, 8]
 -> MaxPool2d(2):                 [N, 4, 4, 4]
 -> flatten:                      [N, 64]
 -> Linear(64, 2):               [N, 2]
```

其中 4 是输出通道数，可以理解为模型同时学习 4 种局部特征探测器。`[N,2]` 的两个数叫 logits，是尚未归一化的类别分数。`CrossEntropyLoss` 接受 logits 和整数标签，内部完成合适的对数 softmax；训练时不要先手动 `softmax`。

### 4. CNN 究竟“学”了什么

最小脚本手动把一个竖直边缘核写入权重，所以我们知道它寻找什么。完整网络则从随机权重开始。损失函数比较 logits 与正确标签，反向传播算出每个核参数应怎样变化，优化器执行更新。许多轮以后，某些卷积核可能对横向结构更敏感，另一些对竖向结构更敏感。

这不等于模型形成了人类式的“条纹概念”。我们能可靠陈述的是：在当前 fixture 分布上，参数更新降低了分类损失，并让输出类别与标签一致。若想知道它是否能处理新位置、新噪声或完全不同图案，还必须设计分离的测试集。

### 5. 这与 VLA-RelComp 有什么关系

VLA 的 observation 经常包含相机图像。模型必须把像素变成能参与语言理解和动作预测的表示。现代 VLA 未必使用传统 CNN 作为主视觉编码器，也可能使用 Vision Transformer，但以下基础完全共通：

- 输入通道顺序、dtype、数值范围必须正确；
- batch 维不能丢；
- 空间特征怎样缩小、展开或变成 token 必须可追踪；
- 分类准确不等于闭环机器人任务成功；
- 合成教学结果绝不能冒充 VLA-Arena 基线。

今天只解决“像素怎样通过一个可训练视觉网络”这一小段，不下载模型、不使用 GPU、不运行真实 VLA 环境。

## 二、今天做什么

### 步骤 0：回到仓库根目录并确认环境

```bash
cd "$(git rev-parse --show-toplevel)"
git branch --show-current
.venv-day06/bin/python --version
.venv-day06/bin/python -c "import torch; print(torch.__version__)"
```

预期看到教材分支、Python 版本和 PyTorch 版本。如果 `.venv-day06/bin/python` 不存在，按 Day 6 建环境，再按 Day 9 的固定依赖安装；止损时间 10 分钟，不要改用一个来源不明的全局环境凑合。

### 步骤 1：运行 29 行最小卷积

先不要看输出，手算三个 shape，然后运行：

```bash
.venv-day06/bin/python day15/code/minimal_convolution.py
```

预期关键输出：

```text
input shape: (1, 1, 5, 5)
kernel shape: (1, 1, 3, 3)
output shape: (1, 1, 3, 3)
```

`feature map` 中正负数表示局部左右亮度差的方向和强弱，并不是概率。

### 步骤 2：运行完整 CNN

```bash
.venv-day06/bin/python day15/code/cnn_lab.py
```

默认程序生成 40 张 8×8 fixture 图像，训练 30 个 epoch，并写出 JSON。预期看到 loss 下降、训练集准确率接近或达到 100%。这是容易的合成训练任务，所以它只能证明训练管线能工作，不能证明泛化，更不能证明 VLA 能识别空间关系。

查看证据：

```bash
.venv-day06/bin/python -m json.tool learner_outputs/day15/cnn_report.json | sed -n '1,60p'
```

重点核对 `run_id`、`result_type`、超参数、首尾 loss、样本数和 `fixture_` ID。

### 步骤 3：运行测试

```bash
.venv-day06/bin/python -m unittest day15.tests.test_cnn_lab -v
```

应有 5 个测试通过。测试不仅检查“程序没崩”，还检查输入契约、输出 `(batch,2)`、错误 shape 会被拒绝、训练确实降低 loss，以及同 seed 的摘要可复现。

## 三、完整代码导读

最小版本完整保存在 [`code/minimal_convolution.py`](code/minimal_convolution.py)，只有约 29 行，可先完整读懂。四个关键动作是：

1. 以二维列表写像素，再 reshape 为 `[1,1,5,5]`；
2. 构造 `[3,3]` 的固定核；
3. 将其复制到 `Conv2d` 的 `[out_channels,in_channels,K,K]` 权重；
4. 前向计算并打印 feature map。

工程版本见 [`code/cnn_lab.py`](code/cnn_lab.py)。它不是突然出现的大成品，而是把前几天的部件接起来：

- `StripeDataset` 延续 Day 14 的 `Dataset`，每次返回 image、label、稳定 ID；
- `TinyStripeCNN` 延续 Day 12 的 `nn.Module`；
- `run_experiment` 延续 Day 13 的 `zero_grad → forward → loss → backward → step`；
- `set_seed` 延续 Day 14 的复现纪律；
- `accuracy` 使用 `eval()` 与 `no_grad()`，避免评测时构建梯度图；
- `main` 负责参数解析、错误出口和 JSON 证据，不把业务逻辑塞进命令行层。

核心模型只有下面这条数据流：

```python
self.features = nn.Sequential(
    nn.Conv2d(1, channels, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(kernel_size=2),
)
self.classifier = nn.Linear(channels * 4 * 4, 2)

def forward(self, images):
    features = self.features(images)
    return self.classifier(torch.flatten(features, start_dim=1))
```

`flatten(..., start_dim=1)` 特意保留第 0 维 batch。如果直接 `torch.flatten(features)`，所有样本会被揉成一条向量，分类头就无法知道哪部分属于哪张图。

完整训练没有划分验证集，是有意保留的教学限制：今天只证明 CNN 能拟合一个最小视觉任务。Day 13 已讲过训练/验证差异，做完下面实验时必须明确称它为“训练集准确率”。严谨的未知样本泛化结论需要额外 holdout 数据。

## 四、动手实验

每个实验都按“先预测—再改/运行—观察—解释”进行。不要只抄最终数字。

### 实验 A：padding 怎样改变空间尺寸

先预测：把最小脚本中的卷积改成 `padding=1` 后，输出是 `3×3` 还是 `5×5`？

修改 `day15/code/minimal_convolution.py`：

```python
conv = nn.Conv2d(1, 1, kernel_size=3, padding=1, bias=False)
```

然后运行最小脚本。预期输出高宽变为 5，因为输入四周补了一圈 0，使核中心也能访问边界位置。观察完成后恢复原行，避免后续输出与教材不一致。这个实验说明 padding 控制边界信息和空间大小，并不是“提高准确率”的魔法开关。

### 实验 B：卷积通道数改变参数量

先预测：通道从 4 改为 1，参数量会增加还是减少？准确率是否必然下降？运行：

```bash
.venv-day06/bin/python day15/code/cnn_lab.py \
  --channels 1 \
  --output learner_outputs/day15/channels_1.json
```

再与默认结果中的 `parameter_count` 比较。预期参数显著减少；这个任务太简单，准确率仍可能很高。因此“更小模型仍成功”只说明 fixture 任务不需要很大容量，不能推出真实视觉任务也只需一个通道。

### 实验 C：训练轮数不足会怎样

先预测只训练 1 个 epoch 时，loss 和准确率会怎样：

```bash
.venv-day06/bin/python day15/code/cnn_lab.py \
  --epochs 1 \
  --output learner_outputs/day15/epoch_1.json
```

与默认 30 epoch 比较。通常 1 epoch 的 loss 更高、准确率更低，但小数据与随机初始化可能让准确率波动。结论应依据保存的数字，而不是为了迎合预测修改描述。

### 实验 D：同 seed 是否真的复现

先预测两个报告中除输出路径外哪些字段应一致，然后运行：

```bash
.venv-day06/bin/python day15/code/cnn_lab.py --seed 22 \
  --output learner_outputs/day15/seed22_a.json
.venv-day06/bin/python day15/code/cnn_lab.py --seed 22 \
  --output learner_outputs/day15/seed22_b.json
diff -u learner_outputs/day15/seed22_a.json learner_outputs/day15/seed22_b.json
```

预期 `diff` 没有输出。在当前 CPU 教学路径上，数据、初始化与 shuffle 都由 seed 固定。以后换 GPU、算子或版本时，设置 seed 仍不等于跨平台逐位一致，届时还要记录软件与硬件环境。

## 五、检查点（含答案）

### 1. `(16, 3, 64, 64)` 中每个数字分别表示什么？

**答案**：16 张图；每张 3 个通道；高度 64；宽度 64。PyTorch `Conv2d` 默认按 `[N,C,H,W]` 解释。

### 2. 输入 8、卷积核 3、padding 1、stride 1 时，输出空间大小是多少？

**答案**：`floor((8+2×1-3)/1)+1=8`。二维高宽都为 8。

### 3. 为什么 `Linear` 前从 `[N,4,4,4]` 变为 `[N,64]`，而不是 `[64N]`？

**答案**：每张图各有 `4×4×4=64` 个特征，batch 中的样本必须保持分离。`flatten(start_dim=1)` 只合并通道和空间维，保留第 0 维 N。

### 4. 使用 `CrossEntropyLoss` 时，为何模型不先调用 softmax？

**答案**：它期望未归一化 logits，并在内部以数值更稳定的方式组合 log-softmax 与负对数似然；提前 softmax 会改变输入语义并可能降低数值稳定性。

### 5. fixture 训练准确率 100% 能否证明 VLA 在 PrepositionCombinations 上成功？

**答案**：不能。数据、任务、模型和指标都不同；本结果只验证一个合成条纹分类教学管线。真实 VLA 结论必须来自冻结协议下的真实环境 episode 和 success 判定。

## 六、常见错误与止损

- **报 `expected ... to have 1 channels`**：先打印输入 shape，确认是 `[N,1,H,W]`；止损 10 分钟。
- **报矩阵乘法 shape 不匹配**：逐层打印 shape，重点核对池化后的 `channels×4×4`；止损 15 分钟，不要盲改 `Linear` 数字。
- **标签 dtype 报错**：`CrossEntropyLoss` 的类别标签应为 `torch.int64` 且 shape 为 `[N]`；止损 10 分钟。
- **loss 不下降**：先恢复默认 `--learning-rate 0.2 --epochs 30 --channels 4 --seed 15`；止损 15 分钟。
- **把准确率叫 VLA 成绩**：立刻检查报告的 `result_type` 和样本 ID；这是表述错误，不应继续推导研究结论。
- **环境导入失败**：回到 Day 6/9 的虚拟环境命令，不升级或混装随机版本；止损 15 分钟。

## 七、精确外部材料

1. [PyTorch `Conv2d` 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv2d.html)：阅读参数 `in_channels`、`out_channels`、`kernel_size`、`stride`、`padding`，以及输入/输出 Shape；看完应能独立算本课输出尺寸。暂时跳过 complex dtype、groups 的高级组合和非零 padding mode。
2. [PyTorch Neural Networks 教程](https://docs.pytorch.org/tutorials/beginner/blitz/neural_networks_tutorial.html)：从 “Define the network” 读到 “Update the weights”；重点跟踪 `Conv2d → pooling → flatten → Linear`。暂时不要求记住 CIFAR-10 的完整网络。
3. [PyTorch `CrossEntropyLoss` 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)：阅读第一种 target 情况（class indices）及 Shape；看完应知道 logits 是 `[N,C]`、标签是 `[N]`。暂时跳过类别概率 target 与高维像素级损失。
4. [Dive into Deep Learning 8.2 Convolutions for Images](https://d2l.ai/chapter_convolutional-neural-networks/conv-layer.html)：阅读 8.2.1–8.2.4，亲手对照“互相关运算、卷积层、边缘检测、学习卷积核”。看完应能把本课固定核与可学习核联系起来。
5. [Dive into Deep Learning 8.3 Padding and Stride](https://d2l.ai/chapter_convolutional-neural-networks/padding-and-strides.html)：阅读 8.3.1–8.3.2，完成输出公式练习；多通道细节留到理解本课 shape 之后。

## 今日收尾

请在学习笔记中留下四行：输入 shape、卷积后 shape、池化后 shape、logits shape；再写一句“本结果是 fixture 训练结果，不是 VLA 实验结果”。能够从像素一路解释到 loss，才算真正完成 Day 15。下一步 Day 16 会把离散文字变成 token 和 embedding，开始从视觉支线转向 Transformer 所需的序列表示。
