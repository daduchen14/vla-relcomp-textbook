# Day 10：导数、计算图与 autograd

> 阶段 2 / Day 10 of 70　　建议用时：8—9 小时　　运行：PyTorch CPU

Day 9 的 tensor 能保存数据并执行算术。神经网络学习还需要回答：参数稍微改变，loss 会朝哪个方向、变化多快？这个局部变化率就是梯度。今天用最小二次函数手算导数，再让 PyTorch 建计算图并反向传播，最后用有限差分作第三种独立核对。

所有数值均为 `fixture_` 教学例子，没有训练模型、GPU 或 VLA 实验结果。

## 1. 学完后你能做什么

1. 用斜率直觉解释导数和偏导数；
2. 对平方函数和均方误差手算梯度；
3. 解释 leaf tensor、`requires_grad`、计算图和 `grad_fn`；
4. 正确调用 `backward()` 并读取 `.grad`；
5. 说明梯度为何默认累积，以及何时清零；
6. 使用中心有限差分检查 autograd；
7. 区分 `.detach()`、`torch.no_grad()` 与“关闭学习”。

## 2. 前置检查与今天做什么

从仓库根目录开始：

```bash
cd "$(git rev-parse --show-toplevel)"
.venv-day06/bin/python day09/code/tensor_lab.py --device cpu
.venv-day06/bin/python -c 'import torch; print(torch.__version__)'
```

今天新增 `minimal_gradient.py`、完整 `autograd_lab.py` 和 4 项测试。个人输出位于 `learner_outputs/day10/gradient_report.json`。

开始前先预测：函数 `y=(x-1)^2` 在 x=3 的斜率是正还是负？如果连续两次对同一个 x 调 `backward()`，`.grad` 会覆盖还是相加？

## 3. 今天学什么概念

### 3.1 导数是局部变化率

汽车瞬时速度是位置对时间的变化率；loss 对参数的导数是“参数微小变化时 loss 怎样变化”。形式上：

```text
f'(x) = lim[h→0] (f(x+h)-f(x))/h
```

例如 `f(x)=(x-1)^2`，导数为 `2(x-1)`。x=3 时梯度 4，表示 x 向正方向增一点，f 会增大；若想减小 f，应往负梯度方向移动。x=1 时梯度 0，是这个函数的最小点。

梯度为 0 不总等于全局最优：也可能是局部极值、鞍点或饱和区域。今天只用凸二次函数建立基本直觉。

### 3.2 向量参数与偏导数

参数向量 `p=[p1,p2,...,pN]`，loss 是一个标量。梯度是每个偏导数组成的同 shape 向量：

```text
L = mean((p-t)^2)
∂L/∂pi = 2(pi-ti)/N
```

除以 N 来自 mean。若使用 sum，梯度没有 `/N`。loss reduction 是训练定义的一部分，不能只看函数名“均方误差”。

### 3.3 计算图

当输入 `requires_grad=True` 时，PyTorch 在前向运算中记录产生结果的操作关系。若：

```python
x = torch.tensor(3.0, requires_grad=True)
y = (x - 1) ** 2
```

x 是用户创建的 leaf tensor；y 是操作结果，带 `grad_fn`。`y.backward()` 从 y 沿图反向应用链式法则，把对 x 的梯度累积到 `x.grad`。

计算图不是教材画出来的静态网络图，而是运行时由实际 tensor 操作动态构建。Python 分支/循环可以影响本次图。

### 3.4 链式法则

把 `u=x-1`、`y=u^2`，则：

```text
dy/dx = dy/du × du/dx = 2u × 1 = 2(x-1)
```

神经网络只是把许多函数层层组合，autograd 反向逐局部导数相乘/相加。你不必手推大型网络全部梯度，但必须能对最小例子核对，否则出现 NaN、梯度为零或爆炸时无法判断。

### 3.5 标量 loss 与 backward

对标量 `loss.backward()`，PyTorch 隐含上游梯度 1。若输出是多元素 tensor，需要提供 `gradient` 参数或先 reduce 成标量。训练通常将每样本损失 mean/sum 成标量再反向。

读取 `.grad` 前确认它是 leaf 且 requires_grad。中间 tensor 默认不保留 `.grad`；可查看 grad_fn 来确认图存在，不应到处 `retain_grad()`。

### 3.6 梯度默认累积

PyTorch 的 `.backward()` 把新梯度加到现有 `.grad`。连续两次对 x² 在 x=3 反向：第一次 6，第二次累积为 12。训练循环每个 batch 通常在反向前执行：

