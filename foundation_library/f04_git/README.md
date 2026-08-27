# Day 4：Git 提交、分支、差异与可恢复实验

> 阶段 1 / Day 4 of 70　　建议用时：7—8 小时　　第三方依赖：Git、Python 标准库

前三天已经留下程序、fixture 数据和测试。今天解决一个科研中更现实的问题：明天代码坏了，怎样准确回到今天？两次实验结果不同，怎样知道代码究竟改了哪一行？Git 的价值不是“把文件传到 GitHub”，而是给每个可解释状态一个身份，并让差异可以检查和恢复。

今天不会提交或改动教材仓库。所有会写入 Git 历史的练习都在 `learner_outputs/foundation_library/f04_git/sandbox_repo/` 临时练习仓库进行；教材脚本本身只读取当前仓库状态。

## 1. 今天学完后你能做什么

1. 区分工作区、暂存区、提交、分支与远端；
2. 解释 `status`、`diff`、`diff --staged` 分别观察哪两个状态；
3. 在隔离练习仓库中完成“修改 → 检查 → 精确暂存 → 提交”；
4. 创建分支并说明分支为什么只是指向提交的可移动名字；
5. 用 `git show` 和 commit hash 找回一次实验对应的代码；
6. 读取 JSON 形式的仓库元数据，并理解 clean 不等于代码正确；
7. 避免把输出、密钥、大模型权重和真实数据误提交。

## 2. 开始前检查与产物

从教材仓库根目录运行：

```bash
cd "$(git rev-parse --show-toplevel)"
python3 -m unittest -v foundation_library.f03_modules_testing.tests.test_episode_schema
git status --short --branch
```

Day 3 测试应为 `OK`。`git status` 可能显示当前教材制作中的变更；学习者不需要替作者提交它们。今天产物包括只读脚本 `minimal_git_status.py`、工程版 `git_evidence.py`、临时仓库测试，以及个人练习仓库和 `git_evidence.json`。

先写下预测：`git add` 是否把文件上传到 GitHub？新建分支是否复制所有文件？commit hash 是按“提交序号”生成的吗？

## 3. 今天学什么概念

### 3.1 Git 记录的是快照关系

把某一时刻所有被跟踪文件的状态想成一张快照。commit 保存这张快照的身份、父提交、作者信息和说明；下一次 commit 指向上一次，于是形成历史。Git 会复用没有变化的内容，不是粗暴复制整个目录，但初学时用“可寻址快照”理解比“撤销按钮”更准确。

commit hash 是内容和元数据计算出的标识，不是第 17 次提交这种顺序号。课程将来记录 `code_commit`，就是为了把一个 episode 指回精确代码状态。只写“最新版”无法复现，因为最新版每天会变。

### 3.2 三个位置：工作区、暂存区、HEAD

- **工作区**：你正在看的文件，可以包含尚未决定保留的编辑；
- **暂存区（index）**：你明确选择放入下一次提交的内容；
- **HEAD**：当前签出的提交，通常也是当前分支指向的位置。

两种 diff 的问题不同：

```bash
git diff                 # 工作区 与 暂存区
git diff --staged        # 暂存区 与 HEAD
```

如果修改后未 add，第一条能看到；add 后它从第一条消失，转而出现在第二条。commit 只接收暂存区，不会自动把工作区其他改动全装进去。因此本课程强调 `git add -- 明确路径`：你应该知道本次提交包含哪些文件。

### 3.3 status 是导航仪，不是裁判

`git status --short --branch` 的短格式常见两列状态：第一列代表暂存区相对 HEAD，第二列代表工作区相对暂存区。常见示例：

```text
 M fixture_note.txt   # 工作区修改，尚未暂存
M  fixture_note.txt   # 修改已暂存
?? new_file.txt       # 未跟踪
```

clean 只表示被 Git 纳入观察范围的内容没有未提交变化，不表示测试通过、数据真实或远端已同步。被 `.gitignore` 忽略的个人输出也不会让状态变脏。

### 3.4 分支是一张可移动书签

