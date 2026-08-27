# Day 9：Tensor、shape、dtype 与 device

> 阶段 2 / Day 9 of 70　　建议用时：8—9 小时　　实测环境：PyTorch 2.13.0、macOS arm64、CPU

Day 7 用 NumPy 表示图像、state 和 action，Day 8 用这些概念建立 evaluator。今天把相同数据迁移到 PyTorch tensor。Tensor 看起来像 ndarray，但它还携带 device、梯度关系和深度学习算子，是后续网络训练、视觉编码与 VLA 推理的数据底座。

作者已在被 Git 忽略的本地虚拟环境免费安装并实测 `torch 2.13.0`。本课所有结论以 CPU 运行证明；没有运行 CUDA、付费 GPU、模型权重或 VLA-Arena。MPS/CUDA 只讲设备选择规则，不把未运行现象写成实测。

## 1. 学完后你能做什么

1. 区分 scalar、vector、matrix、tensor 与 batch；
2. 读取 tensor 的 shape、dtype、device、numel 和 requires_grad；
3. 从 NumPy/列表构造 tensor，理解复制或共享内存的边界；
4. 将 HWC/NHWC 图像转成 CHW/NCHW 并保持语义；
5. 使用 `.to(device/dtype)`，避免设备或类型不一致；
6. 估算 tensor 存储字节数；
7. 在设备不可用时明确失败，不静默伪装成 GPU 运行。

## 2. 环境准备与今天做什么

从仓库根目录开始：

```bash
cd "$(git rev-parse --show-toplevel)"
.venv-day06/bin/python -m pip --version
.venv-day06/bin/python -c 'import torch; print(torch.__version__, torch.__file__)'
```

若还没有 torch，按照官方“Start Locally”页面为自己的 OS 选择 Pip/Python/CPU 命令。macOS 当前可在课程虚拟环境执行：

```bash
.venv-day06/bin/python -m pip install torch
```

安装是免费的但会下载较大 wheel；先用 Day 5 快照确认空间。不要使用 `sudo pip`，不要为 CUDA 随意安装非本机 wheel。教程作者本次下载 torch wheel 约 111 MB，实际大小随版本/平台变化。

今天新增最小 tensor 脚本、完整 `tensor_lab.py`、4 项 CPU 测试和个人 JSON 报告。运行命令统一使用 `.venv-day06/bin/python`，避免系统 Python 找不到 torch。

本课实际验证的直接依赖锁在 [`config/requirements-cpu.txt`](config/requirements-cpu.txt)。它只描述当前 macOS arm64/Python 3.14 教学 CPU 环境，不冒充后续 Linux/CUDA/VLA-Arena 的依赖锁。全新同平台环境可执行：

```bash
.venv-day06/bin/python -m pip install -r day09/config/requirements-cpu.txt
```

## 3. 今天学什么概念

### 3.1 Tensor 是带规则的多维数值网格

零维 tensor 是 scalar，一维可表示 vector，二维可表示 matrix，更高维统称 tensor。名称“维”容易混淆：七维 action 通常是 shape `(7,)` 的一维 tensor，表示有七个分量；它不是七个轴的 7-D tensor。

```python
scalar = torch.tensor(3.0)          # shape ()
vector = torch.tensor([1.0, 2.0])   # shape (2,)
matrix = torch.zeros(2, 3)          # shape (2,3)
```

`ndim` 是轴数，`shape` 是每轴长度，`numel()` 是总元素。对 shape `(2,3,4)`，numel=24。

### 3.2 shape 是接口契约

Day 7 图像是 HWC；工程版先构造 batch NHWC `(N,H,W,C)`，再：

```python
images_nchw = images_nhwc.permute(0, 3, 1, 2)
```

变为 `(N,C,H,W)`。`permute` 参数不是目标 shape，而是“旧轴按什么顺序排列”：旧轴 0 保持 batch，旧轴 3 移到通道，旧轴 1/2 是高宽。