```python
optimizer.zero_grad()
loss.backward()
optimizer.step()
```

累积并非错误，它可用于梯度累积；但若无意遗留，就会改变更新。今天用 `x.grad.zero_()` 看清这个状态。

### 3.7 detach 与 no_grad

`tensor.detach()` 返回与当前图断开的 tensor view，常用于记录/转 CPU/转 NumPy而不让日志操作进入图。工程代码将 loss、grad detach 后转 Python 数值。

`with torch.no_grad():` 在代码块内不记录梯度，适合推理或参数更新。它不等于模型永远不能训练，也不会自动调用 `model.eval()`；后者控制 dropout/batch norm 等训练模式，是另一个概念。

### 3.8 有限差分为什么是独立检查

中心差分：

```text
∂L/∂pi ≈ [L(p+εei)-L(p-εei)]/(2ε)
```

它只做前向数值计算，不依赖 autograd 的反向规则，因此可发现自定义算子或手推梯度错误。epsilon 不能无限小：太大会有截断误差，太小会被浮点舍入吞掉。

工程版用 float64、epsilon=1e-5，让简单二次函数误差小于 1e-8。这组阈值只适合本例，不是所有神经网络的万能标准。

### 3.9 float32 与 float64

训练常用 float32/更低精度提高速度和节省显存；数值梯度检查常用 float64 降低舍入误差。dtype 选择服务于任务：不能因为 gradient check 用 float64 就要求未来模型全程 double。

### 3.10 梯度不是因果解释

梯度说明当前函数局部敏感度，不自动解释模型为何做出某个行为，也不证明语言/视觉 grounding。VLA-RelComp 的行为诊断仍需匹配反事实、状态事件和 oracle；autograd 是训练最小修复的工具，不是研究结论本身。

## 4. 最小可运行版本

```bash
sed -n '1,160p' day10/code/minimal_gradient.py
.venv-day06/bin/python day10/code/minimal_gradient.py
```

预期：x=3、y=4、手算梯度和 autograd 都为 4、match true。逐行指出 detach 的用途，以及为何 y 必须是标量才可直接 backward。

## 5. 完整代码导读与运行

完整代码在 [`code/autograd_lab.py`](code/autograd_lab.py)。按 loss → 手算 → autograd → 有限差分 → 累积 → report 阅读：

```bash
sed -n '1,140p' day10/code/autograd_lab.py
sed -n '141,300p' day10/code/autograd_lab.py
.venv-day06/bin/python day10/code/autograd_lab.py --help
.venv-day06/bin/python day10/code/autograd_lab.py
echo $?
```

预期 loss 约 4.666667；手算最大误差接近 0，有限差分误差小于 1e-8，Passed true，退出码 0。具体科学计数尾数随版本可能略变。

查看：

```bash
sed -n '1,220p' learner_outputs/day10/gradient_report.json
```

三组梯度应逐元素接近；累积 demo 对首参数 3 显示 6、12、0。报告是合成梯度检查。

## 6. 自动化测试

```bash
.venv-day06/bin/python -m unittest -v day10.tests.test_autograd_lab
.venv-day06/bin/python -m py_compile \
  day10/code/minimal_gradient.py \
  day10/code/autograd_lab.py \
  day10/tests/test_autograd_lab.py
```

四项测试验证三种梯度一致、累积/清零、shape 错误和整数输入拒绝。预期全部 `ok`，语法检查无输出。

## 7. 动手实验

### 实验 A：改变 x

复制最小脚本到个人目录，把 x 从 3 改为 0。先预测 y 与梯度符号，再运行。预期 y=1、gradient=-2；要降低 loss，负梯度方向即向正移动。

### 实验 B：mean 改 sum

个人副本把 `quadratic_loss` 的 `.mean()` 改 `.sum()`，同时先不要改手算函数。预测检查是否通过、误差为何扩大。随后把手算公式去掉 `/N`，再验证一致。只修改个人副本。

### 实验 C：观察累积

把 `demonstrate_accumulation` 中第二次 backward 前加入 `x.grad.zero_()`。预测 second 值从 12 变 6。解释训练循环为何每 batch 清零。

### 实验 D：改变 epsilon

分别运行：

```bash
.venv-day06/bin/python day10/code/autograd_lab.py --epsilon 1e-2
.venv-day06/bin/python day10/code/autograd_lab.py --epsilon 1e-12
```

