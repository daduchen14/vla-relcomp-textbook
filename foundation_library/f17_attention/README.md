# Day 17：注意力——查询、键和值

> 建议用时：7—9 小时
>
> 前置知识：Day 9 的矩阵与 shape、Day 12 的线性层、Day 16 的 `[N,L,D]` 序列向量与 mask
>
> 今日目标：从矩阵乘法实现缩放点积注意力，再搭出带 padding mask 的单头 self-attention
>
> 真实性声明：本课输出是随机生成的 `fixture_` 注意力轨迹，不是 VLA 成绩，也不能单独作为模型机制解释

## 完成标准与当天产物

**最低完成线**：运行最小脚本；能写出 Q、K、V、score、weight、output 的 shape，并解释 softmax 为什么沿最后一维进行。

**标准完成线**：运行完整脚本和 6 个测试；能区分 key mask 与 query mask；完成至少两个温度/mask 实验，并准确表述注意力权重的证据边界。

当天产物：

- `foundation_library/f17_attention/code/minimal_attention.py`：约 28 行的矩阵乘法注意力；
- `foundation_library/f17_attention/code/attention_lab.py`：带投影、缩放、padding mask、错误检查和 JSON 证据的单头 self-attention；
- `foundation_library/f17_attention/tests/test_attention_lab.py`：shape、归一化、mask、梯度、非法输入和复现测试；
- `learner_outputs/foundation_library/f17_attention/attention_report.json`：本机生成的 fixture 权重记录，不提交 Git。

Day 18 会把这个注意力层与残差连接、LayerNorm 和前馈网络装配成最小 Transformer block。

## 一、今天学什么概念

### 1. embedding 之后还缺什么

Day 16 给每个 token 一个向量和位置，但每个位置仍像独立坐在座位上的学生。理解“把红杯放在蓝碗左边”时，“左边”必须与目标“红杯”和参照物“蓝碗”发生联系。注意力提供一种可训练的信息读取方式：每个位置根据当前需求，从序列所有有效位置汇总信息。

先用图书馆类比：

- Query（查询，Q）：我现在想找什么；
- Key（键，K）：每本资料用于匹配查询的标签；
- Value（值，V）：资料真正携带、被取回的内容。

查询和键的相似度决定读多少，值决定最终读到什么。类比只帮助入门；在代码中 Q、K、V 都是浮点 tensor，由线性层从输入向量投影得到。

### 2. self-attention 为什么叫 self

若 Q、K、V 都来自同一条输入序列，就是 self-attention。输入 `X` 为 `[N,L,D]`，三组可学习权重产生：

```text
Q = X W_Q
K = X W_K
V = X W_V
```

本课是单头并令投影维度等于 D，因此三者仍为 `[N,L,D]`。之后：

```text
scores  = Q K^T / sqrt(D)       # [N,L,L]
weights = softmax(scores)        # [N,L,L]
output  = weights V              # [N,L,D]
```

`K^T` 只转置最后两个维度。每个 batch 独立计算，不应把不同样本的 token 相互注意。

### 3. 一行 score 矩阵是什么意思

`scores[n,i,j]` 表示第 n 条序列中，第 i 个 query 与第 j 个 key 的匹配分数。固定 i 看一整行，就是“位置 i 打算从哪些位置读取”。softmax 沿最后一维 j 做归一化，使一个有效 query 的所有可用 key 权重之和约等于 1。

随后用这行权重对所有 value 加权求和。因此一个输出位置不再只有自己的 embedding，而是包含按当前参数聚合的上下文。

注意：权重大不自动等于“人类意义上最重要”，更不证明因果机制。权重会受投影、层数、残差、后续网络等影响。本课报告将其称为 synthetic attention trace，而不是 explanation。

### 4. 为什么除以 `sqrt(D)`

维度增大时，随机向量点积的幅度往往增大。若直接送入 softmax，分布容易极端饱和：一个位置接近 1，其余接近 0，梯度变小。除以键维度平方根把数值尺度拉回较温和范围，这就是 scaled dot-product attention 的“scaled”。

完整公式通常写为：

```text
Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V
```

本课 `d_k=D`。多头注意力会把总维度分给多个头，届时缩放因子是每个头的 `d_k`，不是序列长度。

### 5. padding mask 到底屏蔽谁

Day 16 为短序列补 PAD。若不 mask，真实 query 可能把一部分权重分给不存在的 PAD key。工程版本先做：

```python
scores = scores.masked_fill(~valid_mask.unsqueeze(1), float("-inf"))
weights = torch.softmax(scores, dim=-1)
```

`valid_mask` 是 `[N,L]`，`unsqueeze(1)` 变为 `[N,1,L]`，它沿所有 query 广播，屏蔽无效 **key 列**。`softmax(-inf)=0`，所以 PAD key 的权重为零。

但 PAD 位置自己仍充当一个 query，数学上仍会产生一行归一化权重。为了让教学输出清楚，完整实现随后把无效 query 的权重行和输出向量清零。于是：

- mask 的列：不允许别人读取 PAD；
- mask 的行：不让 PAD 自己产生下游输出。

