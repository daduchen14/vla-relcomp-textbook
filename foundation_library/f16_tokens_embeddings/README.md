# Day 16：序列、token、embedding 与位置

> 建议用时：7—9 小时
>
> 前置知识：Day 9 的 tensor/shape、Day 12 的 `nn.Module` 与线性层、Day 14 的 batch
>
> 今日目标：亲手走通“文字 → token → ID → 向量 → 加入位置”的完整路径
>
> 数据声明：所有指令和输出都是 `fixture_` 教学材料，不是模型推理或 VLA 实验结果

## 完成标准与当天产物

**最低完成线**：运行最小脚本，能够解释 `(1,4)` 的 ID 张量为什么变为 `(1,4,4)` 的向量张量，并说明 token 与 token ID 不是同一个东西。

**标准完成线**：运行工程脚本和 6 个测试；能解释 `<PAD>`、`<UNK>`、有效位 mask、embedding 与位置编码各自解决什么问题；完成至少两个变量实验。

当天产物：

- `foundation_library/f16_tokens_embeddings/code/minimal_embedding.py`：24 行左右的字符 token、查表和可学习位置示例；
- `foundation_library/f16_tokens_embeddings/code/sequence_lab.py`：确定性字符词表、批量补齐、mask、正弦位置编码和 JSON 报告；
- `foundation_library/f16_tokens_embeddings/tests/test_sequence_lab.py`：6 个数据契约与复现测试；
- `learner_outputs/foundation_library/f16_tokens_embeddings/sequence_report.json`：本机生成的教学输出，不提交 Git。

Day 17 会直接使用形状为 `[batch, sequence, embedding]` 的序列向量和有效位 mask 来计算 self-attention。

## 一、今天学什么概念

### 1. 为什么神经网络不能直接吃字符串

程序可以保存字符串 `"拿起红杯"`，但矩阵乘法需要数值。将文字交给 Transformer 前，要完成一条明确的数据管道：

```text
原始字符串
  ↓ tokenizer 按规则切分
token 序列
  ↓ vocabulary 查表
整数 ID 序列
  ↓ nn.Embedding 查表
连续向量序列
  ↓ 加位置编码
带内容和顺序信息的序列表示
```

这五层不能混称为“编码”。token 是切分后的符号；token ID 是该符号在词表中的整数编号；embedding 是模型为某个 ID 保存或学到的连续向量。ID 3 并不表示 token 比 ID 2“大”，整数只是查表地址。

本课使用字符级 tokenizer：每个中文字符算一个 token。它很容易手算，适合教学，但不等于 SmolVLA、OpenVLA 或其他语言模型的真实 tokenizer。真实模型通常使用子词或字节级方案，而且词表与模型权重成套发布，不能自行替换。

### 2. 词表为什么必须稳定

词表把 token 映射为 ID：

```text
<PAD> -> 0
<UNK> -> 1
拿 -> 某个固定整数
杯 -> 某个固定整数
```

若同一个 checkpoint 训练时 `杯=5`，推理时却变成 `杯=9`，查出的就是另一个向量，模型接收到的语义入口被破坏。因此完整脚本先收集训练文本中的字符，再排序，以确定性方式分配 ID。真实项目还必须保存 tokenizer 文件、版本或 revision。

两个特殊 token 各有职责：

- `<PAD>`：把短序列补到 batch 的共同长度，本身不是指令内容；
- `<UNK>`：表示词表没有收录、但输入中真实出现的字符。

二者绝不能混为一个 ID。如果“绿”没见过，它仍占据一个真实序列位置，应被注意力看到为未知内容；padding 则应被 mask 排除。

### 3. 为什么 batch 需要 padding 和 mask

“拿杯”长度为 2，“把红杯放在蓝碗左边”更长。普通 tensor 每个维度必须是矩形，所以一批不同长度序列通常补到共同长度：

```text
token_ids = [真实 ID, 真实 ID, PAD, PAD]
valid_mask = [True,    True,    False, False]
```

ID 张量 shape 是 `[N,L]`：N 为 batch 大小，L 为统一序列长度。mask 与它同 shape，明确哪些位置有效。只靠“ID 是否为 0”临时猜也能用于简单场景，但显式传 mask 更清楚，并可适配不同 tokenizer 约定。

