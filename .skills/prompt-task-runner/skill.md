# RUNPROMPT / 运行提示词任务

**规则约束**: 本技能执行提示词时，根据任务类型调用相应规则：
- 功能任务 (00001-09999) → `.claude/rules/01_workflow.md` (ADP)
- Bug修复任务 (10101-19999) → `.claude/rules/02_debug.md` (8D)
- 重构任务 (20101-29999) → `.claude/rules/01_workflow.md` (ADP)
- 测试任务 (30101-39999) → `.claude/rules/01_workflow.md` (ADP)
- 生产环境紧急修复 → `.claude/rules/03_hotfix.md` (HOTFIX)
- 编号约定 → `.claude/rules/05_task_convention.md`

命令触发: RUNPROMPT / Command Trigger: RUNPROMPT

---

## 目的 / Purpose

从 `promptsRec/active/` 目录执行一个提示词任务，并通过移动到 `promptsRec/archive/` 目录来标记完成。 / Execute one prompt task from the `promptsRec/active/` directory and mark completion by moving to `promptsRec/archive/`.

支持的执行者: / Supported executors:

- Claude Code
- Codex
- Gemini

---

## 严格规则：禁止删除提示词文件 / Strict Rule: Never Delete Prompt Files

`promptsRec/active/` 和 `promptsRec/archive/` 目录内的文件严禁删除。 / Files inside `promptsRec/active/` and `promptsRec/archive/` must never be deleted.

唯一有效的完成操作是： / The only valid completion action is:

将原始提示词文件重命名为归档文件。 / Rename the original prompt file into an archived file.

## 并行执行注意事项 / Parallel Execution Note

当多个执行者（Claude Code、Codex、Gemini）可能并行执行任务时，必须：

1. **先创建锁文件**: 在执行任何任务前创建 .lock 文件，防止重复执行
2. **使用 .sequence 获取执行顺序号**: 从 `promptsRec/.sequence` 读取 `exec_next` 作为归档执行顺序号
3. **后续任务合并**: 归档前扫描 archive 查找同编号的原始归档（用于追加后续工作）

When multiple executors (Claude Code, Codex, Gemini) may execute tasks in parallel, you must:

1. **Create lock file first**: Create .lock file before executing any task to prevent duplicate execution
2. **Use .sequence for execution number**: Read `exec_next` from `promptsRec/.sequence` for archive sequence number
3. **Detect follow-up tasks**: Scan archive to find same-numbered original archive for merging follow-up work

---

## 执行流程 / Execution Flow

### 1. 发现任务 / Discover Task

扫描目录: / Scan the directory:

`promptsRec/active/`

选择符合以下条件的文件: / Select files that:

- 以 .md 结尾 / end with .md
- 没有对应的 .lock 文件 / do NOT have a corresponding .lock file

**重要**: 如果有对应的 .lock 文件存在，说明该任务正在被另一个执行者处理，跳过该任务。/ **Important**: If a corresponding .lock file exists, it means the task is being processed by another executor, skip this task.

按文件名排序并选择最早的文件。 / Sort by filename and select the earliest file.

---

### 2. 创建锁文件 / Create Lock

**必须在执行任何任务前创建锁文件**。 / **Lock file must be created before executing any task**.

在提示词旁边创建锁文件。 / Create a lock file next to the prompt.

示例: / Example:

```
001.md
→ 001.lock
```

锁文件内容应包含: / Lock file content should include:

```
{
  "executor": "Codex",
  "start_time": "2026-03-12T10:00:00Z",
  "status": "running"
}
```

如果 .lock 文件已存在，停止执行并选择下一个任务。 / If a .lock file already exists, stop execution and select the next task.

---

### 3. 读取提示词元数据 / Read Prompt Metadata

提取元数据（如果存在）: / Extract metadata if present:

- Primary Executor / 主要执行者
- Task Type / 任务类型
- Stage / 阶段
- Goal / 目标
- Execution / 执行方式