分支不是另一份神秘文件夹，而是指向某个 commit 的名字。`git switch -c fixture/experiment-a` 创建并切换分支；新 commit 后，这张书签向前移动，原分支仍留在旧提交。

为什么实验要分支？因为方法 A、方法 B 与教材稳定状态可以有不同提交序列，diff 仍清楚。分支名不能代替 commit hash：分支会移动，hash 指向具体提交。

本课程真实远端分支由作者维护；学习者今天只在 sandbox 中练习，不对 Draft PR 推送。

### 3.5 GitHub、remote、fetch、push

Git 是本地版本系统；GitHub 托管远端仓库。`origin` 通常只是远端别名。`git fetch` 获取远端引用而不把它合进当前分支；`git push` 把本地提交发送到远端；二者都不是 commit。

`ahead=2` 表示本地相对 upstream 多两个提交，`behind=1` 表示远端有一个本地尚未包含的提交。没有 upstream 时，这两个值应记为未知，而不是擅自写 0。

### 3.6 恢复不是先用破坏性命令

发现错误时先读：

```bash
git status --short --branch
git diff
git log --oneline --decorate -5
git show --stat HEAD
```

先确定错误位于未暂存修改、已暂存修改，还是已经提交的历史。不要把 `git reset --hard` 当万能修复，它会丢弃难恢复的工作区内容。本课使用新分支、额外提交和只读查看来学习恢复模型，不练习破坏性回退。

### 3.7 `.gitignore` 不会替你保密

`.gitignore` 主要防止未跟踪的生成文件被顺手加入；已经被跟踪的文件不会因为后来写进 ignore 就自动消失。密钥一旦提交，即使之后删除，历史和远端仍可能保存它。因此 `.env`、token、私钥从一开始就不写入仓库；发现泄露要撤销密钥，而不只是删文件。

VLA 项目还应排除 checkpoint、数据集、视频、缓存和虚拟环境。配置与小型 fixture 可以提交，真实大资产记录 revision、来源和校验信息即可。

## 4. 先运行 20 行最小版本

```bash
sed -n '1,120p' foundation_library/f04_git/code/minimal_git_status.py
python3 foundation_library/f04_git/code/minimal_git_status.py
```

预期显示当前 branch、短 commit，以及 `clean` 或 `changed`。作者写作时出现 `changed` 完全正常；这个程序只读，不会替你提交。

关键代码使用：

```python
subprocess.run(["git", *arguments], check=True, text=True, capture_output=True)
```

参数以列表传递，没有拼成 shell 字符串；`check=True` 让 Git 失败时不会被误当正常空输出；`capture_output=True` 让 Python 获得 stdout/stderr。

## 5. 工程版：保存可追溯状态

完整代码在 [`code/git_evidence.py`](code/git_evidence.py)。它依次调用只读 Git 命令：

```text
rev-parse --show-toplevel
branch --show-current
rev-parse HEAD
rev-parse ... @{upstream}
rev-list --left-right --count upstream...HEAD
status --porcelain=v1
```

运行：

```bash
python3 foundation_library/f04_git/code/git_evidence.py --help
python3 foundation_library/f04_git/code/git_evidence.py
echo $?
sed -n '1,120p' learner_outputs/foundation_library/f04_git/git_evidence.json
```

预期退出码为 0，JSON 包含仓库根、完整 40 位 commit、分支、upstream、ahead/behind 和 changed paths。具体 hash 与变更数量取决于运行时状态，不应照抄教材示例。`result_type` 明确说明它是仓库元数据，不是 VLA 实验结果。

注意一个细节：程序运行时若教材作者还有未提交文件，JSON 会诚实列出它们。未来记录真实实验时，理想做法是在运行前确认计划内变更已经提交，并把精确 hash 写入 registry；今天只学习读取，不自动改变仓库。

## 6. 隔离练习：亲手完成两个提交

所有命令仍从教材根执行。先建立一个可随时删除重做的个人仓库：

```bash
mkdir -p learner_outputs/foundation_library/f04_git/sandbox_repo
cd learner_outputs/foundation_library/f04_git/sandbox_repo
git init
git config user.name "Fixture Learner"
git config user.email "fixture@example.invalid"
printf 'learning_rate=0.001\n' > fixture_config.txt
git status --short --branch
```

