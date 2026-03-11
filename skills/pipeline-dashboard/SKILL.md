# 流水线仪表盘 / PIPELINE DASHBOARD

---

## 目的 / Purpose

显示当前流水线状态并确定要执行的下一个任务。 / Show the current pipeline status and determine the next task to execute.

此技能不执行任务。 / This skill does NOT execute tasks.
它仅报告流水线状态并推荐下一个提示词。 / It only reports pipeline status and recommends the next prompt.

---

## 扫描目录 / Scan Directory

扫描: / Scan:

`promptsRec/`

将文件分类为: / Classify files into:

已完成任务: / Completed tasks:
- 以 `✅_` 开头的文件 / files starting with `✅_`

运行中任务: / Running tasks:
- 以 `.lock` 结尾的文件 / files ending with `.lock`

待处理任务: / Pending tasks:
- 以 `.md` 结尾但不以 `✅_` 开头的文件 / files ending with `.md` but NOT starting with `✅_`

---

## 任务优先级 / Task Priority

### 优先级规则 / Priority Rules

1. **Bug 任务优先级最高** - 编号 100-199 的任务优先处理
2. **Feature 任务按编号顺序** - 编号 000-099 按顺序执行
3. **依赖关系检查** - 前端任务需等待对应后端任务完成

### 依赖关系定义 / Dependency Definitions

前端任务依赖后端任务完成:

| 前端任务 / Frontend Task | 依赖后端任务 / Depends on Backend |
|------------------------|-----------------------------------|
| `*_ui_migration*` | 后端工作流实现 (如 keeper_confirmation, final_confirmation) |
| `*_frontend*` | 对应的后端 API 实现 |
| `order_create` | order submission workflow |
| `order_list` | order list API |
| `order_detail` | order detail API |
| `keeper_process` | keeper confirmation workflow |
| `tool_search` | tool search API |

### 依赖检测逻辑 / Dependency Detection Logic

1. 提取待处理任务的关键词
2. 扫描已完成任务，查找对应的后端任务
3. 如果依赖未完成，标记该任务为"等待依赖"
4. 跳过等待依赖的任务，继续查找下一个可执行任务

---

## 排序 / Sorting

### 优先级排序 / Priority Sorting

1. 首先按任务类型排序: Bug > Feature
2. 同类型内按编号排序
3. 考虑依赖关系，跳过无法执行的任务

### 排序算法 / Sorting Algorithm

```
1. 扫描所有待处理任务
2. 对每个任务:
   a) 判断是否为 Bug (编号 100-199 或文件名包含 _bug_)
   b) 检测依赖是否满足
   c) 计算有效优先级
3. 按优先级排序输出
4. 返回第一个可执行任务
```

按文件名升序对所有提示词相关文件排序。 / Sort all prompt-related files by filename in ascending order.

对于已完成任务，也按归档文件名升序排序。 / For completed tasks, also sort by archive filename in ascending order.

使用优先级最高且依赖满足的待处理提示词作为下一个推荐任务。 / Use the highest priority pending prompt with satisfied dependencies as the next recommended task.

---

## 负责 Agent 规则 / Responsible Agent Rules

优先级规则: / Priority rules:

1. 如果提示词文件包含: / If the prompt file contains:
   `Primary Executor:` / 主要执行者:
   直接使用该值。 / use that value directly.

2. 如果缺少元数据，根据任务类型或文件名推断: / If metadata is missing, infer by task type or filename:

| 任务类型 / Task Type | 负责 Agent / Responsible Agent |
|---------------------|-------------------------------|
| 架构 / 技术设计 / 审查 / 发布预检 / Architecture / Technical Design / Review / Release Precheck | Claude Code |
| 后端实现 / 数据库修复 / API 实现 / Backend Implementation / Database Fix / API Implementation | Codex |
| 前端设计 / Frontend Design | Gemini |
| 前端实现 / Frontend Implementation | Codex |

如不确定，优先选择 Claude Code。 / If unclear, prefer Claude Code.