如果当前执行者与 Primary Executor 不匹配，停止执行。 / If the current executor does not match Primary Executor, stop execution.

---

### 4. Bug 工作流检查（仅适用于 Bug 提示词）/ Bug Workflow Check (For Bug Prompts Only)

如果提示词是 bug 提示词（文件名匹配 `*_bug_*.md`）: / If the prompt is a bug prompt (filename matches `*_bug_*.md`):

1. 以 `.claude/rules/02_debug.md` 作为权威来源 / Reference `.claude/rules/02_debug.md` as the source of truth
2. 检查 bug 是否遵循一个 bug 一个提示词原则 / Check if the bug follows one-bug-one-prompt principle
3. Bug 修复任务必须执行 D1-D8 步骤，且 D3/D5/D6 必须有 reviewer 评分审核

---

### 5. 执行任务 / Execute Task

执行提示词中定义的工作。 / Execute the work defined in the prompt.

允许的输出包括: / Allowed outputs include:

- 文档 / documentation
- 后端实现 / backend implementation
- 前端实现 / frontend implementation
- 设计文档 / design documents
- 审查报告 / review reports

执行规则: / Execution rules:

- 无占位符文本 / no placeholder text
- 遵循项目文档 / follow project documentation
- 进行最小安全修改 / perform minimal safe modifications

---

### 5.1 默认规则调用 / Default Rule Invocation

根据任务类型，执行者必须调用相应的项目规则：

| 任务类型 | 编号范围 | 默认调用规则 |
|---------|---------|------------|
| 功能任务 / Feature | 00001-09999 | `.claude\rules\01_workflow.md` (ADP开发协议) |
| Bug修复任务 / Bug Fix | 10101-19999 | `.claude\rules\02_debug.md` (8D问题解决协议) |
| 重构任务 / Refactoring | 20101-29999 | `.claude\rules\01_workflow.md` (ADP开发协议) |
| 测试任务 / Testing | 30101-39999 | `.claude\rules\01_workflow.md` (ADP开发协议) |

**规则适用场景说明**：

| 规则文件 | 适用场景 |
|----------|---------|
| `01_workflow.md` (ADP) | 功能开发、UI改进、架构重构、测试任务 — 严格按照四阶段顺序执行 |
| `02_debug.md` (8D) | Bug修复、回归问题 — 仅用于调试或回归问题，必须深挖根因 |
| `03_hotfix.md` | 热修复 — 仅用于生产环境紧急修复，强调最小变更和快速验证 |

**规则调用方式**: 在执行任务前，先加载对应的规则文件，按照规则中定义的流程执行。规则文件内容作为执行者的必须遵守的约束条件。

**优先级**: 如果提示词中明确指定了不同的规则或流程，以提示词中的指示为准。

**功能任务规则 (03_hotfix.md)**:
- 最小影响范围
- 原子性变更
- 立即验证

**Bug修复任务规则 (02_debug.md)**:
- D1 团队组建
- D2 问题描述
- D3 遏制措施 → **全部维度达标**
- D4 根本原因分析
- D5 永久解决方案 → **全部维度达标**
- D6 实施 → **全部维度达标**
- D7 预防
- D8 文档

**各维度最低门槛**：root_cause_depth≥0.24, solution_completeness≥0.24, code_quality≥0.16, test_coverage=0.20(满分)

**重构任务规则 (01_workflow.md)**:
- Phase 1: 业务需求与场景
- Phase 2: 数据流转与深度穿透防御
- Phase 3: 架构设计与约束
- Phase 4: 精确执行与集成验证
- Phase 5: UI一致性验证

---

### 5.1.1 统一执行规则 / Unified Execution Rule

根据任务类型，执行者必须遵循以下规则：

| 任务类型 | 条件 | 执行者 |
|---------|------|--------|
| 重构任务 (20101-29999) | 始终 | Claude Code |
| 测试任务 (30101-39999) | 始终 | Claude Code |
| Bug 修复 (P0/P1 恶性) | 始终 | Claude Code |
| 简化任务 | 始终 | Claude Code |
| 功能任务 (00001-09999) | 前端设计大改 | Claude Code |
| 功能任务 (00001-09999) | 后端/前端实现 | Codex |
| Bug 修复 (普通) | 不涉及架构变更 | Codex |

