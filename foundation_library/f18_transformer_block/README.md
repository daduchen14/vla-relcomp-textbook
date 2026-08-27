# Day 18：Transformer block 最小实现

> 建议用时：7—9 小时
>
> 前置知识：Day 12 的模块与参数、Day 13 的训练循环、Day 16 的序列/mask、Day 17 的单头 self-attention
>
> 今日目标：把注意力、残差连接、LayerNorm 和前馈网络装成一个可训练的 pre-norm Transformer block
>
> 真实性声明：本课只在免费 CPU 上训练合成 `fixture_` 序列分类器，不是 VLA、真实语言模型或 VLA-Arena 结果

## 完成标准与当天产物

**最低完成线**：运行最小脚本；能画出两个子层以及两条残差路径，解释为什么 block 输入和输出 shape 相同。

**标准完成线**：运行工程脚本和 6 个测试；能说明 LayerNorm、残差、FFN、dropout 与 mask 各自职责；完成两个变量实验，并明确区分训练集拟合与未知数据泛化。

当天产物：

- `foundation_library/f18_transformer_block/code/minimal_transformer.py`：约 36 行的最小 block；
- `foundation_library/f18_transformer_block/code/transformer_lab.py`：复用 Day 17 注意力的 pre-norm block、fixture 分类器、训练与 JSON 证据；
- `foundation_library/f18_transformer_block/tests/test_transformer_lab.py`：shape、padding、梯度、错误配置、训练和复现测试；
- `learner_outputs/foundation_library/f18_transformer_block/transformer_report.json`：本机生成的 CPU 教学结果，不提交 Git。

今天结束阶段 2。Day 19 会把 Day 15 的图像和今天的 Transformer 接起来，把图像切成 patch 并映射为视觉 token。

## 一、今天学什么概念

### 1. 注意力还不是完整 Transformer

Day 17 的注意力只负责让各 token 交换信息。一个标准 Transformer block 还需要稳定训练与逐位置变换的结构。可把它想成两次“加工—保留原件”的流水线：

```text
x ── LayerNorm ── Self-Attention ── (+ x) ── y
y ── LayerNorm ── Feed Forward   ── (+ y) ── output
```

本课采用 **pre-norm**：每个子层之前先归一化。原论文常画 post-norm，即残差相加后归一化。两种都真实存在，不能只看 `LayerNorm` 有无而忽略它的位置。课程用 pre-norm 是因为结构清晰、深层训练通常更稳定；今天不做架构优劣研究。

### 2. 残差连接：让子层学习“改多少”

若子层记为 `F`，普通网络输出 `F(x)`，残差形式输出：

```text
y = x + F(x)
```

这要求 `x` 与 `F(x)` shape 相同。注意力和 FFN 最终都把 D 维投影回 D 维，因此 `[N,L,D]` 在 block 前后保持不变。直觉上，子层不必从零重建全部信息，只需学习在原表示上增加怎样的修正；反向传播也有一条直接通过加法的梯度路径。

残差不是把历史结果保存到磁盘，也不是 RNN 的隐藏状态。它就是当前前向图中的逐元素相加。

### 3. LayerNorm：按每个 token 的特征归一化

`nn.LayerNorm(D)` 对最后一维 D 做归一化。输入 `[N,L,D]` 时，每个样本的每个 token 独立计算自身 D 个特征的均值与方差，然后再用可学习缩放与偏移调整。

它与图像中常见的 BatchNorm 不同：LayerNorm 不依赖同 batch 其他样本的统计，因此可自然处理不同 batch 大小和序列。公式可写为：

```text
LN(x) = gamma * (x - mean) / sqrt(var + epsilon) + beta
```

这里 mean/var 沿最后一维算。归一化改善数值尺度，但不会自动修复错误 mask、错误标签或数据泄漏。

### 4. FFN：每个位置共享的两层小网络

注意力负责 token 之间通信；Feed-Forward Network（FFN）则对每个位置独立应用同一组两层网络：

