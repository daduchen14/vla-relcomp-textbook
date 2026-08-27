# Day 12：`nn.Module`、参数与前向传播

> 阶段 2 / Day 12 of 70　　建议用时：8—9 小时　　运行：PyTorch CPU

Day 11 用两个独立 tensor 表示 w/b。网络有成千上万参数时，不能靠手工列表管理。今天用 `nn.Module` 把层、参数和 forward 组织成一个可移动、可保存、可检查的模型，并验证 `state_dict` 保存—加载后预测逐元素完全相同。

checkpoint 只是 `fixture_` 小模型权重，不是 VLA 模型或研究成果。

## 1. 学完后你能做什么

1. 解释 `nn.Module` 的职责，以及 `__init__`/`forward` 分工；
2. 说明为何调用 `model(x)` 而不是直接 `model.forward(x)`；
3. 使用 `parameters()`、`named_parameters()` 和 `state_dict()`；
4. 区分参数、buffer 与普通 Python 属性；
5. 理解 `train()`/`eval()` 与 autograd 是否开启不是同一件事；
6. 只保存/加载 `state_dict`，理解 `strict`/`map_location`；
7. 验证 checkpoint round-trip，而不是只看文件存在。

## 2. 前置检查与产物

```bash
cd "$(git rev-parse --show-toplevel)"
.venv-day06/bin/python day11/code/train_linear_regression.py
.venv-day06/bin/python -c 'import torch; print(torch.__version__)'
```

今天生成代码、测试，以及个人目录中的训练 CSV、report JSON 和 `fixture_regressor_state.pt`。二进制 checkpoint 被 `learner_outputs` 忽略，不提交 Git。

开始前预测：把 `nn.Linear` 保存为局部变量而不赋给 `self`，`model.parameters()` 能否发现？`eval()` 是否等于 no_grad？

## 3. 今天学什么概念

### 3.1 Module 是可组合的模型容器

`nn.Module` 统一管理子模块、parameters、buffers、device/dtype 移动、训练模式与 state dict。最小结构：

```python
class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1)

    def forward(self, x):
        return self.linear(x)
```

`super().__init__()` 初始化注册机制，不能漏。把层赋给 `self.linear` 后，它成为子模块，其 weight/bias 自动注册。

### 3.2 forward 描述数据流

`forward` 说明输入怎样变输出，不负责读 CSV、解析 CLI 或保存日志。调用使用：

```python
y = model(x)
```

`Module.__call__` 会处理 hooks、编译/混合机制后再调用 forward；直接 `model.forward(x)` 会绕开这些框架行为。教学中也坚持 `model(x)`。

### 3.3 Linear 的 shape

`nn.Linear(in_features=1,out_features=1)` 对最后一维做：

```text
y = x W^T + b
```

输入 `(N,1)`，weight `(1,1)`，bias `(1,)`，输出 `(N,1)`。Linear 保留前面的 batch/额外轴，只要求最后一维等于 in_features。

Day 11 的 `(N,)` 与今天 `(N,1)` 都能描述一元数据，但接口语义不同。工程版主动拒绝一维输入，避免广播产生看似可用的错 shape。

### 3.4 参数注册

`nn.Parameter` 是默认 requires-grad 的特殊 tensor。`nn.Linear` 内部已创建 Parameter。查看：

```python
for name, parameter in model.named_parameters():
    print(name, parameter.shape)
```

得到 `linear.weight`、`linear.bias`。若把层放普通局部变量、未绑定到 self，Module 不会持续持有它；若把裸 tensor 赋给 self，它也不会自动变 Parameter（除非显式 `nn.Parameter`）。

参数注册让 optimizer、`.to(device)` 和 state_dict 找到同一组可训练状态。

### 3.5 parameter、buffer、普通属性

- parameter：训练更新并进入 state_dict；
- persistent buffer：不由 optimizer 学习，但属于模型状态，如某些 running stats，也进入 state_dict；
- 普通属性：配置/对象，不自动随 `.to` 移动或进入 state_dict。

需要保存且随设备移动的非训练 tensor 应 `register_buffer`。今天的 Linear 没有额外 buffer，先建立分类。

### 3.6 train/eval 与梯度开关

