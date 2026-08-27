# Day 14：Dataset、DataLoader 与可复现随机性

> 阶段 2 / Day 14 of 70　　建议用时：8—9 小时　　实测：CPU、`num_workers=0/2`

Day 13 已用 DataLoader，但今天要打开黑盒：Dataset 的 index 返回什么，collate 怎样把样本拼成 batch，split 和 shuffle 各由哪个随机生成器控制，多 worker 为什么可能产生重复随机数据。最终保存一份带稳定 `fixture_` ID 的 loader manifest，让“这一轮到底按什么顺序看过哪些样本”可追踪。

作者已在当前 macOS/PyTorch 环境实测 `num_workers=0` 与 `2`，两者的 fixture 成员和顺序一致。不同 OS 的进程启动方式与日志顺序仍可能不同，学习者必须以自己的运行证据为准。

## 1. 学完后你能做什么

1. 实现 map-style Dataset 的 `__len__`/`__getitem__`；
2. 解释 index、稳定 sample ID 与数据来源的关系；
3. 理解默认 collate 与自定义 collate；
4. 用固定 generator 独立控制 split 和 shuffle；
5. 处理最后一个不足 batch；
6. 解释 `num_workers`、worker seed 与 persistent workers；
7. 验证 split 无重叠、同 seed 顺序一致，并保存 manifest。

## 2. 前置检查与今天产物

```bash
cd "$(git rev-parse --show-toplevel)"
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f13_optimizer_overfitting/code/minimal_optimizer.py
```

今天新增 `minimal_dataset.py`、`reproducible_loader.py` 和 4 项测试；个人输出为 `loader_manifest.json`。

先预测：10 个样本、batch 4、`drop_last=False` 的 batch sizes；同一个 seed 但复用已经迭代过的同一个 generator，第二轮顺序是否一定相同？

## 3. 今天学什么概念

### 3.1 Dataset 是“按索引取样”的契约

map-style Dataset 实现：

```python
def __len__(self): ...
def __getitem__(self,index): ...
```

`len` 给样本数，getitem 把 index 映射成一条样本。今天每条包含 stable `sample_id`、source index、feature、target。

真实项目 ID 不能只用“第 3 行”：CSV 重排会改变行号。应包含 task/episode/frame 等稳定来源。fixture 用 index 生成只是教学最小例。

### 3.2 一条样本与一个 batch

Dataset 返回 feature shape `(1,)`；collate 将 4 条 stack 成 `(4,1)`。字符串 ID 组成长度 4 的 list，index 组成 int64 tensor。

默认 collate 能处理常见字典/tensor，但自定义 collate 可做明确校验和 padding。工程版拒绝非 fixture ID 与 batch 内重复 ID，让错误在模型前暴露。

### 3.3 stack 与 concatenate

`torch.stack` 新增 batch 轴：四个 `(1,)`→`(4,1)`。`cat` 沿已有轴连接，可能得到 `(4,)`，丢失最后的 feature 轴语义。collate 的结果必须对齐模型输入契约。

可变长度文本/序列不能直接 stack，需 padding、mask 或 list。Day 20 会处理 token mask。

### 3.4 split 必须保存身份

`random_split` 返回原 Dataset 的 Subset，其中保存 indices。固定 generator 可复现一次划分：

```python
g=torch.Generator().manual_seed(7)
train,val=random_split(dataset,[9,3],generator=g)
```

仅保存 seed 仍不如保存实际 ID/indices 强，因为库版本或数据长度变化会改变结果。manifest 同时保存最终 sample IDs。

训练与 validation ID 必须无重叠并合计覆盖预期集合。真实轨迹数据还要避免同一 episode 的相邻 frame 跨 split；否则表面 ID 不同但信息泄漏。

### 3.5 shuffle 与 split 是两次随机操作

split 决定谁属于哪组；shuffle 只改变某组每轮读取顺序。应使用独立 generator，不依赖进程全局随机状态。工程版每次新建 loader 都用相同 seed，因此第一轮顺序一致。

若反复迭代同一个 loader，其 generator 状态前进，下一 epoch 通常得到新顺序。这是训练期所需；“同 seed”不是每 epoch 完全相同排列。