```text
FFN(x) = Linear(D,H) → GELU → Linear(H,D)
```

它不在序列位置间混合，位置间交互已经由注意力完成；但所有位置共享 FFN 参数。中间维 H 常大于 D，为每个 token 提供更强的非线性变换能力。本课默认 `D=8, H=32`。

GELU 是平滑激活函数。今天应理解“没有激活时两层线性仍等价于一层线性”，不要求手算 GELU 精确值。

### 5. dropout：只在训练模式随机丢弃

dropout 在训练时随机把部分分量置零并做尺度补偿，用来减轻过拟合；`model.eval()` 时关闭。默认脚本设为 0，是为了 CPU 教学输出严格复现。实验可设非零值观察波动，但不能因此声称真实性能变好。

这也解释为什么评测前必须调用 `model.eval()`：即使当前默认 dropout 为 0，工程习惯仍要正确。以后模型还可能有其他训练/评测行为不同的层。

### 6. padding 为什么每个子层之后仍要处理

Day 17 屏蔽了 PAD key 并清零 PAD query 输出，但残差路径会把原输入加回来，FFN 的 bias 也可能在零输入上产生非零输出。因此本课在 block 最后再次执行：

```python
vectors.masked_fill(~valid_mask.unsqueeze(-1), 0.0)
```

这是一种明确的教学契约：无效位置离开 block 时必须全零。真实上游模型可能选择不同内部约定，但必须保证 attention mask 在正确位置生效，不能凭“PAD embedding 是零”推断后面永远是零。

### 7. 本课 fixture 分类任务

程序生成 `[sample_count,5,8]` 随机序列，每条有效长度为 2—5。标签由所有有效 token 第一维的和是否大于 0 决定。分类器执行：

```text
TransformerBlock → masked mean pooling → Linear(D,2)
```

这让前向、loss、backward、optimizer step 都能在 CPU 上实测。训练与评测使用同一批 fixture，只用于证明模型可拟合、梯度连通，不能称为泛化准确率。真实实验必须像 Day 13/14 那样划分数据，并在后续严格隔离 L1/L2。

### 8. 与 VLA-RelComp 的关系

视觉 Transformer、语言模型和多模态 VLA 都会堆叠许多类似 block。真实模型通常使用多头注意力、更大 D/H、更多层、不同位置编码与优化 kernel，但核心数据流仍可拆成今天这四块：注意力、残差、归一化、FFN。

理解 block 后，后续遇到 VLA 输入 shape、mask、OOM 或 checkpoint 参数名时就不再只看到黑盒。仍要坚持边界：本课没有下载权重，没有使用 GPU，没有运行真实 VLA-Arena。

## 二、今天做什么

### 步骤 0：从仓库根目录确认环境

```bash
cd "$(git rev-parse --show-toplevel)"
git branch --show-current
.venv-foundation_library/f06_environments_dependencies/bin/python -c "import torch; print(torch.__version__)"
```

若导入失败，回到 Day 6 和 Day 9 的固定环境；止损 10 分钟。

### 步骤 1：运行最小 block

运行前先预测输入 `(2,4,8)` 经过注意力和 FFN 后的 shape：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f18_transformer_block/code/minimal_transformer.py
```

预期 input/output 都是 `(2,4,8)`，同时打印参数量和第一个输出 token。具体浮点值来自固定 seed 的随机初始化，只是本机教学输出。

最小版使用 PyTorch 官方 `nn.MultiheadAttention(num_heads=1, batch_first=True)`，让代码保持在 15—40 行；工程版则复用 Day 17 自己实现的单头注意力，便于逐层检查 mask。

### 步骤 2：运行完整训练闭环

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f18_transformer_block/code/transformer_lab.py
```

默认在 32 条 fixture 序列上训练 80 epoch。预期：

- shape 从 `(32,5,8)` 到 `(32,5,8)`；
- final loss 小于 first loss；
- training accuracy 接近或达到 `32/32`；
- padding output L1 为 0。

