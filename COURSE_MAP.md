# VLA-RelComp 课程 V2：70 天、8 阶段项目主线

Day 0 是诊断入口，不计入 70 天。F01–F18 是按需补习库，也不计入主线进度。当前主线完成数为 `0 / 70`；`Day 3 🧪` 只表示代表性样章已编写，不表示学习者已完成。

状态：`⬜ 未编写` · `📘 教材已编写` · `🧪 样章已编写` · `✅ 学习者验收通过`。教材状态与学习者完成状态分开记录。

## Day 0：诊断与跳过

[Day 0](mainline/day00_diagnostic/README.md) 用五类入口任务和延迟诊断把失败项路由到 F01–F18；全部通过者直接进入 Day 1。

## 阶段 1：开工并得到首个 episode（Day 1–7）

| Day | 真实项目任务 | 即时补充知识 | 当天必须产物 | 状态 |
|---:|---|---|---|---|
| 1 | 从锁定 commit 克隆并画出最小系统地图 | 终端、Git、仓库根、版本锁定 | `project_map.md`、commit 证明、suite 定位 | 📘 [教材已编写](mainline/day01/README.md) |
| 2 | 从 CLI/YAML 追踪到 PrepositionCombinations 任务列表 | 模块/路径、YAML、配置覆盖、容器 | `config_trace.md`、只读 suite manifest | 📘 [教材已编写](mainline/day02/README.md) |
| 3 | 沿真实 evaluator 追踪 observation→policy→action→step→success | shape/dtype、episode/step、函数调用 | observation 摘要工具、真实调用链图 | 🧪 [样章已编写](mainline/day03/README.md) |
| 4 | 在 Linux/NVIDIA 环境完成自检和可重复 episode | 进程、退出码、CUDA、headless MuJoCo | 命令、日志、视频/帧、registry；Gate 1 | 📘 [教材已编写](mainline/day04/README.md)；学习者 Gate 未通过 |
| 5 | 在真实模型 adapter 中解释 VLA 输入输出 | inference、device、图像/state/指令、动作 | 模型接口卡、离线 shape/dtype 检查 | 📘 [教材已编写](mainline/day05/README.md) |
| 6 | 跑 SmolVLA 单任务最小 pilot | VLM 条件、action chunk、checkpoint | SmolVLA pilot 与故障边界 | 📘 [教材已编写](mainline/day06/README.md)；真实 GPU pilot 待学习者执行 |
| 7 | 跑 OpenVLA/官方较强模型最小 pilot并同口径比较 | action token、连续动作、seed | 第二模型 pilot、比较表 | 📘 [教材已编写](mainline/day07/README.md)；真实 GPU pilot 待学习者执行 |

**Gate 1（Day 4）：** 从新终端完成一个 episode 和完整证据包，口述 observation、action、success 与基础设施错误；环境启动不等于 episode 成功。

## 阶段 2：完成 pilot 与行为诊断雏形（Day 8–14）

| Day | 真实项目任务 | 即时补充知识 | 当天必须产物 | 状态 |
|---:|---|---|---|---|
| 8 | 生成 L0/L1/L2 × task × seed pilot 矩阵并选择主诊断模型 | OOD、分母、选择规则 | pilot manifest、选择结论；Gate 2 | 📘 [教材已编写](mainline/day08/README.md)；真实矩阵与学习者 Gate 待执行 |
| 9 | 读取真实 CBDDL/BDDL 并解释 init/object/goal | 谓词、对象/区域、声明式任务 | 5×3 任务结构表、解析脚本 | 📘 [教材已编写](mainline/day09/README.md) |
| 10 | 找到并验证真实 success predicate | predicate、terminated/truncated、阈值 | success 路径图、predicate 检查器 | 📘 [教材已编写](mainline/day10/README.md)；真实 MuJoCo probe 待 Gate 1 环境 |
| 11 | 从仿真状态识别目标物、参照物和关系 | 坐标/位姿、对象 ID、特权边界 | object/relation state snapshot | 📘 [教材已编写](mainline/day11/README.md)；真实 MuJoCo snapshot 待 Gate 1 环境 |
| 12 | 实现接触、抬升、参照接近、终态关系四段事件日志 | 时序、阈值、假阳/假阴 | stage event logger 与测试 | 📘 [教材已编写](mainline/day12/README.md)；真实视频阈值抽查待 Gate 1 环境 |
| 13 | 构造第一组单因素匹配反事实 | 控制变量、pair ID、seed/init 固定 | pair manifest、配对校验器 | 📘 [教材已编写](mainline/day13/README.md)；真实两臂运行待 Gate 1/2 |
| 14 | 实现最小语言或视觉提示 oracle pilot | 干预、恢复率、因果边界、泄漏 | oracle pilot、诊断口述；Gate 3 | 📘 [教材与 Gate 3 已编写](mainline/day14/README.md)；真实 oracle pilot 与学习者 Gate 待执行 |