同样 shape 不保证同样含义。`(2,3,4,3)` 必须记录为 NHWC，不能只写四个数字。后续模型通常期望 NCHW 或 processor 定义的格式。

### 3.3 dtype 决定表示与算术

原始像素常用 `torch.uint8`；网络输入、state、action 常用 `torch.float32`。归一化：

```python
image_float = image_uint8.to(torch.float32) / 255.0
```

不能只写 `.to(torch.float32)` 就宣称完成预处理：模型可能还要求均值/标准差、resize、颜色通道和范围。今天只完成 `[0,255]→[0,1]` 的教学转换。

默认 dtype 也有陷阱：`torch.tensor([1.0])` 通常为 float32，而 `torch.tensor([1])` 为 int64。整数 tensor 与浮点参数相乘可能触发类型提升或算子限制。关键接口显式指定 dtype。

### 3.4 device 是数据实际所在的计算设备

常见：

- `cpu`：通用处理器；本课实测基线；
- `cuda`：NVIDIA GPU，需要相容驱动、CUDA 构建与硬件；当前未运行；
- `mps`：Apple Metal 后端；本课不把其可用性等同于所有算子适配。

tensor 与模型参数通常必须位于兼容 device。CPU tensor 不能直接与 CUDA 参数计算。移动：

```python
x = x.to("cpu")
```

`.to` 通常返回新引用；若 dtype/device 已满足，可能返回自身。写 `x.to(...)` 而不接返回值，不能假设原变量改变。

工程代码要求显式 `--device cpu|mps|cuda`。请求不可用 CUDA 时返回 2，而不是悄悄改成 CPU后仍宣称“GPU 实验完成”。

### 3.5 device available 不等于完整工作负载可用

`torch.cuda.is_available()` 或 `torch.backends.mps.is_available()` 只回答后端基础可用性。真实模型还取决于算子支持、dtype、显存、驱动与依赖。必须用目标代码做 smoke test并记录实际 device。

当前作者环境只把 CPU 路径纳入真实性证明。任何 MPS/CUDA 命令的预期都属于教学说明，不能作为跑过的证据。

### 3.6 batch 轴

单张 HWC image shape `(H,W,3)`；两张组成 NHWC batch `(2,H,W,3)`。state 从 `(4,)` 扩为 `(N,4)`，action 从 `(7,)` 扩为 `(N,7)`。同一 batch 的第一轴必须一致。

batch 让硬件并行处理多个样本，也会增加内存。它不改变“一个 episode 有多少 step”；batch 轴、时间轴和相机轴必须分开命名。

### 3.7 stride、view 与 contiguous

Tensor 用 storage 存数据，shape/stride 解释如何沿轴访问。`permute` 常只改变视图和 stride，不重排 storage，因此结果可能 `is_contiguous=False`。一些操作需要连续布局，本课显式：

```python
x = x.permute(...).contiguous()
```

这可能复制数据。不要无脑对所有 tensor 调 contiguous；先理解下游要求。今天记录该属性是为了让“布局”成为可见证据。

### 3.8 存储估算

粗略数据字节数：

```text
numel × element_size
```

float32 每元素 4 字节，uint8 每元素 1 字节。shape `(2,3,224,224)` float32 约 1.2 MB（不含 allocator、梯度和中间激活）。训练内存远大于输入 tensor，因为还包含参数、梯度、优化器状态和 activations。

### 3.9 requires_grad 先认识、不深挖

`requires_grad=True` 表示 PyTorch 应追踪相关运算以便自动微分。今天数据 tensors 默认 false，只读取属性。Day 10 会用标量函数亲手比较手算导数与 autograd；今天不要在图像预处理上提前堆梯度概念。

## 4. 先运行约 25 行最小版本

```bash
sed -n '1,160p' day09/code/minimal_tensors.py
.venv-day06/bin/python day09/code/minimal_tensors.py
```

预期结构：

```text
image (2, 2, 3) torch.uint8 cpu
state (4,) torch.float32 cpu
action (7,) torch.float32 cpu
normalized_range 0.0 1.0
```