如果一整条序列全是 PAD，所有 key 都会变为负无穷，softmax 将出现 NaN。本课主动拒绝这种输入，而不是事后隐藏 NaN。

### 6. 温度怎样改变权重形状

把 scores 除以较小的温度，softmax 更尖锐；除以较大的温度，权重更平坦。本课工程脚本通过缩放 query 投影等价地观察这种变化：

```text
temperature < 1：分数绝对差扩大，常更集中
temperature > 1：分数差缩小，常更平均
```

“集中”不等于“更正确”。没有训练目标、验证集和任务指标时，只能描述分布变化。

### 7. 与 VLA-RelComp 的关系

Transformer 型视觉语言模型会在语言 token、视觉 token 或融合序列之间反复进行注意力计算。空间关系指令需要目标、参照物与关系词相互影响，注意力是信息交互的一种核心机制。

但后续诊断不能看到一张注意力图就断言“模型没看懂左边”。VLA-RelComp 的可信结论仍来自匹配反事实、四段行为事件、受控 oracle 和 episode success。注意力轨迹最多是辅助观察，不能替代行为证据。

## 二、今天做什么

### 步骤 0：回到仓库根目录

```bash
cd "$(git rev-parse --show-toplevel)"
git branch --show-current
.venv-foundation_library/f06_environments_dependencies/bin/python -c "import torch; print(torch.__version__)"
```

环境导入失败时回看 Day 6/9，止损 10 分钟，不临时升级依赖。

### 步骤 1：运行最小注意力

运行前先在纸上写 shape：Q 是 `[3,2]`，那么 `Q @ K.T`、weights、`weights @ V` 分别是什么？

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f17_attention/code/minimal_attention.py
```

预期：score 和 weights 都是 `(3,3)`，输出是 `(3,2)`，每行权重和为 1。第三个 token `[1,1]` 同时匹配两个方向，因此它的读取结果会混合多个 value。

### 步骤 2：运行带 mask 的工程版本

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f17_attention/code/attention_lab.py
```

当前免费 CPU 实验无需下载数据或模型。默认输入为 `(2,4,8)`，score 为 `(2,4,4)`，输出回到 `(2,4,8)`。预期有效行权重和误差接近 0，第二条序列最后一个 PAD key 的最大权重为 0。

查看报告：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m json.tool \
  learner_outputs/foundation_library/f17_attention/attention_report.json | sed -n '1,140p'
```

检查 `sample_ids` 均为 `fixture_`，mask 第二行末尾为 false，第二条权重矩阵最后一列与最后一行均为 0。

### 步骤 3：运行单元测试与帮助

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m unittest foundation_library.f17_attention.tests.test_attention_lab -v
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f17_attention/code/attention_lab.py --help
```

应有 6 个测试通过。梯度测试确认注意力没有因错误使用 `no_grad` 而切断训练图；全 PAD 测试确认非法输入在 NaN 发生前被拒绝。

## 三、完整代码导读

[`code/minimal_attention.py`](code/minimal_attention.py) 是完整最小实现。为了看清公式，它令 `Q=K=V=tokens`，没有可学习投影、batch 和 mask。必须先把这约 28 行跑通，再读工程版。

[`code/attention_lab.py`](code/attention_lab.py) 的 `SingleHeadSelfAttention` 依次完成：

1. 三个无 bias 线性层得到 Q、K、V；
2. `keys.transpose(-2,-1)` 只交换序列与特征维；
3. 除以 `sqrt(embedding_dim)`；
4. 对无效 key 填 `-inf`，再 softmax；
5. 权重乘 V，最后通过输出投影；
6. 清零无效 query 的权重行与输出。

它返回 `AttentionResult` 而不是只返回 output，目的是教学与测试能检查 weights。在生产模型中是否返回权重要权衡显存和调试需要。

`make_fixture_batch` 模拟 Day 16 编码器结果：两条序列都补到 L=4，第二条只有前三个位置有效。向量由固定 seed 随机生成，没有语言语义。`token_labels` 只是“目标、动作、关系、参照”的教学标签，绝不能把随机权重解释成真实语言行为。

工程版的参数量来自四个 `D×D` 线性投影。今天不实现多头、dropout、causal mask、缓存或高性能 fused kernel；Day 18 先把正确的单头组件装进 block，再逐步扩大视野。

## 四、动手实验

### 实验 A：改变温度，观察“尖锐程度”

先预测 temperature 为 0.25 与 4.0 时，哪一个通常让每行最大权重更大。运行：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f17_attention/code/attention_lab.py --temperature 0.25 \
  --output learner_outputs/foundation_library/f17_attention/temp025.json
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f17_attention/code/attention_lab.py --temperature 4.0 \
  --output learner_outputs/foundation_library/f17_attention/temp4.json