**Gate 2（Day 8）：** 对陌生 pilot 结果判断可用模型、有效分母与下一步最小实验。
**Gate 3（Day 14）：** 对陌生失败 episode 独立运行四段探针，提出两个替代解释并设计单因素干预。

## 阶段 3：建立可信基线（Day 15–25）

| Day | 真实项目任务 | 即时补充知识 | 当天必须产物 | 状态 |
|---:|---|---|---|---|
| 15 | 冻结代码、模型、数据、任务和运行口径 | revision、快照、可复现性 | baseline protocol lock | 📘 [教材已编写](mainline/day15/README.md)；formal lock 待 Gate 1/2 真实 revision |
| 16 | 建立 run/episode registry 与证据命名 | schema、主键、缺失值 | registry 生成器、schema 测试 | 📘 [教材已编写](mainline/day16/README.md)；formal registry 待真实 protocol lock |
| 17 | 构建可恢复批量 evaluator | retry、checkpoint、幂等 | batch runner、resume 状态 | 📘 [教材已编写](mainline/day17/README.md)；真实 evaluator adapter 待 Gate 1/2 |
| 18 | 按任务运行 L0 基线 | task 统计、seed、init state | L0 registry、视频索引 | 📘 [教材已编写](mainline/day18/README.md)；真实 L0 baseline/video 待 GPU |
| 19 | 按冻结口径运行 L1 | 保留测试、不得调参 | L1 registry | 📘 [教材已编写](mainline/day19/README.md)；真实 L1 held-out 运行待 GPU |
| 20 | 按冻结口径运行 L2 | 强 OOD、失败分类 | L2 registry | 📘 [教材已编写](mainline/day20/README.md)；真实 L2/失败分类待 GPU |
| 21 | 重跑关键任务验证复现性 | 随机性、多 seed、一致性 | reproducibility 表 | 📘 [教材已编写](mainline/day21/README.md)；真实配对重跑待 GPU |
| 22 | 计算任务级成功率与 Wilson 区间 | 二项计数、区间、宏/微平均 | baseline stats 脚本 | 📘 [教材已编写](mainline/day22/README.md)；真实 baseline stats 待真实 registry |
| 23 | 连接视频、异常和四段事件到 episode | evidence join、异常分类 | evidence index | 📘 [教材已编写](mainline/day23/README.md)；真实 evidence join 待真实运行产物 |
| 24 | 同口径比较候选模型并冻结主模型 | 公平比较、L0 样本充分性 | model selection memo | 📘 [教材已编写](mainline/day24/README.md)；真实候选比较/freeze 待 GPU |
| 25 | 从空 manifest 复现缩小版基线表 | 端到端复现、证据口述 | reproduction package；Gate 4 | 📘 [教材与 Gate 4 rehearsal 已编写](mainline/day25/README.md)；真实 Gate 未通过 |

**Gate 4：** 不看步骤，从新 manifest 跑缩小评测、恢复中断、生成任务级表，并解释 L1/L2 为什么不能选 checkpoint。

## 阶段 4：行为级因果诊断（Day 26–35）