指出 `device=cpu` 是实际属性，不是代码注释；指出七维 action 的 ndim 仍是 1。

## 5. 工程版导读与运行

完整代码在 [`code/tensor_lab.py`](code/tensor_lab.py)。按设备选择 → fixture batch → 契约校验 → NHWC/NCHW 转换 → summary 阅读：

```bash
sed -n '1,140p' day09/code/tensor_lab.py
sed -n '141,300p' day09/code/tensor_lab.py
.venv-day06/bin/python day09/code/tensor_lab.py --help
.venv-day06/bin/python day09/code/tensor_lab.py --device cpu --batch-size 2
echo $?
```

预期：PyTorch 版本以本机为准，device cpu；images 从 `(2,3,4,3) uint8` 变为 `(2,3,3,4) float32`。查看报告：

```bash
sed -n '1,240p' learner_outputs/day09/tensor_report.json
```

确认每项有 shape/dtype/device/requires_grad/contiguous/numel/bytes/range。报告是合成 tensor 元数据，不是训练或模型结果。

验证不可用设备失败路径：

```bash
.venv-day06/bin/python day09/code/tensor_lab.py --device cuda
echo $?
```

当前无 CUDA 环境预期返回 2，明确提示不可用，不生成伪造 CUDA 报告。若未来机器真有 CUDA，该命令可能正常；届时以实测为准。

## 6. 自动化测试

```bash
.venv-day06/bin/python -m unittest -v day09.tests.test_tensor_lab
.venv-day06/bin/python -m py_compile \
  day09/code/minimal_tensors.py \
  day09/code/tensor_lab.py \
  day09/tests/test_tensor_lab.py
```

4 项测试覆盖 CPU batch shape、NCHW/dtype/range、非法 batch size、无 CUDA 时拒绝路径。若当前有 CUDA，最后一项会 skip 而不是谎称拒绝；其余仍应通过。

## 7. 动手实验

### 实验 A：改变 batch size

先预测 batch=5 时 images/states/actions shape 与 images numel，再运行：

```bash
.venv-day06/bin/python day09/code/tensor_lab.py --batch-size 5
```

预期 `(5,3,4,3)`、`(5,4)`、`(5,7)`，images numel=180。batch 变化不增加单张图像分辨率。

### 实验 B：计算存储变化

比较报告中原 uint8 NHWC 与 float32 NCHW 的 `storage_bytes`。先预测 float32 是原来的几倍。元素数相同，float32 每元素 4 字节，所以约 4 倍；轴转换本身不改变 numel。

### 实验 C：观察 non-contiguous

在个人副本临时去掉 `.contiguous()`，打印 `is_contiguous()`。预测 permute 后为 false；再恢复 contiguous 为 true。不要把这个现象泛化为“所有 permute 永远不连续”，应看具体 stride。

### 实验 D：`.to` 返回值

```python
x = torch.tensor([1, 2], dtype=torch.int64)
x.to(torch.float32)
print(x.dtype)
y = x.to(torch.float32)
print(y.dtype)
```

先预测两行。预期 x 仍 int64，y 是 float32。说明为什么工程代码接住返回值。

### 实验 E：制造 batch 轴不一致

在个人测试构造 batch 后，把 states 换成 shape `(1,4)` 而 images batch=2，调用 validate。预测错误信息。恢复后重跑全部测试。

## 8. 常见错误与止损

| 现象 | 先检查与处理 | 止损时间 |
|---|---|---:|
| system Python 找不到 torch | 使用 `.venv-day06/bin/python` 并打印 executable | 15 分钟 |
| `pip` 装了仍 import 失败 | 对比 pip 与 Python 路径 | 20 分钟 |
| device mismatch | 打印每个输入与参数 `.device` | 15 分钟 |
| dtype mismatch | 打印 dtype；不要盲目全部 `.float()` | 15 分钟 |
| permute 后 view/reshape 报错 | 查看 contiguous/stride，按需求 contiguous | 20 分钟 |
| CUDA 不可用 | 当前回到 CPU 教学路径，不安装随机 CUDA 包 | 15 分钟 |
| 内存增长 | 手算 numel×element_size，缩小 batch/shape | 立即停止扩大 |

