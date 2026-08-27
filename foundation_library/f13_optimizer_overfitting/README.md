# Day 13：optimizer、mini-batch、epoch 与过拟合

> 阶段 2 / Day 13 of 70　　建议用时：8—9 小时　　运行：PyTorch CPU

Day 12 已把参数装进 Module，今天让 optimizer 统一更新它们，用 DataLoader 切 mini-batch，并把训练集与验证集分开。我们会看到一个重要现象：训练 loss 越来越低，验证 loss 却可能在某点之后上升。这不是程序必然坏了，而是模型开始记住稀疏带噪训练点——过拟合。

曲线来自固定 `fixture_` 正弦回归，只用于教学，不是 VLA 结果。

## 1. 学完后你能做什么

1. 区分 sample、batch、optimizer step 与 epoch；
2. 使用 TensorDataset/DataLoader 对齐并打乱样本；
3. 写出 `zero_grad→forward→loss→backward→step`；
4. 解释 SGD 与 Adam 的基本职责；
5. 正确计算样本加权 epoch loss；
6. 分离 train/validation，并用 validation 选择 best epoch；
7. 识别过拟合信号而不偷看测试集调参。

## 2. 前置检查与产物

```bash
cd "$(git rev-parse --show-toplevel)"
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f12_module_state_dict/code/module_lab.py
```

今天新增最小 optimizer 示例、完整 `overfitting_lab.py`、4 项测试。个人目录保存 learning curves CSV 和摘要 JSON。

先预测：16 个样本、batch size 4，每 epoch 有多少 optimizer steps？训练 3 epochs 累计多少？训练 loss 最低的 epoch 是否一定是验证最佳？

## 3. 今天学什么概念

### 3.1 Dataset 与 DataLoader

Dataset 定义第 i 个样本是什么；DataLoader 决定如何组成 batch、是否 shuffle、如何迭代。`TensorDataset(x,y)` 保证同一 index 的 x/y 配对。

```python
loader = DataLoader(dataset, batch_size=4, shuffle=True)
```

16 样本得到 4 batches；若 18 样本且不 drop_last，最后 batch 为 2。不要用“batch 数×固定 batch size”计算 epoch 样本平均，否则最后小 batch 权重错误。

### 3.2 batch、step 与 epoch

- sample：一条数据；
- batch：一次前向/反向使用的一组 sample；
- optimizer step：参数更新一次；
- epoch：训练集被遍历一轮。

本课 16/4=4 steps per epoch，3 epochs 累计 12 steps。真实 episode 数据若按随机行切 batch，可能把同一任务/轨迹泄漏到不同 split；后续会按 registry 规则划分。

### 3.3 shuffle 与 seed

shuffle 改变每 epoch 的 batch 组合，常帮助 SGD。工程版给 DataLoader 独立 generator/seed，使当前 CPU fixture 顺序可复跑。seed 仍不保证跨版本/硬件所有算法完全相同。

验证和测试通常不需 shuffle，因为不更新参数；但顺序不应影响正确聚合后的指标。

### 3.4 optimizer 封装更新规则

optimizer 持有要更新的 parameters 和内部状态。标准循环：

```python
optimizer.zero_grad()
loss = criterion(model(x), y)
loss.backward()
optimizer.step()
```

顺序不能乱：清除旧梯度，建立本 batch 图，反向累积当前梯度，再更新。`step()` 不会自动计算 loss/backward。

SGD 沿梯度更新，可加 momentum；Adam 为每个参数维护动量/尺度估计，常更容易起步，但并非永远泛化更好。今天最小例用 SGD，过拟合实验用 Adam，是为了教学观察，不构成模型选择结论。

### 3.5 train loss 怎样汇总

MSELoss 默认返回 batch mean。若最后 batch 较小，简单平均各 batch loss 会让小 batch 与大 batch同权。工程版累计：

```text
Σ(batch_loss × batch_size) / Σ(batch_size)
```

得到样本加权 epoch mean。真实多任务还需报告 task-level，而不是只用微平均掩盖困难任务。

### 3.6 train/validation/test