| Day | 真实项目任务 | 即时补充知识 | 当天必须产物 | 状态 |
|---:|---|---|---|---|
| 26 | 把研究假设变成可观测事件和可证伪预测 | 假设、指标、替代解释 | hypothesis-to-metric 表 | 📘 [教材已编写](mainline/day26/README.md)；真实干预结果未运行 |
| 27 | 完善目标接近/接触探针 | 接触、距离、对象选择错误 | target detector、阈值测试 | ⬜ 未编写 |
| 28 | 完善抓取/抬升探针 | 支撑面、夹爪接触、持续阈值 | lift detector、敏感性图 | ⬜ 未编写 |
| 29 | 完善搬运到参照区域探针 | 轨迹距离、趋势、错误参照物 | approach detector | ⬜ 未编写 |
| 30 | 完善终态空间关系探针 | 关系操作定义 | relation detector | ⬜ 未编写 |
| 31 | 批量构造关系最小反事实对 | matching、pair asymmetry | relation pair set | ⬜ 未编写 |
| 32 | 批量构造对象组合匹配对 | 混淆因素、组合覆盖 | object-combination pair set | ⬜ 未编写 |
| 33 | 运行语言规范化 oracle | 结构化三元组、恢复/损伤 | language oracle 结果 | ⬜ 未编写 |
| 34 | 运行视觉对象提示 oracle | 仿真真值、特权边界、可撤销干预 | visual oracle 结果 | ⬜ 未编写 |
| 35 | 汇总四段转化、pair asymmetry 和 oracle 效应 | 效应量、结论边界 | diagnosis table；Gate 5 | ⬜ 未编写 |

**Gate 5：** 对未见 pair 先预测，再运行探针和干预；允许结论为“证据不足”，不得强造修复故事。

## 阶段 5：证据触发的唯一最小修复（Day 36–50）

| Day | 真实项目任务 | 即时补充知识 | 当天必须产物 | 状态 |
|---:|---|---|---|---|
| 36 | 用诊断证据选择唯一修复或停止修复 | 决策矩阵、风险/收益、负结果 | repair decision | ⬜ 未编写 |
| 37 | 构建严格 L0-only 数据和泄漏测试 | 划分、数据血缘 | L0 dataset builder | ⬜ 未编写 |
| 38 | 实现被选中的最小模块 | 模块边界、接口、回归测试 | 单一 repair module | ⬜ 未编写 |
| 39 | 构造平衡/对比/规范化样本 | sampling、pair 标签、质量 | training pairs | ⬜ 未编写 |
| 40 | 定义损失、可训练与冻结参数 | loss、梯度、parameter groups | trainability report | ⬜ 未编写 |
| 41 | 配置 LoRA/轻量微调、显存与 checkpoint | batch、累积、混合精度、LoRA | bounded train config | ⬜ 未编写 |
| 42 | 用极小数据 one-batch overfit | 闭环、loss、数据/代码诊断 | overfit smoke evidence | ⬜ 未编写 |
| 43 | 运行短训练 pilot并检查恢复 | 日志、早停、resume | training pilot | ⬜ 未编写 |
| 44 | 处理稳定性并冻结训练配置 | 数值稳定、seed、异常 | frozen recipe | ⬜ 未编写 |
| 45 | 正式训练 seed 1 | 资源记录、测试集隔离 | checkpoint 1 | ⬜ 未编写 |
| 46 | 训练 seed 2–3 或预算内重复 | 重复、方差 | checkpoints 2–3 | ⬜ 未编写 |
| 47 | 评测 L0 保持 | catastrophic damage、保持率 | L0 retention | ⬜ 未编写 |
| 48 | 首次评测 L1/L2 泛化 | 保留测试、预注册分析 | OOD results | ⬜ 未编写 |
| 49 | 做最小消融和成本匹配对照 | ablation、算力公平、单变量 | ablation table | ⬜ 未编写 |
| 50 | 继续、回退或接受负结果 | go/no-go、有限结论 | repair conclusion；Gate 6 | ⬜ 未编写 |