**简化任务判定**：以下情况视为"简化任务"：
- 参数类型不匹配修复
- API 调用参数提取错误
- 简单函数签名修正
- docstring 更新
- 文档同步
- 单文件/单函数修改

**恶性 Bug 判定**：
- P0：系统无法运行、数据损坏风险
- P1：核心功能损坏、API 不可用、工作流阻塞

---

### 5.1.2 依赖检查与中止规则 / Dependency Check and Abort Rules

**关键规则：如果任务在执行过程中发现依赖的任务未完成，必须立即中止并删除锁。**

在执行任何任务前，必须执行以下依赖检查：

#### 依赖检查流程 / Dependency Check Flow

1. **解析 Dependencies**: 从提示词 Header 中提取 `Dependencies` 字段
2. **检查归档状态**: 扫描 `promptsRec/archive/` 目录，确认所有依赖任务已归档
3. **检查执行状态**: 确认依赖任务不是当前正在执行的任务（带锁但未归档）

#### 依赖未完成的判定 / Dependency Not Met Criteria

满足以下任一条件视为"依赖未完成"：

| 条件 | 说明 |
|------|------|
| 依赖任务无归档文件 | `promptsRec/archive/` 中不存在对应的 ✅/🔶 归档文件 |
| 依赖任务有锁但无归档 | 依赖任务存在 .lock 文件但未归档 |
| 循环依赖检测 | 当前任务间接依赖自己 |

#### 中止执行与锁删除操作 / Abort Execution and Lock Removal

如果检测到依赖未完成：

```
1. 立即停止执行（不继续下一步操作）
2. 删除当前任务的 .lock 文件（如果存在）
3. 生成中止报告到 logs/prompt_task_runs/
4. 不归档提示词文件（保留在 active 目录）
5. 输出警告信息
```

**中止报告格式**：
```markdown
# 任务中止报告 / Task Abort Report

## 基本信息
- 任务编号: <提示词编号>
- 任务文件: <提示词文件名>
- 中止时间: <时间戳>
- 中止原因: 依赖任务未完成

## 依赖检查结果
- 依赖任务: <Dependencies 中列出的任务>
- 检查结果: ❌ 未完成 / ✅ 已完成
- 依赖归档文件: <无 / 存在>

## 执行操作
- [x] 停止任务执行
- [x] 删除 .lock 文件
- [ ] 归档提示词（未执行 - 依赖未满足）

## 后续建议
- 等待依赖任务完成后重新执行
- 或确认依赖任务是否应该被标记为已完成
```

#### 依赖检查时机 / When to Check Dependencies

| 时机 | 是否检查 |
|------|---------|
| 执行任务前（Step 3） | ✅ 必须检查 |
| 发现新的依赖问题时 | ✅ 必须检查并中止 |
| 任务执行中途 | ✅ 如果发现依赖问题立即中止 |

#### 示例场景 / Example Scenarios

**场景 1：前端任务依赖后端任务未完成**

```
提示词: 20111_refactor_tool_code_to_serial_no_frontend.md
Dependencies: 20110（后端和数据库重构完成后）
检查结果: 20110 未归档 → 依赖未完成
操作: 中止执行，删除锁（如有），生成中止报告
```

**场景 2：Bug修复依赖之前的bug修复未完成**

```
提示词: 10115_bug_order_list_filter.md
Dependencies: 10110, 10112
检查结果: 10112 未归档 → 依赖未完成
操作: 中止执行，删除锁（如有），生成中止报告
```

---

### 5.2 文档同步检查 / Documentation Sync Check

执行任务时如发现文档与实现不一致，应立即同步更新文档：