这些是当前 CPU 路径的预期现象，不是事先保证的真实研究成绩。查看证据：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m json.tool \
  learner_outputs/foundation_library/f18_transformer_block/transformer_report.json | sed -n '1,100p'
```

确认 `result_type`、超参数、shape、首尾 loss、训练准确率和所有 `fixture_` ID。

### 步骤 3：运行测试

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m unittest foundation_library.f18_transformer_block.tests.test_transformer_lab -v
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f18_transformer_block/code/transformer_lab.py --help
```

应有 6 个测试通过。测试明确覆盖注意力与 FFN 两条梯度路径，而不仅是“输出 shape 看起来对”。

## 三、完整代码导读

先完整阅读 [`code/minimal_transformer.py`](code/minimal_transformer.py)。类里只有四个组件：两个 LayerNorm、一个官方单头注意力、一个两层 FFN。前向的核心是：

```python
normalized = self.norm1(x)
attended, _weights = self.attention(normalized, normalized, normalized)
x = x + attended
x = x + self.feed_forward(self.norm2(x))
```

同一个 normalized 同时作为 Q/K/V，因此是 self-attention；两次 `x + ...` 就是残差路径。

工程版 [`code/transformer_lab.py`](code/transformer_lab.py) 复用 `foundation_library.f17_attention.code.attention_lab.SingleHeadSelfAttention`，这是课程连续性的实际代码接口，而不是只在文字里说“上一课学过”。

`TransformerBlock.forward` 先检查 `[N,L,D]` 和 `[N,L] bool` 契约，然后做两个 pre-norm 子层。若 Day 17 注意力拒绝全 PAD 序列，它把错误转换为当前层的 `TransformerContractError`，使调用者得到统一接口。

`FixtureSequenceClassifier` 使用 masked mean：有效 token 求和后除以有效数量。它没有使用第一个位置冒充 CLS，因为本课输入没有定义 CLS token。真实模型的 pooling 或动作读取位置必须以其上游实现为准。

`run_experiment` 延续 Day 13 的训练顺序：

```text
zero_grad → forward → CrossEntropyLoss → backward → Adam.step
```

训练结束调用 `eval()` 和 `no_grad()` 再生成报告，避免把训练图保留在评测证据中。

## 四、动手实验

### 实验 A：改变 FFN 隐藏宽度

先预测 `hidden_dim` 从 32 降为 8 时参数量如何变化，训练准确率是否必然降低：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f18_transformer_block/code/transformer_lab.py \
  --hidden-dim 8 \
  --output learner_outputs/foundation_library/f18_transformer_block/hidden8.json
```

预期参数减少；这个 fixture 任务简单，仍可能完全拟合。结果只能说明该训练集对较窄模型也容易，不能推广到 VLA。

### 实验 B：只训练 1 个 epoch

先预测首尾 loss 会不会几乎相同、准确率是否下降：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f18_transformer_block/code/transformer_lab.py \
  --epochs 1 \
  --output learner_outputs/foundation_library/f18_transformer_block/epoch1.json
```

与默认 JSON 比较。一个 epoch 的报告中 first loss 与 final loss 是同一个记录值；准确率通常较低，但随机初始化可能产生波动。必须如实写观察值。

### 实验 C：打开 dropout

先预测 `dropout=0.3` 时，同一训练过程会更稳定还是引入随机扰动：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f18_transformer_block/code/transformer_lab.py \
  --dropout 0.3 \
  --output learner_outputs/foundation_library/f18_transformer_block/dropout03.json