---

## 输出规则 / Output Rules

### 摘要 / Summary

始终显示: / Always show:

- 已完成总数 / total completed count
- 运行中总数 / total running count
- 待处理总数 / total pending count

### 已完成任务 / Completed Tasks

不要列出所有已完成任务。 / Do NOT list all completed tasks.

仅显示最近 3 个已完成任务。 / Only show the most recent 3 completed tasks.

如果少于 3 个，显示全部。 / If there are fewer than 3, show all of them.

如果没有已完成任务，显示: / If there are no completed tasks, show:

无 / None

### 运行中任务 / Running Tasks

显示所有 `.lock` 文件。 / Show all `.lock` files.

如果没有，显示: / If none, show:

无 / None

### 待处理任务 / Pending Tasks

按优先级顺序显示所有待处理提示词文件，附带依赖状态。 / Show all pending prompt files in priority order with dependency status.

格式: / Format:

`<任务文件> [依赖状态]`

- ✅ = 依赖满足，可执行 / Dependencies satisfied, can execute
- ⏳ = 等待依赖 / Waiting for dependency

如果没有，显示: / If none, show:

无 / None

### 下一个推荐任务 / Next Recommended Task

如果存在待处理任务，显示: / If pending tasks exist, show:

- 文件 / File
- 负责 Agent / Responsible Agent
- 依赖状态 / Dependency Status
- 执行命令 / Execution Command

依赖状态说明: / Dependency Status explanation:

- ✅ 依赖满足 / Dependencies satisfied
- ⏳ 等待依赖: <依赖任务> / Waiting for dependency: <dependency>

执行命令格式: / Execution command format:

`RUNPROMPT promptsRec/<filename>`

如果没有待处理任务，显示: / If no pending tasks remain, show:

```
文件: 无 / File: None
负责 Agent: Claude Code / Responsible Agent: Claude Code
命令: release-precheck / Execution Command: release-precheck
原因: 流水线完成。运行最终发布验证。 / Reason: Pipeline complete. Run final release verification.
```

### 等待依赖的任务 / Tasks Waiting for Dependencies

显示所有因依赖未满足而无法执行的任务: / Show all tasks that cannot execute due to unmet dependencies:

```
## 等待依赖的任务 / Tasks Waiting for Dependencies

- <任务文件>: 等待 <依赖任务> 完成 / waiting for <dependency> to complete
```

---

## 响应模板 / Response Template

使用以下结构: / Use the following structure:

```
# 流水线状态 / Pipeline Status

## 摘要 / Summary

已完成: <number> / Completed: <number>
运行中: <number> / Running: <number>
待处理: <number> / Pending: <number>

## 进度 / Progress

<进度条> <百分比>% / <progress_bar> <percent>%

使用 10 单位进度条。 / Use a 10-unit progress bar.

示例: / Example:

██████░░░░ 60%

进度公式: / Progress formula:

已完成 / (已完成 + 待处理) / completed / (completed + pending)

## 最近完成的任务 / Recently Completed Tasks

- <已完成任务_1> / <completed_task_1>
- <已完成任务_2> / <completed_task_2>
- <已完成任务_3> / <completed_task_3>

如果没有: / If none:

无 / None

## 运行中的任务 / Running Tasks

- <锁文件> / <lock_file>

如果没有: / If none:

无 / None

## 待处理任务 / Pending Tasks

- <提示词文件> / <prompt_file>
- <提示词文件> / <prompt_file>

如果没有: / If none:

无 / None

## 下一个推荐任务 / Next Recommended Task

文件: <filename> / File: <filename>
负责 Agent: <Claude Code | Codex | Gemini> / Responsible Agent: <Claude Code | Codex | Gemini>
依赖状态: ✅ 或 ⏳ 等待 <依赖> / Dependency Status: ✅ or ⏳ Waiting for <dependency>
命令: RUNPROMPT promptsRec/<filename> / Execution Command: RUNPROMPT promptsRec/<filename>

## 等待依赖的任务 / Tasks Waiting for Dependencies

- <任务文件>: 等待 <依赖任务> 完成 / <task_file>: waiting for <dependency> to complete

如果没有: / If none:

无 / None
```