1. **功能实现后**: 检查 PRD.md 是否反映最新功能
2. **API 实现后**: 检查 API_SPEC.md 是否与实现一致
3. **权限变更后**: 检查 RBAC 文档是否同步
4. **Schema 变更后**: 检查 DB_SCHEMA.md 和 column_names.py 是否同步

如需更新权威文档，在执行报告中记录：
- 更新的文档
- 更新原因
- 主要变更内容

---

### 6. 编写执行报告 / Write Execution Report

在以下位置创建报告: / Create a report in:

`logs/prompt_task_runs/`

文件名格式: / Filename format:

`run_[时间戳]_[提示词名称].md`

报告必须包含: / Report must include:

- 提示词文件 / prompt file
- 执行者 / executor
- 开始时间 / start time
- 结束时间 / end time
- 创建的文件 / files created
- 更新的文件 / files updated
- 执行状态 / execution status

---

#### 6.1 持续性 Bug 修复的日志规则 / Logging Rules for Persistent Bug Fixes

对于持续性 bug 修复 (后续任务合并场景):

1. **每次执行必记录**: 无论任务大小，每次 RUNPROMPT 执行后必须在 `logs/prompt_task_runs/` 创建运行报告

   / Regardless of task size, every RUNPROMPT execution must create a run report in logs/prompt_task_runs/

2. **自动追加**: 后续任务合并时，将运行报告内容自动追加到原始归档的 "## 后续工作" 部分

   / When merging follow-up tasks, automatically append run report content to the original archive's "## Follow-up Work" section

3. **包含内容** / Include:

   - 执行时间 / Execution time
   - 代码改动 / Code changes
   - 验证结果 / Verification results
   - 人工确认状态 / Human confirmation status (如适用 / if applicable)

4. **无需人工确认**: 日志记录是自动的，代表实际发生的操作，不受人工审核结果影响

   / No human confirmation required: Logging is automatic, representing actual operations performed, not affected by human review results

---

### 7. 归档提示词 / Archive Prompt

**关键步骤：确定正确的执行顺序号和类型编号**

归档文件名使用**双5位编号**格式：

```
✅_<执行顺序号>_<类型编号>_<原始编号>_<描述>_done.md
```

**执行顺序号分配规则**:
为避免频繁扫描 archive 目录，使用 `promptsRec/.sequence` 文件维护执行顺序号计数器。

1. **读取计数器**: 读取 `promptsRec/.sequence` 中的 `exec_next` 值
2. **分配序号**: 使用当前值作为归档文件的执行顺序号
3. **更新计数器**: 使用 replace_all 模式原子递增 `exec_next`

**类型编号分配规则**:
根据任务类型分配类型编号（第二个5位）：

| 任务类型 | 原始编号范围 | 类型编号范围 | 示例 |
|---------|------------|------------|------|
| 功能任务 | 00001-09999 | 00001-09999 (自增) | `00001`, `00002` |
| Bug修复任务 | 10101-19999 | 10101-19999 (自增) | `10101`, `10102` |
| 重构任务 | 20101-29999 | 20101-29999 (自增) | `20101`, `20102` |
| 测试任务 | 30101-39999 | 30101-39999 (自增) | `30101`, `30102` |

**并发保护**: `.sequence` 文件使用 replace_all 模式更新，具有原子性。如遇并发冲突，执行者应重试读取最新值。

**注意**: `.sequence` 文件是执行顺序号的唯一真实来源。严禁扫描 archive 目录来确定顺序号。

Archive format:

`✅_<执行顺序号>_<类型编号>_<原始编号>_<描述>_done.md`

示例: / Example:

```
003_backend_implementation.md (功能任务)

✅_00003_00003_003_backend_implementation_done.md
```

```
101_bug_tool_search_routing.md (Bug任务)

✅_00015_10101_101_bug_tool_search_routing_done.md
```

#### 任务类型归档图标规则 / Task Type Archive Icon Rules

根据任务类型使用不同的归档规则:

1. **Bug 修复任务** (文件名匹配 `*_bug_*.md` 或编号 10101–19999):

   - **确认状态判断**: 检查任务是否需要人工确认 / Check if the task requires human confirmation

     - 如果任务执行报告中标记为 "AI 确认无需人工确认" 或 "人工确认完成" → **已确认** / **Confirmed**
     - 如果任务需要人工验证但尚未确认 → **待确认** / **Pending Confirmation**

   - **图标选择** / Icon selection:

     | 确认状态 / Confirmation Status | 图标 / Icon | 示例 / Example |
     |-------------------------------|------------|---------------|
     | 已确认 (AI 确认) / Confirmed | ✅ | ✅_00015_10101_101_bug_xxx_done.md |
     | 待确认 (需人工) / Pending | 🔶 | 🔶_00017_10102_103_bug_xxx_done.md |

2. **重构任务** (编号 20101–29999):

   - 重构任务需要完整测试验证后才能归档
   - 始终使用 ✅ 图标
   - 如果验证失败，创建 🔶 前缀归档等待重新验证

3. **测试/质量任务** (编号 30101–39999):

   - 测试任务基于测试结果决定归档图标
   - 所有测试通过 → ✅ 图标
   - 有测试失败 → 🔶 图标

4. **功能/开发任务** (编号 00001–09999):

   - 始终使用 ✅ 图标，不适用其他规则

**注意**: Bug 任务、重构任务和测试任务如果需要人工确认则使用 🔶 图标。

**Note**: Bug, refactoring, and testing tasks use 🔶 icon if human confirmation is required.

---

### 7.5 检测后续任务并合并 / Detect Follow-up Task and Merge

在归档前，检测是否为已有归档的后续任务: / Before archiving, detect if this is a follow-up to an existing archive:

1. **提取任务编号**: 从当前提示词文件名提取任务编号 (如 `10103_bug_xxx.md` 中的 `10103`，或 `20101_refactor_xxx.md` 中的 `20101`)

   / Extract task number from current prompt filename (e.g., `10103` from `10103_bug_xxx.md`, or `20101` from `20101_refactor_xxx.md`)

2. **扫描归档目录**: 扫描 `promptsRec/archive/` 目录，查找文件名中包含相同编号的归档文件

   / Scan `promptsRec/archive/` directory for archived files containing the same task number

3. **自动匹配**: 如果找到匹配编号的归档文件 (如 `✅_00017_10003_bug_order_list_api_500_done.md` 或 `✅_00067_20101_201_refactor_service_layer_done.md`):

   / If a matching archived file is found:

   - 读取原始归档的完整内容 / Read the complete original archive content
   - 将当前提示词内容追加到原始归档的 `## 后续工作 / Follow-up Work` 部分 / Append current prompt content to original archive's `## Follow-up Work` section
   - 将合并后的内容写入原始归档文件 (保留原执行顺序号和类型编号) / Write merged content to the original archive file (preserve original sequence and type numbers)
   - 删除当前提示词文件 (而非归档) / Delete current prompt file (instead of archiving)

4. **无匹配**: 如果没有找到匹配编号的归档，执行标准归档流程 (Step 7)

   / If no matching archive found, proceed with standard archiving (Step 7)

**注意**: 后续任务合并适用于所有任务类型:
- Bug 修复 (10101–19999)
- 重构任务 (20101–29999)
- 测试任务 (30101–39999)

**Note**: Follow-up task merge applies to all task types:
- Bug fixes (10101–19999)
- Refactoring tasks (20101–29999)
- Testing tasks (30101–39999)

**合并格式示例 / Merge Format Example**:

```markdown
# BUG 订单列表 API 500

---

## 后续工作 / Follow-up Work

### [日期] 第二轮修复

[后续任务的完整内容]

## 验证更新 / Verification Update

[验证结果]
```

---

### 8. 移除锁文件 / Remove Lock

**关键**: 成功归档后，必须删除 .lock 文件以释放任务锁。 / **Critical**: After successful archive, must delete .lock file to release the task lock.