```

训练时 dropout 引入随机屏蔽，但 seed 已固定，所以同环境重跑仍应复现。最终 `eval()` 会关闭 dropout。不要用单个训练集数字判断正则化是否改善泛化。

### 实验 D：破坏残差连接

先预测把第一条 `vectors = vectors + ...` 改为 `vectors = ...` 后，shape 是否改变、训练是否一定失败。临时修改、运行测试与默认训练，再恢复。

shape 仍相同，训练也可能成功，因此 shape 测试无法证明残差存在。应通过代码结构检查与更深入的行为测试确认架构。这说明“测试通过”只证明其覆盖范围内的性质。

## 五、检查点（含答案）

### 1. 一个基础 Transformer block 的两个主要子层是什么？

**答案**：self-attention 子层与逐位置 FFN 子层；二者各自配合残差连接和归一化，常再加入 dropout。

### 2. 为什么残差相加要求子层输出回到 D 维？

**答案**：逐元素相加要求 shape 相同。输入是 `[N,L,D]`，注意力输出投影和 FFN 第二个线性层都回到 D，才能与输入相加。

### 3. `LayerNorm(D)` 对 `[N,L,D]` 的哪些元素一起归一化？

**答案**：对每个样本、每个 token 的最后 D 个特征单独归一化，不跨 batch 或序列位置汇总。

### 4. attention 与 FFN 在信息流上的分工是什么？

**答案**：attention 在序列位置之间读取和混合信息；FFN 对每个位置独立应用同一非线性变换。两者组合既能跨位置交互，又能加工每个位置的特征。

### 5. 本课 100% training accuracy 能否叫做泛化能力？

**答案**：不能。训练和评测使用同一 fixture batch，只证明可拟合和训练链路连通。泛化需要独立、未参与优化与选择的测试数据；VLA 项目还必须严格保留 L1/L2。

## 六、常见错误与止损

- **残差 shape 不匹配**：检查 FFN 最后一层是否回到 D、attention 输出是否为 `[N,L,D]`；止损 15 分钟。
- **LayerNorm 报 normalized shape 错误**：最后一维必须等于初始化的 embedding_dim；止损 10 分钟。
- **全 PAD 导致错误**：检查数据 collate 和有效长度，任何序列至少有一个真实 token；止损 10 分钟。
- **padding 输出不为零**：确认 block 最后执行 mask，且 mask 为 bool；止损 10 分钟。
- **loss 不下降**：恢复默认 seed、学习率、hidden dim 与 dropout，确认梯度测试通过；止损 20 分钟。
- **把 fixture 拟合写成 VLA 结果**：查看 JSON 的 `result_type`，撤回超出证据的表述；这是科研边界错误。

## 七、精确外部材料

1. [Attention Is All You Need](https://arxiv.org/abs/1706.03762)：阅读第 3.1 节 Encoder and Decoder Stacks、第 3.3 节 Position-wise Feed-Forward Networks，以及 Figure 1 左半；看完应能指出 attention、FFN、residual 和 norm。原论文为 post-norm，注意与本课 pre-norm 对比。
2. [PyTorch `TransformerEncoderLayer` 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html)：阅读参数 `d_model`、`nhead`、`dim_feedforward`、`dropout`、`batch_first`、`norm_first`；看完应能把本课参数映射到官方层。Nested Tensor 暂时跳过。
3. [PyTorch `LayerNorm` 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html)：阅读公式、normalized_shape 与输入输出 Shape；看完应解释为何 `[N,L,D]` 使用 `LayerNorm(D)`。
4. [PyTorch `Dropout` 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.Dropout.html)：阅读训练时 Bernoulli 屏蔽和评测时 identity 的说明；看完应知道为什么调用 `eval()`。
5. [Dive into Deep Learning 11.7 The Transformer Architecture](https://d2l.ai/chapter_attention-mechanisms-and-transformers/transformer.html)：阅读 11.7.2 Positionwise Feed-Forward Networks、11.7.3 Residual Connection and Layer Normalization、11.7.4 Encoder；解码器 causal attention 暂时跳过。

## 今日收尾与阶段 2 回顾

请画出完整 block，给每条箭头写 shape，并在笔记中回答：如果 mask 错了，哪怕 loss 能下降，实验是否可信？答案是否定的。至此你已经从 tensor、梯度和线性回归走到 CNN、embedding、attention 与 Transformer。阶段 3 将把这些组件用于多模态与 VLA 数据流，而不是立即下载大模型或租 GPU。