### 3.6 最后一个 batch

10/4→4、4、2。`drop_last=False` 保留 2；true 丢弃。BatchNorm、小数据或分布式时可能需要特殊策略，但丢弃会改变实际样本数，必须记录。

汇总 loss 时按实际 batch size 加权，不能假设每批都等大。

### 3.7 num_workers

`num_workers=0` 在主进程加载，最易调试；大于 0 创建 worker 并行准备数据。更多 worker 不一定更快，会受磁盘、CPU、序列化和平台影响。

macOS/Windows 常用 spawn，worker 重新导入模块，因此执行入口必须受 `if __name__ == '__main__'` 保护。数据对象也要可序列化。

### 3.8 worker 随机种子

PyTorch 给 worker 基础 seed，但 Dataset 内若还用 Python random/NumPy，应在 worker init 从 `torch.initial_seed()` 派生：

```python
worker_seed=torch.initial_seed()%2**32
numpy.random.seed(worker_seed)
random.seed(worker_seed)
```

否则 fork/spawn 状态可能导致重复或不可解释 augmentation。真实图像随机裁剪必须同时记录库版本与策略。

### 3.9 persistent workers

true 会在 epoch 间保留 worker，减少重启开销，也意味着 worker 内状态持续。工程版只在 num_workers>0 时开启。若 Dataset 持有可变缓存/随机状态，必须理解生命周期。

### 3.10 可复现不是只设 seed

还需要数据版本、split IDs、代码/torch 版本、sampler、batch size、drop_last、workers、随机变换、硬件/确定性算法。manifest 记录其中一部分，并明确不是完整实验复现证明。

## 4. 最小可运行版本

```bash
sed -n '1,180p' foundation_library/f14_dataloader/code/minimal_dataset.py
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f14_dataloader/code/minimal_dataset.py
```

预期 dataset length 5，三个 batches sizes 为 2、2、1；ID 按顺序。指出 sample 的 `(1,)` 如何变 batch `(2,1)`。

## 5. 完整代码与运行

完整代码在 [`code/reproducible_loader.py`](code/reproducible_loader.py)。按 Dataset→collate→worker seed→split→loader→manifest 阅读：

```bash
sed -n '1,170p' foundation_library/f14_dataloader/code/reproducible_loader.py
sed -n '171,340p' foundation_library/f14_dataloader/code/reproducible_loader.py
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f14_dataloader/code/reproducible_loader.py --help
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f14_dataloader/code/reproducible_loader.py
echo $?
```

默认 12 样本分 9 train/3 validation，train batches 4、4、1，validation 一批 3；overlap 空。顺序以实际输出为准。

```bash
sed -n '1,260p' learner_outputs/foundation_library/f14_dataloader/loader_manifest.json
```

确认每批 ID、source indices、feature/target shape，且 result type 是 synthetic loader order。

## 6. 自动化测试

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python -m unittest -v foundation_library.f14_dataloader.tests.test_reproducible_loader
.venv-foundation_library/f06_environments_dependencies/bin/python -m py_compile \
  foundation_library/f14_dataloader/code/minimal_dataset.py \
  foundation_library/f14_dataloader/code/reproducible_loader.py \
  foundation_library/f14_dataloader/tests/test_reproducible_loader.py
```

4 测试覆盖稳定 ID、split 无重叠/完整、同 seed 第一轮顺序相同、最后 batch 被保留。

## 7. 动手实验

### 实验 A：batch size

用 batch=5，先预测 train batches 5/4、validation 3。运行到独立输出文件并核对 shapes。

### 实验 B：改变 split seed

seed 7/8 分别运行。预测成员和 shuffle 都可能改变。比较 train/validation ID，说明为什么正式实验应保存实际 manifest。

### 实验 C：同 loader 两轮

个人脚本构造一个 train loader，连续 collect 两次。预测两轮 shuffle 顺序通常不同；再新建同 seed loader，第一轮恢复。解释 generator state。

### 实验 D：错误 validation count

sample 12、validation 12。预测退出码 2，不生成合法 split。该配置错误不能当训练 failure。

### 实验 E：多 worker 免费尝试

```bash
.venv-foundation_library/f06_environments_dependencies/bin/python foundation_library/f14_dataloader/code/reproducible_loader.py \
  --num-workers 2 \
  --output learner_outputs/foundation_library/f14_dataloader/loader_workers2.json
