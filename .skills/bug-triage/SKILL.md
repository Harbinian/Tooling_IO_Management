# Bug 分类 / BUG TRIAGE

---

## 目的 / Purpose

分析新报告的 bug，分类其严重性和所有权，为正确的执行者生成结构化的后续提示词。 / Analyze a newly reported bug, classify its severity and ownership, and generate a structured follow-up prompt for the correct executor.

此技能不直接修复 bug。 / This skill does NOT directly fix the bug.
它为流水线创建 bug 任务。 / It creates a bug task for the pipeline.

---

## 输入 / Inputs

Bug 报告可能来自: / A bug report may come from:

- 用户描述 / user description
- 错误日志 / error logs
- 堆栈跟踪 / stack traces
- 截图 / screenshots
- 发布预检失败项 / failed release precheck items
- 运行时异常 / runtime exceptions
- 数据库错误 / database errors
- 前端交互问题 / frontend interaction issues

---

## 分类目标 / Classification Goals

对于每个 bug，确定: / For every bug, determine:

1. Bug 摘要 / Bug summary
2. 影响区域 / Affected area
3. 严重性 / Severity
4. 根本原因方向 / Root-cause direction
5. 负责执行者 / Responsible executor
6. 推荐的下一个提示词文件 / Recommended next prompt file

---

## 影响区域分类 / Affected Area Classification

将 bug 分类到以下区域之一: / Classify the bug into one of these areas:

- 架构 / Architecture
- 后端 / Backend
- 数据库 / Database
- API
- 前端 / Frontend
- 集成 / Integration
- 发布/部署 / Release / Deployment

---

## 严重性级别 / Severity Levels

使用以下级别: / Use these levels:

- 严重 / Critical
- 高 / High
- 中 / Medium
- 低 / Low

指导: / Guidance:

严重 / Critical:
- 系统无法运行 / system cannot run
- 数据损坏风险 / data corruption risk
- 订单工作流受阻 / order workflow blocked
- 缺少数据库字段导致运行时失败 / missing database fields causing runtime failures

高 / High:
- 主要功能损坏 / major feature broken
- API 不可用 / API unusable
- 通知持久化损坏 / notification persistence broken
- 前端无法完成核心工作流 / frontend cannot complete core workflow

中 / Medium:
- 部分工作流问题 / partial workflow issue
- 显示不正确 / incorrect display
- 非阻塞性集成问题 / non-blocking integration issue

低 / Low:
- 文本问题 / text issue
- 小型 UX 问题 / minor UX issue
- 非关键格式问题 / non-critical formatting issue

---

## 负责执行者规则 / Responsible Executor Rules

| 任务类型 / Task Type | 负责执行者 / Responsible Executor |
|---------------------|-------------------------------|
| 架构 / 审查 / 系统级不一致 / Architecture / Review / System-level inconsistency | Claude Code |
| 后端 / 数据库 / API / 集成修复 / Backend / Database / API / Integration fix | Codex |
| 前端设计问题 / Frontend design issue | Gemini |
| 前端实现修复 / Frontend implementation fix | Codex |

如不确定: / If uncertain:
→ Claude Code

---

## 输出文件 / Output Files

生成两个文件。 / Generate two files.

### 1. Bug 分类报告 / Bug triage report

创建: / Create:

`docs/BUG_TRIAGE_REPORT.md`

报告必须包含: / The report must include:

- Bug 摘要 / bug summary
- 影响区域 / affected area
- 严重性 / severity
- 观察到的症状 / observed symptoms
- 可能的根本原因 / possible root cause
- 推荐的执行者 / recommended executor
- 推荐的下一个动作 / recommended next action

### 2. Bug 提示词 / Bug prompt

在以下位置创建新的提示词文件: / Create a new prompt file in:

`promptsRec/active/`

文件名格式（必须使用5位编号）: / Filename format (must use 5-digit numbering):

`10101_bug_<简短名称>.md`

如果 10101 已存在，递增到下一个可用编号。 / If 10101 already exists, increment to the next available number.

示例: / Examples:

```
10101_bug_missing_field.md
10102_bug_api_mismatch.md
10103_bug_frontend_submit_fail.md
```

---

## Bug 提示词格式 / Bug Prompt Format

生成的提示词必须包含标准头: / The generated prompt must include the standard header:

```
Primary Executor: <Claude Code | Codex | Gemini>
Task Type: Bug Fix
Priority: <P0 | P1 | P2>
Stage: <5-digit Bug Number>
Goal: <one-line bug fix objective>
Dependencies: <"None" or list of prompt numbers that must complete first>
Execution: RUNPROMPT
```