`model.train()`/`model.eval()` 改 `model.training` 并影响 Dropout、BatchNorm 等层。Linear 在两模式输出相同，但仍应形成习惯。

`eval()` 不关闭 autograd；`torch.inference_mode()`/`no_grad()` 才控制图记录。工程 `predict` 同时 eval + inference_mode：一个设层行为，一个省梯度开销。

### 3.7 state_dict 是什么

`state_dict()` 是从名称到 parameter/buffer tensor 的映射。本课键：

```text
linear.weight
linear.bias
```

它不包含 forward Python 代码/类定义/训练数据/超参数。加载时必须先构造相同架构，再 `load_state_dict`。

只保存整个 model 对象会依赖 Python pickle 与原类路径，迁移/安全性更差。课程优先保存 state dict，并另外保存配置、代码 commit 和模型 revision。

### 3.8 加载安全与来源

本课使用：

```python
torch.load(path, map_location="cpu", weights_only=True)
```

`weights_only=True` 缩小反序列化能力，`map_location=cpu` 防止文件设备假设。仍只加载可信来源；不要运行未知 checkpoint。哈希、来源、许可与 revision 会在模型章节记录。

### 3.9 strict 加载

`load_state_dict(state, strict=True)` 要求键与当前模型完全匹配。缺 key/多 key 通常意味着架构、命名或 checkpoint 不一致。初学时不要随手 strict=False 掩盖问题；只有明确做迁移学习并逐项解释 missing/unexpected keys 时才放宽。

### 3.10 文件存在不等于保存正确

round-trip 验证：训练模型预测→保存→新建同架构模型→加载→相同输入预测→逐元素比较。`torch.equal` true 证明本例预测位级相同；还应记录 state keys、版本、配置。大模型可能因设备/算法存在数值差异，需定义合适 tolerance。

## 4. 最小可运行代码

```bash
sed -n '1,180p' day12/code/minimal_module.py
.venv-day06/bin/python day12/code/minimal_module.py
```

预期打印模型结构、input/output `(3,1)`、`linear.weight (1,1)`、`linear.bias (1,)` 且 requires_grad true。初始化值随 seed/版本可不同，不把数值写死。

## 5. 完整代码与操作

完整代码在 [`code/module_lab.py`](code/module_lab.py)。按模型→数据→参数清单→训练→predict→save/load→artifacts 阅读：

```bash
sed -n '1,160p' day12/code/module_lab.py
sed -n '161,340p' day12/code/module_lab.py
.venv-day06/bin/python day12/code/module_lab.py --help
.venv-day06/bin/python day12/code/module_lab.py
echo $?
```

预期 final loss 接近 0，state keys 两项，checkpoint round trip true，退出码 0。

```bash
sed -n '1,220p' learner_outputs/day12/fixture_module_report.json
sed -n '1,12p' learner_outputs/day12/fixture_module_history.csv
ls -lh learner_outputs/day12/fixture_regressor_state.pt
```

文件大小只是本机现象；关键证据是重新加载预测匹配。报告在调用 `predict` 后采集 reloaded model 的 `training`，预期为 false；这里的字段也提醒我们模式是会被 `train()`/`eval()` 改变的状态。

## 6. 自动化测试

```bash
.venv-day06/bin/python -m unittest -v day12.tests.test_module_lab
.venv-day06/bin/python -m py_compile \
  day12/code/minimal_module.py \
  day12/code/module_lab.py \
  day12/tests/test_module_lab.py
```

4 项测试覆盖参数名、训练收敛、state round-trip 与错误 shape。临时 checkpoint 自动清理，不污染教材。

## 7. 动手实验

### 实验 A：改变 seed

分别 seed 7/8、epochs 0 不合法，因此用 epochs 1 观察初始与一轮后参数。先预测初值不同、最终长训练仍接近 2/1。seed 控制初始化，不决定真实关系。

### 实验 B：漏注册层

个人副本把 `self.linear` 改成局部 `linear`，并尝试 forward。预测属性不存在或参数清单为空。恢复 `self` 后重跑。

### 实验 C：eval 不等于 no_grad

构造 model，调用 eval，输入 requires_grad，前向后查看 output.requires_grad。预测仍 true；再放 inference_mode 变 false。说明两个开关职责。