- train：更新参数；
- validation：选超参数、epoch/checkpoint；
- test：最终一次评估，不参与选择。

本课只有教学 train/validation。VLA-RelComp 中 L1/L2 是保留泛化测试，不能拿来挑 learning rate 或 best checkpoint。修复训练仅用 L0，并需从 L0 内再划分 validation。

### 3.7 评估模式

每 epoch 后：`model.eval()` + `inference_mode()` 计算 validation，不 backward/step。下一 epoch 前必须 `model.train()`。当前 MLP 没 Dropout/BatchNorm，模式不改变输出，但代码习惯必须正确。

### 3.8 过拟合

工程数据：16 个带噪训练点，121 个无噪 validation 点；64 隐层 MLP 容量较大。默认实测 best validation epoch 约 53，而到 399 时 train loss 很低、validation 更高。

过拟合信号不是“train loss 低”本身，而是 train 持续改善而 validation 相对最佳点恶化。本课定义最后 validation > best×1.05 作为教学 signal；阈值不是论文通用标准。

### 3.9 best epoch 与 early stopping

用 validation loss 最低点选择 best epoch，不能最后一轮自动当最好。真正 early stopping 还需保存当时 checkpoint、patience、最小改善量，并预先决定规则。今天只记录 best index，不在循环内提前停。

### 3.10 泛化边界

validation 与 train 来自相同 x 范围但噪声不同，观察的是本 fixture 的拟合泛化。它不是组合泛化，更不是 L0→L1/L2。课程后面会严格区分同分布 validation 与未见组合 test。

## 4. 最小可运行版本

```bash
sed -n '1,180p' foundation_library/f13_optimizer_overfitting/code/minimal_optimizer.py
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f13_optimizer_overfitting/code/minimal_optimizer.py
```

预期 4 batches/epoch，w≈2、b≈1。指出 optimizer 如何从 `model.parameters()` 获得注册参数。

## 5. 完整代码与运行

完整代码在 [`code/overfitting_lab.py`](code/overfitting_lab.py)。按 MLP→splits→loader→evaluate→train→summary 阅读：

```bash
sed -n '1,170p' foundation_library/f13_optimizer_overfitting/code/overfitting_lab.py
sed -n '171,340p' foundation_library/f13_optimizer_overfitting/code/overfitting_lab.py
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f13_optimizer_overfitting/code/overfitting_lab.py --help
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f13_optimizer_overfitting/code/overfitting_lab.py
echo $?
```

作者默认 CPU 实测：best epoch 53、best validation 约 0.0272，最后 train 约 0.0007、validation 约 0.0665、overfitting signal true。PyTorch 版本/平台变化可使数字改变；以自己的 CSV 为准，不照抄。

```bash
sed -n '1,15p' learner_outputs/foundation_library/f13_optimizer_overfitting/fixture_learning_curves.csv
sed -n '1,180p' learner_outputs/foundation_library/f13_optimizer_overfitting/fixture_overfitting_report.json
```

## 6. 自动化测试

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m unittest -v foundation_library.f13_optimizer_overfitting.tests.test_overfitting_lab
.venv-foundation_library/f06_environments_dependencies/bin/python -m py_compile \
  foundation_library/f13_optimizer_overfitting/code/minimal_optimizer.py \
  foundation_library/f13_optimizer_overfitting/code/overfitting_lab.py \
  foundation_library/f13_optimizer_overfitting/tests/test_overfitting_lab.py