示例:

```
Primary Executor: Codex
Task Type: Bug Fix
Priority: P1
Stage: 10101
Goal: Fix order API parameter mismatch
Dependencies: None
Execution: RUNPROMPT
```

然后包含: / Then include:

- 上下文 / Context
- 观察到的 / Observed issue
- 需要调查的内容 / Required investigation
- 需要修复的范围 / Required fix scope
- 输出要求 / Output requirements
- 完成标准 / Completion criteria

---

## Bug 提示词内容规则 / Bug Prompt Content Rules

提示词必须: / The prompt must:

- 具体 / be specific
- 识别目标区域 / identify the target area
- 除非必要，否则避免大规模重新设计 / avoid broad redesign unless necessary
- 保留现有工作的逻辑 / preserve existing working logic
- 清楚地描述预期的修复结果 / describe expected fix outcome clearly

---

## 示例路由 / Example Routing

| 问题 / Issue | 路由到 / Route to |
|-------------|-----------------|
| 数据库字段不匹配 / Database field mismatch | Codex |
| API 请求/响应不匹配 / API request / response mismatch | Codex |
| 实现后的架构不一致 / Architecture inconsistency after implementation | Claude Code |
| 前端页面交互 bug / Frontend page interaction bug | Codex |
| 前端流程/UX 重新设计问题 / Frontend flow / UX redesign issue | Gemini |

---

## Bug 工作流集成 / Bug Workflow Integration

Bug 修复任务（10101-19999）必须遵循 `.claude/rules/02_debug.md` 中的 8D 问题解决协议。

### 强制审核机制

Bug 修复提示词中 D3/D5/D6 阶段完成后**必须**触发 reviewer 评分审核：

- D3 完成 → 全部维度达标后才能继续 D4
- D5 完成 → 全部维度达标后才能继续 D6
- D6 完成 → 全部维度达标后才能继续 D7

**各维度最低门槛**：

| 维度 | 满分 | 最低门槛 |
|------|------|----------|
| root_cause_depth | 0.3 | ≥0.24 |
| solution_completeness | 0.3 | ≥0.24 |
| code_quality | 0.2 | ≥0.16 |
| test_coverage | 0.2 | =0.20（必须满分） |

### 升级检查 / Escalation Check

报告新 bug 时: / When a new bug is reported:

1. 在 `promptsRec/active/` 中扫描匹配 `*_bug_*.md` 的现有 bug 提示词 / Scan existing bug prompts in `promptsRec/active/` for files matching `*_bug_*.md`
2. 确定新问题是否是现有 bug 的子问题 / Determine if the new issue is a sub-issue of an existing bug

### 升级条件 / Escalation Conditions

仅当满足所有条件时，才允许创建新的 bug 提示词: / A NEW bug prompt is allowed ONLY if ALL conditions are met:

1. 根本原因与任何现有 bug 无关 / The root cause is unrelated to any existing bug
2. 问题属于不同的子系统 / The issue belongs to a different subsystem
3. 在现有 bug 范围内修复会导致架构副作用 / Fixing it inside the existing bug scope would cause architectural side effects

否则: / Otherwise:
- 记录为子问题 / Record as sub-issue
- 不要创建新的提示词 / Do NOT create a new prompt

---

## 约束 / Constraints

此技能严禁: / This skill must NOT:

- 直接修改后端代码 / directly modify backend code
- 直接修改前端代码 / directly modify frontend code
- 直接重命名提示词 / directly rename prompts
- 直接执行 bug 修复 / directly execute bug fixes
- 为属于现有 bug 的子问题创建新的 bug 提示词 / create new bug prompts for sub-issues that belong to existing bugs

它仅分析并生成下一个 bug 修复任务。 / It only analyzes and generates the next bug-fix task.

---

## 完成标准 / Completion Criteria

当以下条件满足时，技能完成: / The skill is complete when:

1. `docs/BUG_TRIAGE_REPORT.md` 存在 / docs/BUG_TRIAGE_REPORT.md exists
2. `promptsRec/active/` 下存在新的 bug 提示词 / a new bug prompt exists under promptsRec/active/
3. 提示词包含 Primary Executor / the prompt includes Primary Executor
4. Bug 已分类严重性和所有权 / the bug is classified with severity and ownership
5. 提示词具体清晰，包含所需的修复范围和输出要求 / the prompt is specific and clear with required fix scope and output requirements.
