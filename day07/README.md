# Day 7：NumPy、数组、图像和机器人状态

> 阶段 1 / Day 7 of 70　　建议用时：8—9 小时　　依赖：NumPy 2.x（本机已免费实测）

Day 6 建立了 Python 环境边界。今天第一次引入第三方数值库 NumPy，把“许多数字”组织成有 shape、dtype 和轴语义的数组。VLA 的图像、机器人状态和动作最终都会变成这类规则数值容器；如果轴顺序或类型错了，程序可能仍能运行，却把红色当蓝色、把 batch 当时间或让动作尺度失控。

今天只生成 `fixture_` 合成数组，不读取相机、不连接机器人、不运行模型。动作数值没有物理设备含义，任何输出都不是 VLA 实验结果。

## 1. 学完后你能做什么

1. 区分 Python 列表与 NumPy ndarray；
2. 解释 shape、ndim、size、dtype 和 axis；
3. 用 `(H, W, C)` 表示 RGB 图像，用一维向量表示 state/action；
4. 理解索引、切片、广播、复制与 view 的基本风险；
5. 把 `uint8 [0,255]` 图像正确转换为 `float32 [0,1]`；
6. 校验七维动作的 shape、dtype 与有限性；
7. 用 NPZ 保存精确数组、用 JSON 保存小型可读摘要。

## 2. 前置检查与安装边界

从仓库根目录开始：

```bash
cd "$(git rev-parse --show-toplevel)"
python3 day06/code/environment_doctor.py
python3 -c 'import numpy as np; print(np.__version__, np.__file__)'
```

若最后一条成功，不要重复安装。本教材作者环境实测为 NumPy 2.4.2，但你的版本可以不同。若报 `ModuleNotFoundError`，在 Day 6 虚拟环境中免费安装并始终用同一解释器：

```bash
.venv-day06/bin/python -m pip install 'numpy>=2.0,<3'
.venv-day06/bin/python -c 'import numpy as np; print(np.__version__)'
```

这会访问 PyPI，但不需要付费。网络失败时最长排查 20 分钟；可先阅读正文，不要使用 `sudo pip` 或随机镜像。后续命令中的 `python3` 应替换成成功导入 NumPy 的准确解释器。

今天代码位于 `day07/code/`，个人输出是 `learner_outputs/day07/fixture_arrays.npz` 和 `array_summary.json`。

## 3. 今天学什么概念

### 3.1 为什么列表还不够

Python 列表可以同时装字符串、整数和另一个列表，灵活但不自动保证矩形形状或统一数值类型。NumPy ndarray 通常把同一 dtype 的元素放在规则多维网格中，可进行批量计算。

```python
python_list = [1, 2, 3]
array = np.array([1, 2, 3], dtype=np.float32)
```

`python_list * 2` 会重复列表，得到六个元素；`array * 2` 对每个元素做数值乘法。两者语法相似、语义不同，所以先确认对象类型。

### 3.2 shape、ndim、size 与 dtype

假设图像 shape 为 `(4, 6, 3)`：4 是高度 H，6 是宽度 W，3 是通道 C。`ndim=3` 表示有三个轴，`size=72` 是总元素数。shape 不是“数据量的装饰”，而是每个轴的语义契约。

常见 dtype：

- `uint8`：0–255 无符号整数，常用于存储 RGB 像素；
- `float32`：深度学习最常见浮点类型之一；
- `float64`：NumPy 某些构造默认值，精度更高但占用更多；
- `bool`：真假 mask。

`uint8` 的最大值是 255，再加 1 若按 uint8 计算可能回绕；浮点除法前要显式 `astype(np.float32)`。真实模型还可能要求减均值、除标准差，而非只除 255；必须遵守对应 processor 的官方契约。

### 3.3 轴顺序必须写清

常见图像布局有 HWC 与 CHW：

```text
HWC: (height, width, channels)   NumPy/图像读取中常见
CHW: (channels, height, width)   PyTorch 单张图像中常见
NCHW: (batch, channels, height, width)
```