```

4 测试覆盖 split shape、step count、评估模式和 best epoch 摘要逻辑。

## 7. 动手实验

### 实验 A：batch size

分别 batch=1/4/16、epochs=50。先预测每 epoch steps 为 16/4/1，再核对 report。比较曲线时同时记录总 optimizer steps，不能只比 epoch。

### 实验 B：小模型容量

hidden=4 与默认 64 各跑 400 epoch。预测小模型 train loss 较高但 validation 未必更差。记录 best/last，不只看最后。

### 实验 C：训练时长

epochs=40/400，其余固定。预测短训练可能尚未到 best，长训练可能过拟合。不要根据 validation 后再悄悄改测试集。

### 实验 D：学习率

lr=0.001 与 0.05，先预测收敛速度/稳定性。若出现非有限 loss，程序返回 2；保存命令和首次异常，不用最后一轮伪造曲线。

### 实验 E：手找 best epoch

写个人脚本读取 CSV，用 Python `min(rows,key=validation_loss)`，与 JSON 核对。再找最低 train epoch，解释两者为什么可能不同。

## 8. 常见错误与止损

| 现象 | 检查 | 止损时间 |
|---|---|---:|
| steps 数错误 | len(loader)、最后 batch、drop_last | 15 分钟 |
| validation 有梯度 | eval + inference/no_grad | 10 分钟 |
| 下一 epoch 仍 eval | train loop 开头 `model.train()` | 10 分钟 |
| epoch loss 偏差 | 是否按 batch size 加权 | 20 分钟 |
| 每次曲线不同 | 模型 seed 与 loader generator | 20 分钟 |
| train 降 val 升 | 先识别过拟合，不继续无限训练 | 20 分钟 |
| 用 test 选 best | 停止并重新定义无泄漏 split | 立即停止 |

## 9. 与 VLA-RelComp 的连接

未来 Dataset 会提供图像/state/instruction/action，DataLoader 产生 batch；optimizer 只能更新指定最小修复参数。L0 内 validation 选择 checkpoint，L1/L2 只做保留评测。

若反复查看 L1/L2 后调整 hidden size/epoch，它们就不再是干净 test。必须另留最终状态或明确 post hoc。过拟合不仅是 loss 曲线问题，也是研究协议问题。

Day 14 将系统学习 Dataset/DataLoader 的索引、batch 拼接、worker seed 与可复现随机性。

## 10. 检查点与答案

### 题 1

16 样本 batch 4、3 epochs 有多少 updates？

**答案：** 每 epoch 4 batches，共 12 optimizer steps。

### 题 2

optimizer.step 会自动 backward 吗？

**答案：** 不会；需先 forward/loss/backward，step 只按已有梯度更新。

### 题 3

为什么 batch loss 不能总做简单平均？

**答案：** 最后 batch 大小可能不同；应按样本数加权，除非 loss/协议另有定义。

### 题 4

训练 loss 继续降、validation 升意味着什么？

**答案：** 是过拟合信号：更贴训练数据但未改善验证泛化；仍需结合重复实验和曲线判断。

### 题 5

为什么 L1/L2 不能用来挑 best epoch？

**答案：** 它们是最终泛化测试；参与选择会泄漏测试信息并夸大效果。

## 11. 完成标准

**最低完成线：** 两脚本、4 测试通过；解释 batch/step/epoch/optimizer 顺序。

**标准完成线：** 完成 A—E；找到 best epoch、识别过拟合、按样本加权；保存 CSV/JSON 与对照笔记。

**当天产物：** 教材 optimizer/过拟合代码与测试；个人 curves、report 和五组实验。

## 12. 精确外部材料

| 材料 | 精确范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [PyTorch Optimization Tutorial](https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html) | Hyperparameters、Optimization Loop、Full Implementation，45 分钟 | 标准 train/test loop | classification accuracy 细节 |
| [PyTorch Data Tutorial](https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html) | Preparing data、Iterating through DataLoader，30 分钟 | Dataset/DataLoader 角色 | 自定义图片 Dataset 留 Day 14 |
| [PyTorch `Optimizer.zero_grad`](https://docs.pytorch.org/docs/stable/generated/torch.optim.Optimizer.zero_grad.html) | 描述与 set_to_none note，15 分钟 | 梯度清零语义 | 性能微调 |
| [D2L §4.4 Underfitting or Overfitting](https://d2l.ai/chapter_multilayer-perceptrons/underfit-overfit.html) | §4.4.1–4.4.4，40 分钟 | 模型容量、训练误差、泛化误差 | 高阶多项式代码可选 |

外部资料帮助理解通用循环；本课 fixture 数字只以实际 CSV 为证据。