这里的 `printf` 只写个人练习目录。预测 `??` 表示什么。然后精确暂存并检查：

```bash
git add -- fixture_config.txt
git diff
git diff --staged
git commit -m "fixture: add initial config"
git log --oneline --decorate -3
```

此时第一条 diff 应为空，`--staged` 在 commit 前显示新增行；commit 后二者都为空。

创建实验分支并改变唯一变量：

```bash
git switch -c fixture/learning-rate
printf 'learning_rate=0.002\n' > fixture_config.txt
git diff -- fixture_config.txt
git add -- fixture_config.txt
git diff --staged -- fixture_config.txt
git commit -m "fixture: compare learning rate 0.002"
git log --oneline --decorate --graph --all
```

你应看到两个 commit，分支指向第二个。这个练习不说明 0.002 更好，因为没有模型和指标；它只证明代码变量变化被隔离并记录。

回到教材根：

```bash
cd "$(git rev-parse --show-toplevel)"
```

注意这条命令在 sandbox 中会回到 sandbox 根，而不是教材根，因为内层也是 Git 仓库。应改用你开始时记录的教材绝对路径，或连续执行：

```bash
cd ../../..
git rev-parse --show-toplevel
```

预期重新显示教材仓库。嵌套仓库是今天故意制造的路径陷阱；以后实验输出目录不会保存真实内层 `.git`。

## 7. 运行自动化测试

```bash
cd "$(git rev-parse --show-toplevel)"
python3 -m unittest -v foundation_library.f04_git.tests.test_git_evidence
```

测试会在系统临时目录创建 Git 仓库、配置无效示例邮箱、提交 fixture 文件，然后验证 clean 状态；再修改文件，验证脚本能看到路径。末尾应为 `Ran 1 test` 和 `OK`。它不会改教材仓库，也不访问 GitHub。

## 8. 动手实验

### 实验 A：观察 add 前后两种 diff

在 sandbox 新增 `fixture_notes.txt`。运行前预测它会出现在 `git diff` 还是 status；未跟踪文件内容默认不会出现在普通 diff。先 `git add -- fixture_notes.txt`，再比较 `git diff` 与 `git diff --staged`。写下“add 移动了哪一份状态”，不要回答“上传了文件”。

### 实验 B：同一文件的已暂存与未暂存修改

先把 `version 1` 写入文件并 add，再追加 `version 2` 但不 add。预测短状态的两列，然后运行 `git status --short`、两种 diff。你会看到同一文件同时具有暂存和未暂存差异。含义是下一次 commit 只包含暂存时的版本，不一定等于屏幕上当前文件。

### 实验 C：用 hash 查看旧状态

运行 `git log --oneline`，复制第一个提交短 hash，只执行 `git show HASH:fixture_config.txt`。预测输出 0.001 还是 0.002。该命令读取旧快照，不切分支、不覆盖工作区。把 hash 和观察写入个人笔记。

### 实验 D：在非仓库目录测试失败路径

建立普通临时目录，并让工程脚本读取：

```bash
mkdir -p learner_outputs/foundation_library/f04_git/not_a_repo
python3 foundation_library/f04_git/code/git_evidence.py --repo learner_outputs/foundation_library/f04_git/not_a_repo
echo $?
```

预期报告不是 Git 仓库并返回 2，不生成伪造的 commit。然后回到默认命令确认仍能成功。

## 9. 常见错误与止损

| 现象 | 原因与处理 | 止损时间 |
|---|---|---:|
| Git 要求 user.name/email | 只在 sandbox 用示例身份配置，不改全局设置 | 10 分钟 |
| `nothing to commit` | 先看 status；文件可能没变、已忽略或未 add | 15 分钟 |
| 普通 diff 为空但 status 有 `M ` | 变更已经暂存，查看 `diff --staged` | 10 分钟 |
| 回不到教材根 | 当前在嵌套 sandbox 仓库；按目录层级退回 | 10 分钟 |
| detached HEAD | 只读查看 branch/log，不在不理解时提交 | 20 分钟 |
| 不小心把敏感值写入 commit | 停止推送，立即撤销该凭据并寻求历史清理 | 立即停止 |