工程脚本对过长文本直接报错，而不是静默截断。静默截断机器人指令可能把“左边”截掉，使任务含义发生改变。真实模型通常有截断策略，但它必须被显式记录和测试。

### 4. `nn.Embedding` 本质是可学习查找表

若词表大小为 V、向量维度为 D，embedding 权重 shape 为 `[V,D]`。输入某个 ID，就取权重矩阵对应的一行：

```text
token_ids:       [N, L]
embedding table: [V, D]
output vectors:  [N, L, D]
```

它不是把整数当连续数做乘法，而是查表。训练时，损失梯度会更新被使用的行。`padding_idx=0` 让 PAD 对应的 token embedding 保持为零；本课在加入位置编码后又用 mask 把整个 PAD 位置清零，因为否则 PAD 虽没有 token 向量，仍会得到非零位置向量。

向量每个维度通常不能单独翻译成人类词语。我们关注的是向量经过训练后能否让下游任务有效区分、组合和预测，而不凭某个数值声称模型“理解”了对象关系。

### 5. 为什么还要位置

只做 token 查表时，“杯在碗左边”和“碗在杯左边”包含相似的 token 集合，但顺序改变了关系。embedding 表对同一个 token 总返回同一内容向量，本身没有序号。于是要加入位置表示：

```text
序列向量 = token embedding + position encoding
```

最小脚本使用可学习位置表；工程脚本实现 Transformer 原论文中的固定正弦/余弦位置编码。对位置 `pos` 和偶数维 `2i`：

```text
PE(pos, 2i)   = sin(pos / 10000^(2i/D))
PE(pos, 2i+1) = cos(pos / 10000^(2i/D))
```

位置 0 的偶数槽是 `sin(0)=0`，奇数槽是 `cos(0)=1`，测试会验证这一点。今天不要求推导为什么选择 10000；要掌握的是位置表 shape `[L,D]` 可广播到 `[N,L,D]`。

### 6. 与 VLA-RelComp 的关系

VLA 输入中的语言指令决定“拿什么”“放到哪个参照物的哪种关系位置”。在 `PrepositionCombinations` 中，词序、对象名和关系词都可能影响动作。后续诊断不能只说“语言有问题”，而要先确认：

- 使用的是模型配套 tokenizer 与 revision；
- 原始指令有没有被截断或意外改写；
- token IDs、attention mask 和 batch shape 是否正确；
- L0/L1/L2 的文本处理是否一致，是否发生数据泄漏。

本课没有运行任何真实 tokenizer 或 VLA 模型，所有数字只说明教学编码管线可运行。

## 二、今天做什么

### 步骤 0：从仓库根目录确认环境

```bash
cd "$(git rev-parse --show-toplevel)"
git branch --show-current
.venv-foundation_library/f06_environments_dependencies/bin/python -c "import torch; print(torch.__version__)"
```

若虚拟环境不存在，返回 Day 6 与 Day 9 按固定依赖创建；止损 10 分钟，不要在系统 Python 中反复混装。

### 步骤 1：运行最小 embedding

运行前先预测：文本有 4 个字符，embedding dim 为 4，最终 shape 是什么？

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f16_tokens_embeddings/code/minimal_embedding.py
```

预期关键输出：

```text
text: 拿起杯子
token ids: [[1, 2, 3, 4]]
token shape: (1, 4)
embedding shape: (1, 4, 4)
```

最后一行向量的具体值来自固定 seed 下的随机初始化，只是当前实测教学值，不代表自然语言含义。

### 步骤 2：运行工程版本

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f16_tokens_embeddings/code/sequence_lab.py
```

默认建立训练字符词表，再编码三条 fixture 评测指令。其中“绿”没有出现在建词表文本中，因此会映射为 `<UNK>`。预期看到：

```text
Token IDs shape: (3, 12)
Embedding shape: (3, 12, 8)
Padding vector L1: 0.0
```

查看保存内容：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m json.tool \
  learner_outputs/foundation_library/f16_tokens_embeddings/sequence_report.json | sed -n '1,100p'