先预测误差。二次函数中心差分在较宽范围很准，但极小 epsilon 可能出现舍入误差。记录实际值，不强求与某台机器完全相同。

### 实验 E：严格容差失败

```bash
.venv-day06/bin/python day10/code/autograd_lab.py \
  --epsilon 1e-5 --tolerance 1e-15
echo $?
```

预期可能 Passed false、退出码 1，但报告正常写出；这是“梯度检查未通过”，不同于配置错误退出码 2。

## 8. 常见错误与止损

| 现象 | 先检查 | 止损时间 |
|---|---|---:|
| `.grad is None` | 是否 leaf、requires_grad、是否 backward | 20 分钟 |
| backward 报非标量 | 先 mean/sum 或明确上游梯度 | 15 分钟 |
| 第二轮梯度翻倍 | 是否忘记清零 | 10 分钟 |
| 原地操作报错 | 不直接改需梯度 leaf；查看报错位置 | 20 分钟 |
| 有限差分不准 | dtype、epsilon、loss 是否确定 | 25 分钟 |
| 出现 NaN/inf | 检查首次非有限中间量，不继续 step | 20 分钟 |
| 图被重复 backward 报错 | 默认图会释放；重新前向或理解 retain_graph | 20 分钟 |

不要用 `retain_graph=True` 掩盖训练循环设计错误；本课每次需要梯度都重新构建简单前向图。

## 9. 与 VLA-RelComp 的连接

行为克隆训练会比较预测 action 与示范 action 得到 loss，autograd 将梯度传回动作头、多模态融合与可训练参数，optimizer 再更新。L0-only 最小修复能否正确训练，首先依赖 loss、梯度清零、device/dtype 和数据 split 均正确。

梯度检查不能替代 L0/L1/L2 评测。训练 loss 下降只说明优化目标改善，不保证闭环 success 或组合泛化提高。课程以后始终分开保存训练指标与 evaluator 行为证据。

Day 11 会把今天的梯度用于最小线性回归：构造 fixture 数据、定义参数、循环更新并保存 loss 曲线数据。

## 10. 检查点与答案

### 题 1

均方误差用 mean 与 sum 时梯度为何不同？

**答案：** mean 多除以元素数 N，梯度为 `2(p-t)/N`；sum 为 `2(p-t)`。reduction 是目标定义的一部分。

### 题 2

为什么梯度默认累积？

**答案：** 多条计算路径或多个小 batch 的贡献可以相加；但普通训练每轮通常需显式清零，避免混入上一轮。

### 题 3

有限差分 epsilon 越小越好吗？

**答案：** 不是。过大有截断误差，过小会受浮点舍入/消减影响，需要与 dtype、函数尺度一起选择。

### 题 4

detach 和 no_grad 有何区别？

**答案：** detach 针对 tensor，返回从当前图断开的表示；no_grad 是上下文，块内运算不构建梯度图。二者都不等于 `model.eval()`。

### 题 5

训练梯度正常能否证明模型理解空间关系？

**答案：** 不能。梯度只证明优化链路的局部数学行为；研究推断需要闭环行为、受控对照与状态事件。

## 11. 完成标准

**最低完成线：** 最小/完整代码和 4 项测试通过；能手算二次函数与 MSE 梯度；解释累积。

**标准完成线：** 完成 A—E；能用三种方法核对梯度、解释 epsilon/dtype/退出码；保存报告和个人推导。

**当天产物：** 教材的标量示例、梯度检查器和测试；个人目录中的 JSON、公式推导与五项实验记录。

## 12. 精确外部材料

| 材料 | 精确范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [PyTorch Tutorials: Automatic Differentiation](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html) | Tensors/Functions/Computational Graph/DAGs 三段，45 分钟 | requires_grad、grad_fn、backward | Jacobian product 复杂例子 |
| [PyTorch `Tensor.backward`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.backward.html) | Parameters 与梯度累积 note，20 分钟 | 标量/非标量与累积 | create_graph 高阶导数 |
| [PyTorch Autograd mechanics](https://docs.pytorch.org/docs/stable/notes/autograd.html) | How autograd encodes history 与 Locally disabling gradient computation，35 分钟 | 图、no_grad、detach | complex autograd 与并发 |
| [D2L §2.5 Automatic Differentiation](https://d2l.ai/chapter_preliminaries/autograd.html) | §2.5.1–2.5.3，35 分钟 | 动手计算、清零、非标量 backward | 控制流选读 |

先手算本课公式，再读 autograd；不要用框架输出替代纸面推导。