不因 MPS/CUDA 暂不可用暂停课程；CPU 足以完成 Day 9–18 的最小概念代码。后续真实模型 GPU 运行会单独获批。

## 9. 与 VLA-RelComp 的连接

未来 VLA batch 可能包含 `pixel_values (N,C,H,W)`、state `(N,D)`、token IDs `(N,L)` 和动作目标 `(N,T,7)`。任何一处 batch/time/channel 轴错位都可能产生“形状能广播但语义错”的隐蔽故障。

device 记录也是实验字段：不能在 CPU smoke test 后写“GPU 已验证”，也不能因为 MPS 可用就推断 NVIDIA/CUDA 环境正确。模型 revision、torch 版本、device 类型和 dtype 必须一起记录。

Day 10 会让一个 `requires_grad=True` 标量经过计算图，用 `.backward()` 得到梯度，并与手算导数核对。

## 10. 检查点与答案

### 题 1

“七维动作”为什么通常不是七阶 tensor？

**答案：** 七维指七个动作分量，tensor shape 通常 `(7,)`，只有一个轴；阶/ndim 是轴数。

### 题 2

`.to(torch.float32)` 为什么要接返回值？

**答案：** `.to` 返回转换后的 tensor，原 tensor 不保证原地改变；不接返回值可能继续使用旧 dtype/device。

### 题 3

CUDA available 能否证明 VLA 模型可运行？

**答案：** 不能，只是基础后端检测。还需模型、显存、算子、dtype、驱动和完整目标路径 smoke test。

### 题 4

NHWC→NCHW 是否改变元素数？

**答案：** 不改变，只重排轴解释；numel 相同。转 float32 会改变每元素字节数。

### 题 5

为什么 device 不可用时不静默回 CPU？

**答案：** 静默回退会让记录声称的运行设备与事实不符，掩盖性能/兼容性问题。应明确失败，由调用者选择 CPU。

## 11. 完成标准

**最低完成线：** torch 可在隔离环境导入；两个脚本和 4 项 CPU 测试通过；能解释 shape/dtype/device。

**标准完成线：** 完成 A—E；手算 numel/bytes，解释 NCHW、contiguous 和 `.to`；保存 tensor report 与个人对照笔记。

**当天产物：** 教材中的最小 tensor 脚本、工程 tensor lab 与测试；个人目录中的 JSON 报告和五项实验记录。

## 12. 精确外部材料

| 材料 | 精确范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [PyTorch Start Locally](https://pytorch.org/get-started/locally/) | 只选自己的 OS、Pip、Python、CPU；阅读验证代码，20 分钟 | 正确安装/验证当前平台 | CUDA/ROCm 命令 |
| [PyTorch Tutorials: Tensors](https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html) | Initializing、Attributes、Operations 三节，45 分钟 | 构造并读取 shape/dtype/device | Bridge with NumPy 留作选读 |
| [PyTorch Tensor Attributes](https://docs.pytorch.org/docs/stable/tensor_attributes.html) | `torch.dtype` 与 `torch.device` 开头说明，25 分钟 | 正式理解 dtype/device | layout 与 memory format 深挖 |
| [PyTorch `Tensor.to`](https://docs.pytorch.org/docs/stable/generated/torch.Tensor.to.html) | Parameters、Returns、三个 examples，15 分钟 | 正确接收 device/dtype 转换 | non_blocking 性能优化 |
| [PyTorch `permute`](https://docs.pytorch.org/docs/stable/generated/torch.permute.html) | 函数说明与例子，10 分钟 | 轴重排参数语义 | 稀疏 tensor |

外部材料的版本页面会更新；实际报告以本机 `torch.__version__` 为准。今天不下载模型或 CUDA 资产。