**Gate 6：** 从原始 registry 重建基线—修复—消融比较，检查 L0 保持、L1/L2 改善和多 seed 稳定，禁止只选最好一次。

## 阶段 6：最终实验与证据锁定（Day 51–60）

| Day | 真实项目任务 | 即时补充知识 | 当天必须产物 | 状态 |
|---:|---|---|---|---|
| 51 | 冻结最终矩阵与停止规则 | preregistration、版本冻结 | final manifest | ⬜ 未编写 |
| 52 | 干净重跑主基线 | clean-room、缓存污染 | final baseline data | ⬜ 未编写 |
| 53 | 干净重跑修复模型 | 同配置、checkpoint provenance | final repair data | ⬜ 未编写 |
| 54 | 重跑关键反事实对 | pair 完整性、缺失处理 | final pair data | ⬜ 未编写 |
| 55 | 重跑关键 oracle | 诊断与最终方法分栏 | final oracle data | ⬜ 未编写 |
| 56 | 冻结四段事件统计 | conversion rate、阶段漏斗 | stage metrics | ⬜ 未编写 |
| 57 | 完成 Wilson、恢复/损伤率与配对检验 | 效应量、区间、McNemar 边界 | statistics script | ⬜ 未编写 |
| 58 | 选择代表案例并建立视频证据表 | 避免 cherry-pick | casebook | ⬜ 未编写 |
| 59 | 汇总时间、显存、失败运行和成本 | 系统指标、实验分母 | resource table | ⬜ 未编写 |
| 60 | 冻结结果与允许的论文主张 | claim-evidence、负结果 | results lock；Gate 7 | ⬜ 未编写 |

**Gate 7：** 随机抽三条主张，指出对应表格、原始 episode、版本和不能推出的更强结论。

## 阶段 7：论文式成品（Day 61–66）

| Day | 真实项目任务 | 即时补充知识 | 当天必须产物 | 状态 |
|---:|---|---|---|---|
| 61 | 清理数据、脚本和可追溯索引 | tidy data、原始数据不可覆盖 | release candidate data | ⬜ 未编写 |
| 62 | 生成最终表格 | caption、计数、区间、加粗规则 | paper tables | ⬜ 未编写 |
| 63 | 生成阶段漏斗、pair 和干预图 | 诚实可视化、误差条 | paper figures | ⬜ 未编写 |
| 64 | 写问题、方法和实验设置 | 研究问题、操作定义 | methods draft | ⬜ 未编写 |
| 65 | 写结果、诊断与修复结论 | 证据顺序、有限语言 | results draft | ⬜ 未编写 |
| 66 | 写相关工作、限制、伦理和负结果 | scope、外推边界 | complete report draft | ⬜ 未编写 |

## 阶段 8：复现与答辩（Day 67–70）

| Day | 真实项目任务 | 即时补充知识 | 当天必须产物 | 状态 |
|---:|---|---|---|---|
| 67 | fresh clone 重建环境并复现最小表格 | lockfile、缓存、文档可执行性 | reproduction log | ⬜ 未编写 |
| 68 | 完成 README、一键入口和演示脚本 | 信息架构、失败回退 | public project entry | ⬜ 未编写 |
| 69 | 完成答辩故事、问题库和 10 分钟演示 | 口述结构、追问、诚实边界 | slides、口述稿、Q&A | ⬜ 未编写 |
| 70 | 不看答案复写核心模块并复现关键证据 | 迁移、代码所有权、最终自检 | final capstone；Gate 8 | ⬜ 未编写 |

**Gate 8：** 从 fresh clone 在限时内复现关键表、定位失败 episode、口述四段诊断和最小修复，并现场改一个参数解释影响；不能由 Agent 代做。

## Gate 通用验收

每个 Gate 必须使用新输入，明确允许/禁止材料，提供机器命令、产物、口述 rubric 和“通过 / 补做 / 停止扩张”三种结论；参考答案只在 `shared/answer_keys/`。
