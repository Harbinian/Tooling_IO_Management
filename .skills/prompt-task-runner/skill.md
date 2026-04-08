---
name: prompt-task-runner
executor: Claude Code
auto_invoke: false
depends_on: []
triggers:
  - /prompt-task-runner
rules_ref:
  - .claude/rules/01_workflow.md
  - .claude/rules/02_debug.md
  - .claude/rules/05_task_convention.md
version: 1.0.0
---

# 运行提示词任务技能 / RUNPROMPT

**规则约束**: 本技能执行提示词时，根据任务类型调用相应规则：
- 功能任务 (00001-09999) → `.claude/rules/01_workflow.md` (ADP)
- Bug修复任务 (10101-19999) → `.claude/rules/02_debug.md` (8D)
- 重构任务 (20101-29999) → `.claude/rules/01_workflow.md` (ADP)
- 测试任务 (30101-39999) → `.claude/rules/01_workflow.md` (ADP)
- 编号约定 → `.claude/rules/05_task_convention.md`
- 生产环境紧急修复 → `.claude/rules/03_hotfix.md` (由 `self-healing-dev-loop` 处理)

命令触发: RUNPROMPT / Command Trigger: RUNPROMPT

---

## 目的 / Purpose

从 `promptsRec/active/` 目录执行一个提示词任务，并通过移动到 `promptsRec/archive/` 目录来标记完成。/ Execute one prompt task from the `promptsRec/active/` directory and mark completion by moving to `promptsRec/archive/` directory.

支持的执行者：/ Supported executors:
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

**所有执行者（包括 Claude Code）必须在执行任何任务前创建锁文件。** / **All executors (including Claude Code) must create lock files before executing any task.**

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

### 4. 任务类型识别 / Task Type Identification

**任务类型必须按编号区间判断，不按文件名片段。**

| 编号范围 | 任务类型 | 调用规则 |
|----------|---------|----------|
| 00001-09999 | 功能任务 | `.claude/rules/01_workflow.md` (ADP) |
| 10101-19999 | Bug修复任务 | `.claude/rules/02_debug.md` (8D) |
| 20101-29999 | 重构任务 | `.claude/rules/01_workflow.md` (ADP) |
| 30101-39999 | 测试任务 | `.claude/rules/01_workflow.md` (ADP) |

**执行器分配规则**（来自 `.claude/rules/05_task_convention.md`）：

| 任务类型 | 条件 | 执行者 |
|---------|------|--------|
| 重构任务 (20101-29999) | 始终 | Codex |
| 测试任务 (30101-39999) | 始终 | Claude Code |
| Bug 修复 (P0/P1 恶性) | 始终 | Claude Code |
| 简化任务 | 始终 | Claude Code |
| 功能任务 (00001-09999) | 前端设计大改 | Claude Code |
| 功能任务 (00001-09999) | 后端/前端实现 | Codex |
| Bug 修复 (普通) | 不涉及架构变更 | Codex |

**简化任务判定**（来自 `.claude/rules/05_task_convention.md`）：
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

### 5. 执行任务 / Execute Task

执行提示词中定义的工作。 / Execute the work defined in the prompt.

**规则调用方式**: 在执行任务前，先加载对应的规则文件（`.claude/rules/01_workflow.md`、`.claude/rules/02_debug.md` 或 `.claude/rules/03_hotfix.md`），按照规则中定义的流程执行。

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

### 5.1 依赖检查与中止规则 / Dependency Check and Abort Rules

**关键规则：如果任务在执行过程中发现依赖的任务未完成，必须立即中止并删除锁。**

在执行任何任务前，必须执行以下依赖检查：

#### 依赖检查流程 / Dependency Check Flow

1. **解析 Dependencies**: 从提示词 Header 中提取 `Dependencies` 字段
2. **检查归档状态**: 确认所有依赖任务已在 `promptsRec/archive/` 中归档
3. **检查执行状态**: 确认依赖任务不是当前正在执行的任务（带锁但未归档）

#### 依赖未完成的判定 / Dependency Not Met Criteria

满足以下任一条件视为"依赖未完成"：

| 条件 | 说明 |
|------|------|
| 依赖任务无归档文件 | `promptsRec/archive/` 中不存在对应的归档文件 |
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

## 执行操作
- [x] 停止任务执行
- [x] 删除 .lock 文件
- [ ] 归档提示词（未执行 - 依赖未满足）
```

---

### 5.2 文档同步检查 / Documentation Sync Check

执行任务时如发现文档与实现不一致，应立即同步更新文档：

1. **功能实现后**: 检查 PRD.md 是否反映最新功能
2. **API 实现后**: 检查 API_SPEC.md 是否与实现一致
3. **权限变更后**: 检查 RBAC 文档是否同步
4. **Schema 变更后**: 检查 DB_SCHEMA.md 和 column_names.py 是否同步

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

### 6.1 持续性 Bug 修复的日志规则 / Logging Rules for Persistent Bug Fixes

对于持续性 bug 修复：

1. **每次执行必记录**: 无论任务大小，每次 RUNPROMPT 执行后必须在 `logs/prompt_task_runs/` 创建运行报告

2. **自动追加**: 后续任务合并时，将运行报告内容自动追加到原始归档

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

| 任务类型 | 原始编号范围 | 类型编号范围 |
|---------|------------|------------|
| 功能任务 | 00001-09999 | 00001-09999 (自增) |
| Bug修复任务 | 10101-19999 | 10101-19999 (自增) |
| 重构任务 | 20101-29999 | 20101-29999 (自增) |
| 测试任务 | 30101-39999 | 30101-39999 (自增) |

**并发保护**: `.sequence` 文件使用 replace_all 模式更新，具有原子性。

**注意**: `.sequence` 文件是执行顺序号的唯一真实来源。严禁扫描 archive 目录来确定顺序号。

Archive format:

`✅_<执行顺序号>_<类型编号>_<原始编号>_<描述>_done.md`

**归档图标规则**（来自 `.claude/rules/05_task_convention.md`）：

| 任务类型 | 图标规则 |
|---------|---------|
| Bug 修复 (10101-19999) | D3/D5/D6 全部维度达标 → ✅；否则 → 🔶 |
| 重构任务 (20101-29999) | tester E2E 验证 pass → ✅；否则 → 🔶 |
| 测试任务 (30101-39999) | 所有 P0 测试通过 → ✅；否则 → 🔶 |
| 功能任务 (00001-09999) | 始终 → ✅ |

**禁止将 🔶 前缀文件归档** — 🔶 表示部分完成，不得进入 archive 目录。

---

### 7.5 后续任务合并 / Follow-up Task Merge

在归档前，检测是否为已有归档的后续任务：

1. **提取任务编号**: 从当前提示词文件名提取任务编号
2. **扫描归档目录**: 在 `promptsRec/archive/` 中查找包含相同编号的归档文件
3. **合并**: 如果找到匹配编号的归档，将当前提示词内容追加到原始归档的 `## 后续工作` 部分

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

---

## 安全规则 / Guardrails

- 每次运行只执行一个提示词 / execute only one prompt per run
- 严禁删除提示词文件 / never delete prompt files
- 仅在完成后归档 / archive only after completion
- 所有文件必须使用 UTF-8 编码 / all files must use UTF-8 encoding
- 所有规则调用必须引用 `.claude/rules/` 中的真源文件
