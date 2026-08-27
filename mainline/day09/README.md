# Mainline Day 9：从真实 BDDL 读出对象、初态和目标关系

今天不看视频猜任务，而是从锁定 commit 的 15 个真实 BDDL 声明中回答：有哪些对象、目标物与参照物初始在哪里、成功要求哪个关系成立。你会生成 L0/L1/L2 各 5 行的结构表，并保留上游 `obj_of_interest` 与 `goal` 不一致的静态证据。

## 1. 真实项目产物

- `learner_outputs/mainline/day09/task_structures.json`：15 task 的 language、对象类型、init placement、goal 三元组与元数据一致性；
- `learner_outputs/mainline/day09/task_structures.md`：5×3 可读表；
- `learner_outputs/mainline/day09/challenge_structure.json`：新教学 BDDL 的独立解析；
- `learner_outputs/mainline/day09/challenge_reflection.md`：解释为什么 goal 优先于 `obj_of_interest`，但不能修改 upstream。

本日产物全是静态声明结构，不是仿真状态 snapshot，也不证明任务能成功启动。

## 2. 当前卡点

自然语言说“把番茄放到碗上”很容易理解，但研究探针需要稳定对象 ID：究竟是 `tomato_1` 还是 `tomato_3`，参照是哪个 `porcelain_bowl`，终态检查是 `On` 还是 `In`。这些不能靠文件名或语言猜，必须读 `:init` 和 `:goal`。

锁定数据还有一个真实陷阱：部分 `:obj_of_interest` 没覆盖 goal 的两个参数。它可能是辅助元数据，却不是成功判定。解析器因此同时保留两者：target/reference 从单个二元 goal 得出；interest 只报告覆盖与否，不自动覆盖 goal、不“修复”研究仓库。

## 3. 前置诊断

```bash
.venv-day06/bin/python mainline/day09/code/minimal_sexpr.py
```

应看到嵌套 tree、relation `On`、target `tomato_2`、reference `porcelain_bowl_1`。嵌套列表/字典卡住补 [F02](../../foundation_library/f02_csv_json/README.md)，递归函数和测试卡住补 [F03](../../foundation_library/f03_modules_testing/README.md)；通过就直接继续。

## 4. 即时知识

- **声明式任务**：BDDL 写“必须有哪些事实”，不是按时间写机器人每一步怎么动。
- **对象与类型**：`:objects` 中 `tomato_1 - tomato` 把实例 ID 和类别分开；研究日志必须用实例 ID。
- **初态谓词**：`:init` 的 `(On a b)`、`(In a region)` 描述 episode 起点；这里先静态记录，不把 region 名误当坐标。
- **目标谓词**：`:goal (And (On target reference))` 是成功逻辑。本套件锁定文件恰好都是一个二元 goal，本课才可取三元组。
- **target/reference**：对 `On/In`，第一个参数是被移动对象，第二个是目标容器/承载物；relation 是谓词名。
- **metadata 边界**：`obj_of_interest` 原样保存并做一致性提示，不能静默改写 goal。

## 5. 成熟材料处方