shape `(3, 224, 224)` 不能仅凭数字判断是 CHW 图像还是三帧灰度图，必须结合接口定义。转换 HWC→CHW 可用 `np.transpose(image, (2, 0, 1))`；这只改变轴顺序，不改变颜色值。

VLA observation 可能含一个或多个相机图像、proprioceptive state 和语言。不能把它们未经说明地拼成一条长列表；每个字段需有 shape、dtype、范围和坐标/时间语义。

### 3.4 索引和切片

对 HWC 图像：

```python
pixel = image[0, 0]       # shape (3,)，左上像素的 RGB
red_channel = image[:, :, 0]  # shape (H, W)
crop = image[1:3, 2:5, :]     # 高度/宽度切片，保留通道
```

索引从 0 开始，切片右端不包含。`image[0, 0, 0]` 是单个标量。调试时逐轴说出含义，比盯着大数组更有效。

NumPy 切片经常是原数组的 view，修改切片可能修改原数组：

```python
crop = image[:2, :2]
crop[:] = 0
```

若需要独立副本，用 `.copy()`。今天不要求背所有内存规则，但修改前应问“这是 view 还是 copy”。

### 3.5 广播：不用手写每个像素

本课生成绿通道：

```python
image[:, :, 1] = np.linspace(0, 255, height, dtype=np.uint8)[:, None]
```

右侧原 shape 为 `(H,)`，`[:, None]` 变成 `(H,1)`。赋给 `(H,W)` 区域时，NumPy 沿宽度复制每行值，这叫 broadcasting。它不一定真的复制内存，而是按兼容规则扩展计算。

广播强大也危险：错误 shape 恰好兼容时不会报错，却可能沿错误轴计算。因此任何关键变换后立即打印/断言 shape。

### 3.6 state 与 action 是有语义的向量

本课 state shape `(4,)`，可类比 x、y、z、夹爪状态；这只是教学约定。action shape `(7,)`，课程暂将前三维称为平移 delta、后三维旋转 delta、最后一维夹爪命令。真实 VLA-Arena/模型接口的顺序、坐标系、范围和 gripper 约定必须以后从锁定上游代码核验，不能用本课类比替代。

工程脚本的 `action_scale` 只缩放前六个运动分量，不缩放 gripper。这样修改一个控制变量时能预测：scale=2 后第一个分量从 0.01 变 0.02，最后一维仍为 1.0。

### 3.7 NaN 与 infinity

浮点数组可能出现 `NaN` 或正负 infinity。它们会沿计算传播，让损失和动作失效。`np.isfinite(array)` 对每项判断，再用 `np.all` 确认全部有限：

```python
if not np.all(np.isfinite(state)):
    raise ArrayContractError(...)
```

不要把 NaN 自动替换成 0 后继续真实实验，因为这会隐藏上游错误。先记录来源并使该 episode 标成基础设施异常。

### 3.8 保存数组与摘要

JSON 可读但不天然保留 NumPy dtype；把数组 `.tolist()` 后类型/体积信息会弱化。`.npz` 能在一个压缩文件保存多个 NumPy 数组，适合今天的小型 fixture。真实大规模观测不会随意提交 Git，而是保存索引、格式、版本和校验信息。

本课 NPZ 保存 image、normalized_image、state、action；JSON 只保存 shape、dtype、范围和小动作列表。二者都有不同用途。

## 4. 先运行 25 行最小版本

```bash
sed -n '1,160p' day07/code/minimal_arrays.py
python3 day07/code/minimal_arrays.py
```

预期：

```text
image (2, 3, 3) uint8
state (4,) float32
action (7,) float32
red_pixel [255, 0, 0]
```

亲手指出 `image[0,0]` 为什么是三个数，`fixture_state.shape` 中的逗号为什么表示一维 tuple `(4,)` 而不是四行一列 `(4,1)`。

## 5. 工程版逐步操作