```

检查所有 `sample_id` 均以 `fixture_` 开头，第三条文本的 `unknown_count` 为 1，padding 对应的 `valid_mask` 为 false。

### 步骤 3：运行测试和帮助入口

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m unittest foundation_library.f16_tokens_embeddings.tests.test_sequence_lab -v
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f16_tokens_embeddings/code/sequence_lab.py --help
```

应有 6 个测试通过。它们验证稳定词表、PAD/UNK 区分、拒绝静默截断、位置公式、padding 清零和同 seed 复现。

## 三、完整代码导读

最小版本完整保存在 [`code/minimal_embedding.py`](code/minimal_embedding.py)，按以下顺序读：手写词表 → 字符查 ID → `nn.Embedding` 查向量 → `arange` 生成位置 ID → 两种向量逐元素相加。它故意不处理未知字符和 padding，让第一遍数据流保持短小。

完整版本在 [`code/sequence_lab.py`](code/sequence_lab.py)，主要组件如下：

1. `CharacterVocabulary` 只从训练文本建表，以排序保证同样字符集合得到同样映射；
2. `encode` 返回等长的 ID 与 bool mask，过长就给可操作错误；
3. `encode_batch` 把多条样本变为 `[N,L]`，并生成稳定 `fixture_` ID；
4. `sinusoidal_positions` 明确实现公式；
5. `SequenceEncoder` 用 `register_buffer` 保存位置表，使它随模型迁移 device 和保存状态，但不接受优化器更新；
6. `run_experiment` 只输出可核查摘要，不把巨大 tensor 全塞进 JSON。

核心前向只有三步：

```python
positions = self.position_table[: token_ids.shape[1]].unsqueeze(0)
vectors = self.token_embedding(token_ids) + positions
return vectors.masked_fill(~valid_mask.unsqueeze(-1), 0.0)
```

`unsqueeze(0)` 让 `[L,D]` 位置表在 batch 维广播；`unsqueeze(-1)` 把 `[N,L]` mask 变成 `[N,L,1]`，从而同时清掉一个 PAD 位置的 D 个分量。

这里的位置表通过 `register_buffer` 进入 `state_dict`，但不是 `Parameter`。这与 Day 12 的知识衔接：参数会被训练，buffer 是模型状态但默认不求梯度。

## 四、动手实验

### 实验 A：embedding 维度改变哪个 shape

先预测 `--embedding-dim 16` 会改变 `[N,L]` 的哪一维，以及参数量是否增加。运行：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f16_tokens_embeddings/code/sequence_lab.py \
  --embedding-dim 16 \
  --output learner_outputs/foundation_library/f16_tokens_embeddings/dim16.json
```

预期 ID shape 仍为 `(3,12)`，embedding shape 变为 `(3,12,16)`。向量维度增加意味着 token 表参数增加，但不自动保证任务效果更好。本脚本没有训练下游任务，不能比较准确率。

再尝试奇数维：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f16_tokens_embeddings/code/sequence_lab.py --embedding-dim 7
echo $?
```

预期给出“必须为正偶数”并返回 2，因为本课正弦实现成对填入 sin/cos。

### 实验 B：最大长度过短