- **中文主材料（20 分钟）**：[VLA-Arena 锁定版《场景构建指南》§1 BDDL 文件结构](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/docs/scene_construction_zh.md#1-bddl-文件结构)。只读 1.1–1.4，重点是 objects、obj_of_interest、init、goal；不创建新场景。
- **论文补充（英文，10 分钟）**：[VLA-Arena §2.1 Constrained BDDL](https://arxiv.org/html/2512.22539v4#S2.SS1)。只读 CBDDL 为什么用于正式任务/约束声明；安全谓词留到后续课程。

## 6. 最小实验

[minimal_sexpr.py](code/minimal_sexpr.py) 是完整递归解析示例：

```python
#!/usr/bin/env python3
"""把极小 BDDL S-expression 解析成嵌套列表。"""

from collections import deque


def parse_one(tokens: deque[str]):
    token = tokens.popleft()
    if token != "(":
        return token
    result = []
    while tokens and tokens[0] != ")":
        result.append(parse_one(tokens))
    if not tokens:
        raise ValueError("缺少右括号")
    tokens.popleft()
    return result


def parse(text: str):
    spaced = text.replace("(", " ( ").replace(")", " ) ")
    tokens = deque(spaced.split())
    expression = parse_one(tokens)
    if tokens:
        raise ValueError("顶层表达式之后仍有 token")
    return expression


if __name__ == "__main__":
    sample = "(:goal (And (On tomato_2 porcelain_bowl_1)))"
    tree = parse(sample)
    predicate = tree[1][1]
    print("tree", tree)
    print("relation", predicate[0])
    print("target", predicate[1])
    print("reference", predicate[2])
```

它只支持本日所需的括号/atom，不冒充完整 PDDL parser；完整工程脚本另外处理注释、section 唯一性、typed objects 和错误退出。

## 7. 真实 VLA-Arena 操作

```bash
export VLA_ARENA_LOCKED=/absolute/path/to/VLA-Arena
.venv-day06/bin/python mainline/day09/code/build_task_structures.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --json-output learner_outputs/mainline/day09/task_structures.json \
  --markdown-output learner_outputs/mainline/day09/task_structures.md
sed -n '1,30p' learner_outputs/mainline/day09/task_structures.md
```

应看到 15 行和一个非零 `metadata warnings` 计数。脚本通过 `git show HEAD:path` 读取 sparse checkout 中的真实 blob，先从锁定 [task map](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/benchmark/vla_arena_suite_task_map.py#L163-L185) 得到 level/task_id，再解析每个 [BDDL 文件（L0 task 0 示例）](https://github.com/PKU-Alignment/VLA-Arena/blob/babe582ebffc82b979b77964a7e56417d02f63a4/vla_arena/vla_arena/bddl_files/extrapolation_preposition_combinations/level_0/pick_the_tomato_in_the_top_layer_of_the_drawer_and_place_it_on_the_bowl_between_the_vase_and_the_teapot.bddl)。

[build_task_structures.py](code/build_task_structures.py) 的关键顺序是：tokenize→递归 S-expression→定位唯一 section→解析 typed objects→取单个二元 goal→在 init 中找 target/reference placement→输出一致性警告。它不 import MuJoCo，也不读取二进制 `.pruned_init`；后者是 episode 初始状态向量，不等于 BDDL 的符号 `:init`。

## 8. 独立挑战

换用 `shared/fixtures/day09_challenge.bddl`，生成 `learner_outputs/mainline/day09/challenge_structure.json`。这是本地教学输入，不是 upstream task，relation、对象类型和 metadata 均与最小示例不同。

不给完整命令；从 `extract_fixture.py --help` 和主操作迁移。然后写至少 100 字 `challenge_reflection.md`，必须精确比较 `obj_of_interest` 与 `goal` 的对象 ID、说明 relation，并解释为什么保留提示而不改输入。正文不展示正确三元组。

## 9. 机器验收与口述 rubric

```bash
.venv-day06/bin/python -m unittest -v mainline.day09.tests.test_day09_tools
.venv-day06/bin/python mainline/day09/code/check_day09.py \
  --upstream "$VLA_ARENA_LOCKED" \
  --table-json learner_outputs/mainline/day09/task_structures.json \
  --table-md learner_outputs/mainline/day09/task_structures.md \
  --challenge-input shared/fixtures/day09_challenge.bddl \
  --challenge-output learner_outputs/mainline/day09/challenge_structure.json \
  --challenge-reflection learner_outputs/mainline/day09/challenge_reflection.md
```

口述 10 分：objects/type 2；init 与二进制 init state 区别 2；goal 三元组与 target/reference 3；语言/interest/goal 边界 2；静态/仿真边界 1。机器通过且 ≥8 进入 Day 10；5–7 按弱项补 F02/F03。若擅自修改 upstream 或用语言覆盖 goal，停止扩张并重做证据分层。

## 10. 证据复盘

- 已运行：锁定 15 BDDL blob 的递归解析、5×3 表、metadata 覆盖检查、教学 challenge 与单元测试。
- 未运行：`.pruned_init` 反序列化、MuJoCo 对象生成、任何 success predicate。
- 可以主张：锁定声明中的对象类型、符号初态、goal 三元组和静态 metadata 差异。
- 不能主张：上游 metadata 一定是 bug、自然语言与 goal 哪个“语义正确”、或仿真终态会按预期判 success；Day 10 才追真实判定代码。

自测题（答案在 `shared/answer_keys/day09.md`）：

1. `:objects`、`:init`、`:goal` 分别回答什么？
2. 怎样从二元 goal 得到 relation、target 和 reference？
3. 为什么 `obj_of_interest` 不能替代 goal？
4. 自然语言和 goal 看起来不一致时应怎样处理？
5. 静态 BDDL 解析通过后仍有哪些事实未知？