今天禁止用 `reset --hard`、强推或改教材 `main` 来解决练习错误。sandbox 做乱了可以保留笔记后重建个人练习目录；不要删除教材仓库。

## 10. 与 VLA-RelComp 的连接

一次可信 episode 至少要关联 code commit、配置、模型 revision、task、seed/init state 和证据路径。Git 主要解决第一项和小型文本配置，不负责保存模型权重或证明环境正确。将来出现 L1 成功率变化时，先检查比较双方是否来自明确 commit，diff 是否只包含计划改动。

分支适合探索，commit 适合定位，tag 可用于阶段性不可移动标记，Draft PR 适合集中审阅整套教材。它们解决不同问题。今天留下的 `git_evidence.py` 会在后续实验目录章节扩展为运行 manifest 的一部分。

## 11. 检查点与答案

### 题 1

`git add` 做了什么，没做什么？

**答案：** 它把指定内容放进本地暂存区，准备进入下一 commit；它没有创建 commit，也没有上传 GitHub。

### 题 2

为什么 `git diff` 为空仍可能有尚未提交的修改？

**答案：** 普通 diff 比较工作区与暂存区。变更若已暂存，应使用 `git diff --staged` 比较暂存区与 HEAD。

### 题 3

分支名与 commit hash 哪个更适合写进实验记录，为什么？

**答案：** 精确 commit hash；分支会随新提交移动，hash 指向具体历史对象。可以同时记分支方便阅读，但不能只记分支。

### 题 4

工作区 clean 能证明实验可复现吗？

**答案：** 不能。它只说明 Git 可见范围没有未提交变化，还需依赖、模型/数据 revision、配置、seed、环境与原始证据。

### 题 5

为什么不把 checkpoint 和视频直接全部提交到 Git？

**答案：** 它们体积大、变化方式不适合普通 Git，还可能有许可或隐私问题。仓库保存代码、配置、小 fixture 和资产标识，大文件使用获批存储并记录来源与校验。

## 12. 完成标准

**最低完成线：** 运行两个只读脚本和单元测试；在 sandbox 完成两个 commit；能解释两种 diff。

**标准完成线：** 完成实验 A—D；能根据 status 判断内容在哪一层；用 hash 读取旧文件；保存个人 Git 笔记和 `git_evidence.json`。

**当天产物：** 教材中的 Git 证据脚本与测试，个人目录中的 sandbox 历史、JSON 和笔记。个人 sandbox 不提交。

## 13. 精确外部材料

| 材料 | 精确范围与用时 | 看完应会什么 | 暂时跳过 |
|---|---|---|---|
| [Pro Git 2nd ed. §1.3 What is Git?](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F) | 重点读 Snapshots、Nearly Every Operation Is Local、Three States，30 分钟 | 快照与三个状态 | SHA-1 密码学细节 |
| [Pro Git §2.2 Recording Changes](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) | 从 checking status 到 committing changes，45 分钟 | status、diff、add、commit | 跳过删除/移动批量练习 |
| [Pro Git §2.3 Viewing History](https://git-scm.com/book/en/v2/Git-Basics-Viewing-the-Commit-History) | 读 `git log` 基础与 `--stat`/`--oneline`，20 分钟 | 定位 commit 与查看概要 | 复杂 pretty format |
| [Pro Git §3.1 Branches in a Nutshell](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell) | 读到 Creating a New Branch，35 分钟 | 分支是提交指针 | 合并、rebase 留到需要时 |
| [Git `status` 官方文档 Short Format](https://git-scm.com/docs/git-status#_short_format) | 只读 Short Format 表格，20 分钟 | 看懂 XY 两列 | porcelain v2 细节 |

外部材料用于核对 Git 的正式模型；操作仍以本课隔离 sandbox 为主。看完每节后回到自己的 `git log --graph` 指出 HEAD、当前分支和两个 commit。