先数评测文本有几个字符，再预测 `max_length=3` 会发生什么：

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f16_tokens_embeddings/code/sequence_lab.py --max-length 3
echo $?
```

预期程序拒绝运行而不是截掉结尾，并返回 2。这说明数据契约优先于“程序勉强跑完”。真实 VLA 指令若被截断，必须在预处理阶段留下证据。

### 实验 C：PAD 位置为什么还要再清零

先预测：仅设置 `padding_idx=0`，在加位置编码以后 PAD 位置总向量是否仍为零？然后临时注释 `masked_fill`，让 `forward` 返回 `vectors`，再运行工程脚本。

预期 `Padding vector L1` 大于 0，因为位置向量仍存在。恢复清零行后应回到 0。该实验只说明本课选择“完全清零 PAD 表示”；Transformer 中还会把 mask 用到注意力分数上，Day 17 将实现它。

### 实验 D：未知字符不是 padding

在 `evaluation_texts` 第三条中把“绿”改为词表已见的“蓝”，运行并比较 JSON 的 `unknown_count`。先预测它从 1 变成多少。

预期变为 0，而该字符位置的 `valid_mask` 始终为 true。结果说明 UNK 表示有效但未知的输入，PAD 表示不存在的补位。完成后恢复源码。

## 五、检查点（含答案）

### 1. token、token ID、embedding 分别是什么？

**答案**：token 是 tokenizer 切出的符号；token ID 是词表给符号分配的离散整数地址；embedding 是用该 ID 从可学习表中取出的连续向量。

### 2. 为什么 `<UNK>` 不能与 `<PAD>` 共用同一个 ID？

**答案**：UNK 是输入中真实存在但词表未知的内容，应占有效位置；PAD 只是为矩形 batch 补位，应被 mask 排除。共用会让模型无法区分二者。

### 3. 输入 ID shape `[3,12]`、embedding dim 8，输出 shape 是什么？

**答案**：`[3,12,8]`。每个 batch 的每个序列位置都查得一个 8 维向量。

### 4. 为什么 token embedding 之外还要位置编码？

**答案**：同一个 token 的查表向量不携带它位于第几个位置；顺序会改变语言关系，所以要注入位置差异。否则后续注意力难以区分排列。

### 5. 本课第三条指令出现 `<UNK>` 能证明真实 VLA 不认识绿色吗？

**答案**：不能。未知只由本课手工建立的 fixture 字符词表造成，与真实模型 tokenizer、训练数据或视觉能力无关。

## 六、常见错误与止损

- **`IndexError: index out of range`**：检查 token ID 是否小于词表大小，tokenizer 与 embedding 是否配套；止损 15 分钟。
- **两个文本不能组成 tensor**：先 padding 到同一长度，再创建 tensor；止损 10 分钟。
- **mask shape 对不上**：同时打印 `token_ids.shape` 和 `valid_mask.shape`，二者应完全一致；止损 10 分钟。
- **embedding 维度为奇数时报错**：本课正弦实现要求偶数，恢复默认 8；止损 5 分钟。
- **文本过长**：先确认 max length 与真实 tokenizer 规则，不要未经记录直接删字；本课可增大 `--max-length`；止损 10 分钟。
- **中文显示乱码**：确认终端和 JSON 使用 UTF-8；不要把乱码当 tokenization 结果；止损 10 分钟。

## 七、精确外部材料

1. [PyTorch `nn.Embedding` 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.Embedding.html)：阅读 Parameters、Shape 和 `padding_idx` 示例；看完应能由 `[N,L]` 推出 `[N,L,D]`。暂时跳过 sparse optimizer 与 `max_norm`。
2. [PyTorch `register_buffer` 官方文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.register_buffer)：阅读该方法及 persistent 参数；看完应能解释位置表为何是状态但不是可训练参数。
3. [Attention Is All You Need 原论文](https://arxiv.org/abs/1706.03762)：阅读第 3.4 节 Embeddings and Softmax 与第 3.5 节 Positional Encoding；看完应知道 embedding 的缩放背景及正弦位置公式。今天跳过第 3.2 注意力推导，留给 Day 17。
4. [Hugging Face Tokenizers 文档：The tokenization pipeline](https://huggingface.co/docs/tokenizers/pipeline)：阅读 Normalization、Pre-tokenization、Model、Post-processing 四段；理解真实 tokenizer 不只是 `list(text)`。今天不安装库、不训练 BPE。
5. [Dive into Deep Learning 11.6 The Dataset for Pretraining Word Embeddings](https://d2l.ai/chapter_natural-language-processing-pretraining/word-embedding-dataset.html)：阅读 11.6.1 Subsampling 前的语料/词表准备部分；看完应区分 corpus、token 与 vocabulary。负采样内容暂时跳过。

## 今日收尾

在笔记里画出一条带 shape 的数据流：`字符串 → token 列表 → [N,L] IDs/mask → [N,L,D] vectors`；再写出 PAD 与 UNK 的区别，以及一条“fixture 编码不是 VLA 推理”的真实性声明。Day 17 将不再把序列位置彼此孤立，而是让每个位置通过查询、键和值读取其他有效位置。