如果删除锁文件前执行失败，保留锁文件以便后续重试或人工干预。 / If execution fails before removing lock file, keep the lock file for retry or manual intervention.

---

## 失败处理 / Failure Handling

如果执行失败: / If execution fails:

- 不要重命名提示词 / do NOT rename the prompt
- 保留原始提示词文件 / keep the original prompt file
- 编写失败执行报告 / write a failure execution report

---

## 成功输出 / Success Output

提示词归档成功: / Prompt archived successfully:

```
✅_00003_00003_backend_implementation_done.md
```

或 Bug 任务:

```
✅_00015_10003_bug_tool_search_routing_done.md
```

---

## 失败输出 / Failure Output

提示词未归档。 / Prompt NOT archived.

原因: <失败原因> / Reason: <failure reason>

---

## 安全规则 / Guardrails

- 每次运行只执行一个提示词 / execute only one prompt per run
- 严禁删除提示词文件 / never delete prompt files
- 仅在完成后归档 / archive only after completion
- 所有文件必须使用 UTF-8 编码 / all files must use UTF-8 encoding

---

# Advanced Topics / 高级主题

## Executor Registry — 执行器注册表

### 目的

将执行器管理从硬编码规则改为注册表模式，便于扩展和维护。执行者只需查看注册表即可了解所有可用执行器的能力。

### 预定义执行器

| 执行器 | 能力范围 | 适用任务 |
|--------|----------|----------|
| Claude Code | 架构设计、重构、复杂Bug、测试、P0/P1 | P0/P1 Bug、重构、测试、架构相关、简化任务 |
| Codex | 后端实现、前端实现 | 普通功能实现、简单Bug修复 |
| Gemini | 前端UI设计 | 前端设计大改 |

### 执行器能力矩阵

| 能力 | Claude Code | Codex | Gemini |
|------|-------------|-------|--------|
| 架构设计 | ✅ | ❌ | ❌ |
| 重构 | ✅ | ⚠️ | ❌ |
| 后端实现 | ✅ | ✅ | ❌ |
| 前端实现 | ✅ | ✅ | ⚠️ |
| UI设计 | ⚠️ | ❌ | ✅ |
| 测试编写 | ✅ | ⚠️ | ❌ |

- ✅ = 主力能力
- ⚠️ = 可辅助

### 选择算法

给定任务时，按以下算法选择执行器：

```
输入: task_type, complexity, task_description

Step 1: 根据 task_type 确定候选执行器列表
  - 功能任务 (00001-09999) → [Claude Code, Codex]
  - Bug修复 (10101-19999) → [Claude Code, Codex]
  - 重构任务 (20101-29999) → [Claude Code]
  - 测试任务 (30101-39999) → [Claude Code]

Step 2: 根据 complexity 调整优先级
  - P0/P1 (高) → 强制 Claude Code
  - 涉及多文件/多模块 → 优先 Claude Code
  - 单文件/简单修复 (低) → 优先 Codex

Step 3: 根据 task_description 二次筛选
  - 包含"架构"、"重构"、"测试" → Claude Code
  - 包含"前端设计"、"UI" → 考虑 Gemini
  - 包含"API"、"数据库"、"后端" → 优先 Codex

Step 4: 返回最优执行器
```

### 执行器能力说明

**Claude Code**:
- 优势: 全栈能力，架构设计，复杂问题分析
- 工具: Read, Edit, Bash, Agent, Glob, Grep
- 适用复杂度: 中高
- 限制: 无

**Codex**:
- 优势: 专注实现，代码生成速度快
- 工具: 代码生成/修改
- 适用复杂度: 低中
- 限制: 不擅长架构设计

**Gemini**:
- 优势: UI设计，创意生成
- 工具: UI组件生成
- 适用复杂度: 中
- 限制: 不擅长后端逻辑

### 注册表扩展指南

新增执行器时，需在注册表中添加：

```markdown
| 新执行器名 | 能力范围 | 适用任务 |
|------------|----------|----------|
| ... | ... | ... |
```

并更新能力矩阵。