```

运行前预测 sample membership 不变；顺序应由 generator 控制。若平台报 spawn/序列化错误，最长排查 25 分钟并保存 stderr，默认 workers=0 已足够完成本课。不得把未成功路径写成实测通过。

## 8. 常见错误与止损

| 现象 | 检查 | 止损时间 |
|---|---|---:|
| batch shape 少一轴 | stack/cat 与单样本 shape | 20 分钟 |
| train/val 重叠 | 实际 ID 集合，不只看计数 | 15 分钟 |
| 每轮顺序不同 | shuffle 与 generator 状态 | 15 分钟 |
| worker 卡住 | 回到 workers=0，检查 main guard | 25 分钟 |
| 随机增强重复 | worker_init_fn 与 Python/NumPy seed | 25 分钟 |
| 最后 batch 变小 | drop_last/样本数余数 | 10 分钟 |
| 稳定 ID 随文件排序变 | 使用资源内 ID/manifest | 20 分钟 |

多进程只是性能手段，不是正确性前置；先让单 worker 数据契约完全正确。

## 9. 与 VLA-RelComp 的连接

VLA 数据样本可能按 episode/时间窗组织，含多相机图像、state、instruction、action chunk。split 必须按任务/level/episode 防泄漏，而不是随机 frame。collate 还需处理图像 resize、文本 padding、action mask。

L1/L2 不进入训练 loader；manifest 应能证明每个 sample 属于哪一 split。workers/augmentation 的随机性要与 seed、init state 等实验随机性分开记录。

Day 15 将把 batch 图像送入最小 CNN，观察卷积如何利用局部邻域与通道。

## 10. 检查点与答案

### 题 1

Dataset 与 DataLoader 分别负责什么？

**答案：** Dataset 定义按索引取一条样本；DataLoader 负责采样顺序、batch、collate 和 worker。

### 题 2

10 样本 batch 4、drop_last false 的 batch sizes？

**答案：** 4、4、2。

### 题 3

同 seed 为什么同一 loader 第二轮仍可不同？

**答案：** generator 是有状态的，第一轮消耗随机数；新 epoch继续状态产生新排列。

### 题 4

为何只保存 split seed 不够强？

**答案：** 数据长度、排序、库算法/版本变化都可能改变结果；应保存实际 sample IDs/indices。

### 题 5

为什么不能随机 frame 后宣称 episode split 无泄漏？

**答案：** 同一 episode 的相邻 frame 高度相关，跨 split 会让 validation/test 包含训练轨迹信息；应按 episode/任务分组。

## 11. 完成标准

**最低完成线：** 两脚本、4 测试与 workers=0 路径通过；解释 index/collate/split/shuffle。

**标准完成线：** 完成 A—E（多 worker 不适用时保留实际错误）；证明 ID 无重叠、顺序复现，保存 manifest 与笔记。

**当天产物：** 教材 Dataset/Loader、manifest 工具和测试；个人 manifest 与五项实验记录。

## 12. 精确外部材料

| 材料 | 精确范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [PyTorch Data Tutorial](https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html) | Dataset、DataLoader、Iterate 三节，45 分钟 | 自定义 Dataset 与 batch | 图片标注下载示例 |
| [PyTorch DataLoader docs](https://docs.pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader) | 构造参数、single/multi-process、randomness，45 分钟 | workers/generator/persistent | IterableDataset 分片细节 |
| [PyTorch Reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html) | Controlling sources 与 DataLoader 小节，25 分钟 | generator/worker_init_fn | CUDA deterministic 性能 |
| [PyTorch `random_split`](https://docs.pytorch.org/docs/stable/data.html#torch.utils.data.random_split) | 函数说明和 generator 示例，15 分钟 | 可复现划分 | fraction remainder 深挖 |

多 worker 行为以目标 OS/PyTorch 实测为准；当前作者环境已验证 workers=0 与 2，后续 Linux 仍须按课程命令重新验证。