完整代码在 [`code/sensor_pipeline.py`](code/sensor_pipeline.py)。阅读顺序：构造 fixture → 校验 observation/action → 归一化 → 构造摘要 → 保存 → CLI。

```bash
sed -n '1,130p' day07/code/sensor_pipeline.py
sed -n '131,280p' day07/code/sensor_pipeline.py
python3 day07/code/sensor_pipeline.py --help
python3 day07/code/sensor_pipeline.py
echo $?
```

预期结构：

```text
Image: shape=(4, 6, 3), dtype=uint8
State: shape=(4,), dtype=float32
Action: shape=(7,), dtype=float32
Saved arrays: .../learner_outputs/day07/fixture_arrays.npz
Saved summary: .../learner_outputs/day07/array_summary.json
Result type: synthetic arrays; not a VLA experiment result
0
```

查看摘要并重新读取 NPZ：

```bash
sed -n '1,160p' learner_outputs/day07/array_summary.json
python3 -c 'import numpy as np; d=np.load("learner_outputs/day07/fixture_arrays.npz"); print(d.files); print(d["image"].shape, d["action"])'
```

预期 normalized 范围在 0–1，image 仍是 uint8，action 是七维。`np.load` 得到类似字典的对象，数组名来自保存时的关键字。

## 6. 自动化测试

```bash
python3 -m unittest -v day07.tests.test_sensor_pipeline
python3 -m py_compile \
  day07/code/minimal_arrays.py \
  day07/code/sensor_pipeline.py \
  day07/tests/test_sensor_pipeline.py
```

预期 4 项测试通过：observation shape/dtype、归一化范围、动作缩放、错误六维动作被拒绝。语法检查无输出。测试在 CPU 上运行，不需要 GPU。

## 7. 动手实验

### 实验 A：改变图像尺寸

先预测 `--height 3 --width 5` 的 image shape、size 和 NPZ 中红通道最后一列，再运行：

```bash
python3 day07/code/sensor_pipeline.py --height 3 --width 5
```

预期 shape `(3,5,3)`、size 45；红通道从 0 沿宽度增长至 255。尺寸变化不代表真实相机分辨率。

### 实验 B：改变动作尺度

先预测 scale 2 时七个分量：

```bash
python3 day07/code/sensor_pipeline.py --action-scale 2
sed -n '1,160p' learner_outputs/day07/array_summary.json
```

预期前六维乘 2，gripper 仍 1。解释为什么离散/语义不同的 gripper 不应随运动尺度一起缩放。

### 实验 C：HWC 转 CHW

在个人脚本读取 NPZ，并执行：

```python
chw = np.transpose(image, (2, 0, 1))
```

先写 shape 预测，再打印。预期 `(3,H,W)`。然后验证 `image[0,0,0] == chw[0,0,0]`，说明红通道同一元素的位置映射。

### 实验 D：观察 view

复制 `image` 到个人变量，取左上 `crop = image[:2,:2]`，把 crop 全置 0。先预测原 image 是否改变，再运行。随后用 `.copy()` 重做并比较。把结论写成一句规则：需要独立修改时显式 copy。

### 实验 E：制造 NaN

在个人副本构造 state 后执行 `state[0] = np.nan`，再调用 `validate_observation`。预测异常类型与消息。预期拒绝，而不是保存看似正常摘要。恢复原代码后重跑所有测试。

## 8. 常见错误与止损

| 现象 | 先检查与处理 | 止损时间 |
|---|---|---:|
| `No module named numpy` | `sys.executable` 与同解释器 `-m pip` | 20 分钟 |
| shape 与预期相反 | 逐轴写 H/W/C 语义，不盲目 reshape | 20 分钟 |
| 颜色异常 | 查 RGB/BGR 和通道轴 | 20 分钟 |
| 归一化全为 0/异常 | 先看原 dtype，再 `astype(float32)` | 15 分钟 |
| 修改切片导致原数组变化 | 检查 view，必要时 `.copy()` | 15 分钟 |
| `NaN` 传播 | 找首次非有限值，不直接填 0 | 20 分钟 |
| 内存突然很大 | 手算 shape×dtype 字节数，缩小 fixture | 立即停止扩大 |