### 实验 D：破坏 state key

个人脚本加载 state dict，删除 `linear.bias` 后 strict load。预测 missing key 错误。不要用 strict=False“修好”，先恢复完整 state。

### 实验 E：比较保存前后

用同一输入打印 before/after 最大差，预期 0。再创建未加载的新模型比较，通常非 0，说明“同架构”不等于“同参数”。

## 8. 常见错误与止损

| 现象 | 先检查 | 止损时间 |
|---|---|---:|
| parameters 为空 | 是否调用 super、层是否赋给 self | 20 分钟 |
| shape 错 | 最后一维是否等于 in_features | 15 分钟 |
| eval 后仍有 grad | eval 不关闭 autograd，用 inference/no_grad | 10 分钟 |
| missing/unexpected keys | 架构、键、strict、checkpoint revision | 20 分钟 |
| 加载设备错误 | map_location | 15 分钟 |
| 保存后预测不同 | 是否同配置、eval、相同输入、成功 load | 25 分钟 |
| 未知 checkpoint | 不加载，先核验来源/hash/许可 | 立即停止 |

不要提交真实大 checkpoint；仓库保存代码、配置和资产标识，权重使用获批来源与存储。

## 9. 与 VLA-RelComp 的连接

视觉编码器、语言模型、动作头都是 Module/子模块。冻结模块与可训练模块必须能从 named parameters 解释；checkpoint key 能映射到架构；推理必须 eval + inference mode 并记录 device/dtype。

最小修复阶段若只训练一个关系模块或 adapter，需要证明 optimizer 只收到目标参数，而不是意外解冻整个 VLA。今天的参数清单是未来审查训练范围的基础。

Day 13 将引入正式 optimizer、mini-batch、epoch 和 train/validation 对照，观察过拟合。

## 10. 检查点与答案

### 题 1

为何层要赋给 `self`？

**答案：** Module 才能注册并递归发现子层参数，使 parameters、to、state_dict、optimizer 正常工作。

### 题 2

eval 是否关闭梯度？

**答案：** 否。eval 改层模式；no_grad/inference_mode 控制计算图，通常推理两者同时用。

### 题 3

state_dict 包含 forward 代码吗？

**答案：** 不包含，主要是参数/buffer 映射；加载前需有匹配模型类/配置。

### 题 4

为何优先 weights_only 加载可信 state dict？

**答案：** 减少任意对象反序列化风险并使边界更清楚；未知来源仍不应加载。

### 题 5

checkpoint 文件存在能证明什么？

**答案：** 只证明路径有文件；需加载、检查 keys/config/version，并用固定输入验证预测。

## 11. 完成标准

**最低完成线：** 两个脚本和 4 测试通过；能找到两项参数并解释 forward/state_dict。

**标准完成线：** 完成 A—E；证明 round-trip，区分 eval/grad、parameter/buffer/属性；保存 CSV、JSON、fixture checkpoint 与笔记。

**当天产物：** 教材 Module、训练/保存加载程序和测试；个人训练历史、报告与小 checkpoint。

## 12. 精确外部材料

| 材料 | 精确范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [PyTorch Tutorials: Build the Neural Network](https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html) | Define Class、Model Layers、Parameters 三节，45 分钟 | Module/forward/parameters | GPU 示例只阅读 |
| [PyTorch `nn.Module`](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html) | 开头例子及 `train`/`eval`/`state_dict` 条目，30 分钟 | Module 核心 API | hooks/compile 高级项 |
| [PyTorch `nn.Linear`](https://docs.pytorch.org/docs/stable/generated/torch.nn.Linear.html) | Variables、Shape、Examples，20 分钟 | weight/bias shape | TF32/CUDA note |
| [PyTorch Saving and Loading Models](https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html) | Saving/Loading state_dict 与 inference 部分，35 分钟 | 正确 round-trip | 多模型 checkpoint 暂跳 |
| [PyTorch Serialization Semantics](https://docs.pytorch.org/docs/stable/notes/serialization.html) | state_dict 与 `weights_only=True` 两节，25 分钟 | 加载安全边界 | layout control |

只加载本课自己刚生成的 fixture checkpoint；不要从随机链接下载权重练习。