---

## Bug 工作流识别 / Bug Workflow Recognition

此技能必须识别 `docs/BUG_WORKFLOW_RULES.md` 中定义的 bug 工作流规则。 / This skill must recognize bug workflow rules defined in `docs/BUG_WORKFLOW_RULES.md`.

### Bug 提示词检测 / Bug Prompt Detection

Bug 提示词遵循模式: `*_bug_*.md`，编号范围为 100-199。 / Bug prompts follow the pattern: `*_bug_*.md` with numbering in 100-199 range.

### 一个 Bug 一个提示词原则 / One-Bug-One-Prompt Principle

推荐下一个任务时: / When recommending next tasks:

- 如果存在 bug 提示词 (1xx)，检查 `docs/BUG_*.md` 中是否有记录的子问题 / If a bug prompt exists (1xx), check if there are sub-issues recorded in `docs/BUG_*.md`
- 新 bug 提示词应根据 `docs/BUG_WORKFLOW_RULES.md` 第 5 节仅为升级的问题创建 / New bug prompts should only be created for escalated issues per `docs/BUG_WORKFLOW_RULES.md` Section 5

### 升级参考 / Escalation Reference

在推荐新的 bug 提示词之前，检查问题是否应作为子问题记录在现有 bug 文档中。 / Before recommending a new bug prompt, check if the issue should be recorded as a sub-issue in existing bug documentation instead.

参考: `docs/BUG_WORKFLOW_RULES.md` 作为权威来源。 / Reference: `docs/BUG_WORKFLOW_RULES.md` as the source of truth.

---

## 队列异常检测 / Queue Anomaly Detection

此技能适配 `skills/prompt-task-runner` 的 Step 7.5 规则，用于识别持续性 Bug 修复的后续任务。/ This skill adapts to prompt-task-runner Step 7.5 rules to detect follow-up tasks for persistent bug fixes.

### 检测逻辑 / Detection Logic

在显示待处理任务时，对每个任务执行以下检测:

1. **提取任务编号**: 从待处理文件名提取编号 (如 `103_bug_xxx.md` -> `103`)
2. **判断类型**: 检查是否为 Bug 提示词 (匹配 `*_bug_*.md`)
3. **扫描归档**: 在 `promptsRec/✅_*` 中查找包含相同编号的归档文件
4. **标记行为**:

   | 任务类型 / Task Type | 已有归档 / Archive Exists | 行为 / Behavior |
   |---------------------|--------------------------|----------------|
   | Bug 提示词 (1xx) / Bug Prompt | 是 / Yes | 显示 "[后续任务将合并 → ✅_序列号]" / Show "[Follow-up will merge → ✅_seq]" |
   | Bug 提示词 / Bug Prompt | 否 / No | 正常显示 / Normal display |
   | 开发提示词 / Dev Prompt | 是 / Yes | 标记为 "重复错误" / Flag as "Duplicate error" |
   | 开发提示词 / Dev Prompt | 否 / No | 正常显示 / Normal display |

### 输出示例 / Output Example

```
## 待处理任务 / Pending Tasks

- 103_bug_order_list_api_500.md [后续任务将合并 → ✅_00017]
- 020_new_feature.md
- 021_another_feature.md [⚠️ 重复: 已有归档]
```

### 原理 / Rationale

- **Bug 修复**: 允许持续修复，后续任务会自动合并到原始归档 (prompt-task-runner Step 7.5)
- **开发任务**: 严格执行不重复原则，确保流水线有序执行

---

## 约束 / Constraints

此技能严禁: / This skill must NOT:

- 执行任务 / execute tasks
- 创建文件 / create files
- 修改文件 / modify files
- 重命名文件 / rename files
- 清除锁文件 / clear lock files

它仅检查和报告流水线状态。 / It only inspects and reports pipeline state.