不要通过无意义 `reshape(-1)` 让错误消失；reshape 能改变布局解释，却不会恢复丢失的轴语义。

## 9. 与 VLA-RelComp 的连接

未来一个 observation 可能包含相机 RGB `(H,W,3)`、机器人 state `(D,)` 和 instruction；policy 输出单步 action `(7,)` 或 action chunk `(T,7)`。从今天开始每个接口都要写明轴名、dtype、值域、单位和坐标系。

图像归一化必须服从模型 processor，action 反归一化必须服从 checkpoint 数据统计。错一个 dtype/范围可能让模型“能运行但行为很差”，这属于输入/适配层问题，不应立即归因模型组合泛化失败。

Day 8 会把今天的 observation/action 放入 CPU mini evaluator：策略读取观测、环境按动作更新、循环记录 step，最终由明确 predicate 决定 success。

## 10. 检查点与答案

### 题 1

shape `(4,6,3)` 为什么不能脱离接口直接说含义？

**答案：** 数字只给长度，轴语义由接口定义；它可能是 HWC 图像，也可能代表别的三轴数据。必须同时记录轴顺序。

### 题 2

为什么 uint8 图像归一化前先转 float32？

**答案：** 避免整数类型的范围、写回和精度规则造成错误，并得到模型数值计算所需浮点结果。

### 题 3

广播有什么风险？

**答案：** 错误 shape 若恰好兼容，计算不会报错却沿错误轴扩展。关键操作后要断言 shape 并用小例子核对数值。

### 题 4

为什么 action scale 不缩放最后的 gripper？

**答案：** 本课最后一维是不同语义的夹爪命令，不是连续位姿 delta；统一缩放会改变协议。真实定义仍需按上游接口核验。

### 题 5

NPZ 和 JSON 摘要各适合保存什么？

**答案：** NPZ 保留数组 shape/dtype/数值；JSON 适合小型、可读、可检索的元数据。大真实数据需专门资产存储与索引。

## 11. 完成标准

**最低完成线：** NumPy 可导入；两个脚本和 4 项测试通过；能解释 HWC、dtype 与归一化。

**标准完成线：** 完成 A—E；能手算数组 size、转换 HWC/CHW、发现 view 和 NaN；保存 NPZ、JSON 与个人实验笔记。

**当天产物：** 教材中的最小数组示例、完整 sensor pipeline 与测试；个人目录中的 fixture NPZ、摘要和五项改动记录。

## 12. 精确外部材料

| 材料 | 精确范围 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [NumPy User Guide: Array fundamentals](https://numpy.org/doc/stable/user/basics.html) | 读 Array attributes、Indexing、Data types 三个入口的介绍，40 分钟 | shape/axis/dtype 基础 | 结构化 dtype |
| [NumPy quickstart](https://numpy.org/doc/stable/user/quickstart.html) | The Basics 至 Shape Manipulation 之前，45 分钟 | 创建、属性、逐元素运算 | 线性代数高级例子 |
| [NumPy Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) | General broadcasting rules 与最前两个例子，30 分钟 | 手判 shape 是否兼容 | 高维图像高级优化 |
| [NumPy Copies and Views](https://numpy.org/doc/stable/user/basics.copies.html) | 全页，25 分钟 | 区分索引 view 与显式 copy | 内部 strides 深挖 |
| [NumPy `savez_compressed`](https://numpy.org/doc/stable/reference/generated/numpy.savez_compressed.html) | Parameters、Returns、Examples，15 分钟 | 保存多个命名数组 | pickle 对象数组 |

每读完一节，回到 `sensor_pipeline.py` 指出一个对应语句并用 fixture 小数组验证，不连续阅读整个 NumPy 手册。