```

打开两个 JSON，对比 `first_sequence_weights` 每行的最大值。预期低温通常更集中，高温更平坦。这里只能说权重分布变化，不能说低温理解更好。

### 实验 B：去掉缩放因子

先预测 embedding 维度很大时，不除 `sqrt(D)` 会让 softmax 更平还是更尖。临时把代码中的：

```python
scores = queries @ keys.transpose(-2, -1) / math.sqrt(self.embedding_dim)
```

改成：

```python
scores = queries @ keys.transpose(-2, -1)
```

运行默认命令并比较权重。随机样本中通常更尖锐，但单次结果不等于普遍证明。完成后恢复缩放行，并重新运行测试。

### 实验 C：故意取消 key mask

先预测若注释 `scores.masked_fill(...)`，第二条序列的最后一个 PAD key 是否会得到非零权重。临时注释该行并运行测试：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m unittest \
  foundation_library.f17_attention.tests.test_attention_lab.AttentionLabTests.test_padding_key_and_query_are_zeroed -v
```

预期测试失败，因为真实 query 会读取 PAD 列。恢复代码后测试应通过。这个实验说明 mask 不是装饰性 metadata，而是参与注意力数值计算的契约。

### 实验 D：全 PAD 为什么要提前拒绝

直接运行一小段：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python - <<'PY'
import torch
from foundation_library.f17_attention.code.attention_lab import SingleHeadSelfAttention

model = SingleHeadSelfAttention(4)
model(torch.zeros(1, 2, 4), torch.zeros(1, 2, dtype=torch.bool))
PY
```

运行前预测错误信息。预期抛出“每条序列至少需要一个有效 token”。结果说明边界输入应在产生 NaN 前失败，并给调用者明确原因。

## 五、检查点（含答案）

### 1. Q、K、V 分别决定什么？

**答案**：Q 表示当前位置的查询需求；K 用于和查询计算匹配分数；V 是按照归一化权重实际汇总的内容。三者通常来自输入的不同可学习线性投影。

### 2. 输入 `[N,L,D]` 时，单头 score 与 output 的 shape 是什么？

**答案**：`QK^T` 得到 `[N,L,L]`；它与 `[N,L,D]` 的 V 相乘后，output 为 `[N,L,D]`。

### 3. softmax 为什么使用 `dim=-1`？

**答案**：固定一个 query 后，要在所有 key 位置之间分配读取权重；key 是 score 的最后一维，所以沿最后一维归一化，每个有效 query 行和为 1。

### 4. 只清零 PAD 的 token embedding，为什么还需要注意力 mask？

**答案**：位置编码、投影 bias 或其他层仍可能让 PAD 表示非零；即使 value 为零，把概率分给 PAD 也会稀释真实 token。mask 从 score 层阻止读取无效 key。

### 5. 注意力权重最大的位置能否直接称为模型决策原因？

**答案**：不能。权重只是某层某头的信息混合系数，会受上下游层与残差影响；因果判断需要受控干预和行为结果。VLA-RelComp 仍以 episode 与四段状态事件为主要证据。

## 六、常见错误与止损

- **矩阵乘法 shape 错误**：打印 Q、K、`K.transpose(-2,-1)`，只转最后两维；止损 15 分钟。
- **softmax 行和不是 1**：确认沿 `dim=-1`，并只检查有效 query 行；止损 10 分钟。
- **出现 NaN**：检查是否整条序列全 PAD、温度是否为正、score 是否含无穷；止损 15 分钟。
- **PAD 权重不是 0**：确认 mask 在 softmax 之前填到 key 列，而不是事后只清 output；止损 15 分钟。
- **mask dtype 错误**：使用 `torch.bool`，不要把 0/1 float mask 直接交给本课接口；止损 5 分钟。
- **把随机权重解释成空间关系理解**：检查报告 `result_type`；本课没有训练模型也没有 VLA 行为证据，应立即撤回该结论。

## 七、精确外部材料

1. [Attention Is All You Need](https://arxiv.org/abs/1706.03762)：精读第 3.2.1 节 Scaled Dot-Product Attention，并对照 Figure 2 左图；看完应能默写核心公式和 `sqrt(d_k)` 的理由。第 3.2.2 多头部分留给后续扩展。
2. [PyTorch `scaled_dot_product_attention` 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)：阅读函数签名、伪实现和 Shape legend；比较官方 mask 约定与本课手写实现。暂时跳过 GQA 和具体 fused backend 选择。
3. [PyTorch `MultiheadAttention` 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html)：只阅读类简介、`batch_first`、`key_padding_mask` 和输入输出 shape；今天不替换手写单头实现。
4. [Dive into Deep Learning 11.3 Attention Scoring Functions](https://d2l.ai/chapter_attention-mechanisms-and-transformers/attention-scoring-functions.html)：阅读 11.3.1 Masked Softmax 和 11.3.3 Scaled Dot-Product Attention；看完应理解有效长度怎样进入 softmax。
5. [Attention is not Explanation](https://aclanthology.org/N19-1357/)：阅读摘要、第 1 节与第 6 节 Conclusion；理解为何不能把注意力图直接当因果解释。实验细节和所有数据集暂时跳过。

## 今日收尾

在笔记中写下四个等式 `Q=XWq`、`K=XWk`、`V=XWv`、`softmax(QKᵀ/√d)V`，并标注每一步 shape。再用一句话分别解释 key mask 和 query 清零。完成后，你已经拥有 Day 18 Transformer block 中最核心的信息交互部件。
