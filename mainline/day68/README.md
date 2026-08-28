# Mainline Day 68：完成 README、一键入口和演示脚本

今天把仓库变成第一次访问也能行动的 public entry：START_HERE 同时给 learner/reviewer path、五分钟 one-command demo、expected output、failure fallback 和 evidence legend。Demo 只跑免费路由、结构与 synthetic table。

## 1. 真实项目产物

- 根 [START_HERE](../../START_HERE.md) 的公开导航与证据图例；
- [course_demo.py](../../shared/scripts/course_demo.py) 的一键 smoke；
- `demo_report.json` 的逐步 exit/output/fallback；
- B 新步骤顺序/输入的 demo 与 memo。

## 2. 当前卡点

README 信息很多却没有“现在运行什么”，新读者仍会迷路；单一入口只服务学习者，又不利于审阅者快速验证证据。命令失败若只抛 traceback，也无法把读者路由到正确层级。

本课把首屏任务压缩为 one command，并为每步存具体 fallback；真实 GPU 路径仍独立标注，不在演示中偷跑。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day68/code/minimal_failure_fallback.py
```

应看到 route PASS、table FAIL 及其下一步。若 CLI/退出码不熟补 [F05](../../foundation_library/f05_linux_processes/README.md)；课程入口先读 [Day 0](../day00_diagnostic/README.md)。

## 4. 即时知识

- **information architecture**：按用户问题组织入口，不按作者文件历史堆叠。
- **public entry**：新读者在首屏能判断对象、起点、命令和边界。
- **learner/reviewer path**：完成任务与核验证据的两条不同路径。
- **one-command demo**：一个命令运行最小代表性闭环。
- **expected output**：成功时可核对的稳定短句与报告。
- **failure fallback**：失败后最小、具体、可执行的下一步。
- **evidence legend**：防止“文件存在、测试通过、真实实验完成”混写。

## 5. 成熟材料处方

- **主材料（Diátaxis，10 分钟）**：[Diátaxis documentation framework](https://diataxis.fr/)。只看 tutorials/how-to/reference/explanation 四象限，理解入口为何按读者任务分流。
- **补充材料（Python 官方中文，6 分钟）**：[argparse 教程](https://docs.python.org/zh-cn/3/howto/argparse.html)。只看位置/可选参数和 help 输出，让 demo CLI 可发现。
- **锁定项目定位（8 分钟）**：[upstream README 快速开始第 42–70 行](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/README.md#L42-L70) 是完整环境入口；本课 public demo 明确不把安装/下载/GPU 当免费 smoke。

## 6. 最小实验

[minimal_failure_fallback.py](code/minimal_failure_fallback.py) 是完整 16 行代码：

```python
#!/usr/bin/env python3
"""最小例子：入口命令失败时给下一条可执行回退。"""

checks = [
    {"name": "route", "exit_code": 0, "fallback": "打开 Day 0"},
    {"name": "table", "exit_code": 2, "fallback": "核对 input/expected hash"},
]

for check in checks:
    if check["exit_code"] == 0:
        status = "PASS"
        next_action = "继续下一步"
    else:
        status = "FAIL"
        next_action = check["fallback"]
    print(f"{check['name']}: {status}; next={next_action}")
```

长文件 [course_demo.py](../../shared/scripts/course_demo.py) 用当前 Python 子进程执行 spec 步骤，捕获 exit/output 并生成 fail-helpfully report。

## 7. 真实 VLA-Arena 操作

```bash
python3 shared/scripts/course_demo.py \
  --spec shared/fixtures/day68_demo_a.json \
  --output learner_outputs/mainline/day68/demo_a.json
```

应见 `PASS ... steps=3 gpu=false`。真实 VLA-Arena 入口仍按锁定 README 另建 Python 3.11 环境并保存安装、权重与 GPU 证据；public smoke 失败时不自动下载、安装或租 GPU。

## 8. 独立挑战

换 B spec 和新输出运行。写 ≥270 字 memo，原样包含 `public entry`、`five-minute demo`、`learner path`、`reviewer path`、`one command`、`expected output`、`failure fallback`、`evidence legend`、`Day 0`、`COURSE_MAP`、`synthetic`、`cannot claim`。说明 B 步骤顺序为何仍可审计。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day68.tests.test_day68_tools
.venv-day06/bin/python mainline/day68/code/check_day68.py \
  --example-spec shared/fixtures/day68_demo_a.json --example-report learner_outputs/mainline/day68/demo_a.json \
  --challenge-spec shared/fixtures/day68_demo_b.json --challenge-report learner_outputs/mainline/day68/demo_b.json \
  --challenge-memo learner_outputs/mainline/day68/challenge_memo.md
```

口述 10 分：首屏/one command 2；两条路径 2；expected 2；fallback 2；legend/boundary 2。机器通过且 ≥8 才完成 Day 68；死链、静默失败、自动重依赖/GPU、无证据图例或 demo 当模型结果均不通过。

## 10. 证据复盘

- 已运行：A/B public demo 的 Day 0 路由、V2 结构和 synthetic table。
- 静态源码事实：锁定 upstream README 的完整安装入口。
- 未运行：upstream 安装、模型下载、MuJoCo、NVIDIA/GPU 与 episode。
- 可以主张：新读者可用一个免费命令获得逐步 PASS/fallback。
- 不能主张：public demo 证明 VLA-Arena 或模型可运行。

自测题（答案在 `shared/answer_keys/day68.md`）：

1. public entry 首屏回答什么？
2. learner/reviewer path 有何不同？
3. one command 失败后应提供什么？
4. evidence legend 区分哪些状态？
5. demo PASS 等于模型运行吗？
