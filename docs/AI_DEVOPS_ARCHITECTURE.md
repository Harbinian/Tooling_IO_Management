# AI DevOps 架构 / AI DevOps Architecture

---

## 概述 / Overview

本项目使用提示词驱动开发流水线，结合 AI 技能和 Agent 来管理开发、验证、发布和 bug 修复。 / This project uses a Prompt-Driven Development Pipeline combined with AI Skills and Agents to manage development, verification, release, and bug fixing.

系统实现持续的 AI 辅助工程循环，包括: / The system enables a continuous AI-assisted engineering loop including:

- 设计 / design
- 实现 / implementation
- 验证 / verification
- 发布 / release
- 事件捕获 / incident capture
- Bug 分类 / bug triage
- 自动化修复任务 / automated repair tasks

所有任务状态使用文件表示，而非外部任务管理系统。 / All task states are represented using files instead of an external task management system.

---

## 系统层级 / System Layers

架构由四个层级组成。 / The architecture consists of four layers.

1. 任务层 / Task Layer
2. 执行层 / Execution Layer
3. 验证层 / Verification Layer
4. 事件与演进层 / Incident and Evolution Layer

---

## 1. 任务层 / 1 Task Layer

任务层定义需要完成的工作。 / The task layer defines what work needs to be done.

所有开发任务都以 Markdown 提示词文件的形式存在，位于: / All development tasks exist as Markdown prompt files located in:

`promptsRec/`

每个提示词文件代表一个工程任务。 / Each prompt file represents a single engineering task.

示例任务: / Example tasks:

```
001_architecture_phase.md
002_technical_design.md
003_backend_implementation.md
004_backend_review.md
005_frontend_design.md
006_frontend_implementation.md
```

与 bug 相关的任务在生命周期后期生成: / Bug-related tasks are generated later in the lifecycle:

```
101_bug_api_error.md
102_bug_missing_field.md
```

在本系统中: / In this system:

提示词文件 = 任务定义 / Prompt file = Task definition

---

## 2. 执行层 / 2 Execution Layer

执行层负责运行任务和协调 Agent。 / The execution layer is responsible for running tasks and coordinating agents.

核心技能: / Core skills:

```
skills/prompt-task-runner
skills/pipeline-dashboard
skills/release-precheck
skills/bug-triage
skills/incident-capture
```

### RUNPROMPT

技能位置: / Skill location:

`skills/prompt-task-runner`

目的: / Purpose:

执行提示词任务。 / Execute prompt tasks.

职责: / Responsibilities:

- 发现待处理的提示词 / discover pending prompts
- 创建 .lock 文件 / create .lock file
- 执行提示词任务 / execute the prompt task
- 生成执行报告 / generate execution report
- 归档提示词 / archive the prompt

归档命名格式: / Archive naming format:

`✅_序列号_原始提示词_摘要.md`

示例: / Example:

```
003_backend_implementation.md
变为 / becomes

✅_00003_003_backend_implementation_backend_done.md
```

### 流水线仪表盘 / Pipeline Dashboard

技能位置: / Skill location:

`skills/pipeline-dashboard`

目的: / Purpose:

提供流水线状态概览。 / Provide an overview of pipeline status.

功能: / Functions:

- 统计已完成任务 / count completed tasks
- 检测运行中任务 / detect running tasks
- 列出待处理提示词 / list pending prompts
- 确定下一个任务 / determine next task
- 确定负责执行者 / determine responsible executor

此技能不执行任务。 / This skill does NOT execute tasks.

---

## 3. 验证层 / 3 Verification Layer

验证确保系统在发布前内部一致。 / Verification ensures that the system is internally consistent before release.

主要技能: / Primary skill:

`skills/release-precheck`

### 发布预检 / Release Precheck

目的: / Purpose:

执行最终系统一致性验证。 / Perform final system consistency verification.

检查项包括: / Checks include:

- API 规范一致性 / API specification consistency
- 数据库 Schema 对齐 / database schema alignment
- 状态机验证 / state machine validation
- 审计日志覆盖 / audit logging coverage
- 通知持久化 / notification persistence
- 前端 / API 字段映射 / frontend / API field mapping

输出: / Output:

`docs/RELEASE_PRECHECK_REPORT.md`

严重性级别: / Severity levels:

- 严重 / Critical
- 高 / High
- 中 / Medium
- 低 / Low

只有解决严重和高问题后，系统才能发布。 / Only when Critical and High issues are resolved can the system be released.

---

## 4. 事件与演进层 / 4 Incident and Evolution Layer

部署后，可能发生运行时事件。 / After deployment, runtime incidents may occur.

两个技能支持持续改进。 / Two skills support continuous improvement.

### 事件捕获 / Incident Capture

技能位置: / Skill location:

`skills/incident-capture`

目的: / Purpose:

将运行时错误转换为结构化事件报告。 / Convert runtime errors into structured incident reports.

输入来源包括: / Input sources include:

- 日志 / logs
- 堆栈跟踪 / stack traces
- 用户 bug 报告 / user bug reports
- 后端异常 / backend exceptions
- 前端控制台错误 / frontend console errors

输出文件位置: / Output file location:

`incidents/`

示例文件: / Example file:

`INCIDENT_20260312_submit_error.md`

事件记录包括: / Incident records include:

- 事件摘要 / incident summary
- 受影响模块 / affected module
- 严重性 / severity
- 错误消息 / error message
- 堆栈跟踪 / stack trace
- 观察到的行为 / observed behavior
- 预期行为 / expected behavior
- 可能根本原因 / possible root cause

### Bug 分类 / Bug Triage

技能位置: / Skill location:

`skills/bug-triage`

目的: / Purpose:

分析事件并生成 bug 修复提示词。 / Analyze incidents and generate bug-fix prompts.

职责: / Responsibilities:

- 分类严重性 / classify severity
- 识别受影响的系统区域 / identify affected system area
- 确定负责执行者 / determine responsible executor
- 生成 bug 修复提示词 / generate bug-fix prompt

生成的提示词位置: / Generated prompt location:

`promptsRec/`

示例: / Example:

`101_bug_missing_column.md`

执行者路由规则: / Executor routing rules:

| 问题类型 / Issue Type | 执行者 / Route to |
|---------------------|-----------------|
| 架构或系统级问题 / Architecture or system-level issue | Claude Code |
| 后端 / 数据库 / API 问题 / Backend / Database / API issue | Codex |
| 前端设计问题 / Frontend design issue | Gemini |
| 前端实现问题 / Frontend implementation issue | Codex |

---

## Agent 角色 / Agent Roles

三个 AI Agent 在流水线中协作。 / Three AI agents collaborate within the pipeline.

### Claude Code

主要职责: / Primary responsibilities:

- 架构设计 / architecture design
- 技术文档 / technical documentation
- 系统审查 / system review
- 流水线协调 / pipeline coordination
- 发布验证 / release verification
- Bug 分类 / bug triage

角色: / Role:

架构师 / 审查者 / 协调者 / Architect / Reviewer / Coordinator

### Codex

主要职责: / Primary responsibilities:

- 后端实现 / backend implementation
- 数据库修复 / database fixes
- API 开发 / API development
- 前端实现 / frontend implementation
- Bug 修复 / bug fixes

角色: / Role:

实现工程师 / Implementation Engineer

### Gemini

主要职责: / Primary responsibilities:

- 前端设计 / frontend design
- UI 布局 / UI layout
- 交互设计 / interaction design
- 字段映射可视化 / field mapping visualization

角色: / Role:

前端设计师 / Frontend Designer

---

## 任务状态管理 / Task State Management

任务状态通过文件命名约定表示。 / Task state is represented through file naming conventions.

待处理任务: / Pending task:

`003_backend_implementation.md`

运行中任务: / Running task:

`003_backend_implementation.lock`

已完成任务: / Completed task:

`✅_00003_003_backend_implementation_backend_done.md`

这种方法提供了轻量级且可审计的状态机，无需外部任务数据库。 / This approach provides a lightweight and auditable state machine without requiring an external task database.

---

## 持续 AI 开发循环 / Continuous AI Development Loop

系统实现完整的 AI 驱动生命周期。 / The system enables a full AI-driven lifecycle.

设计 / Design
↓
提示词生成 / Prompt Generation
↓
RUNPROMPT 执行 / RUNPROMPT Execution
↓
归档 / Archive
↓
发布预检 / Release Precheck
↓
部署 / Deployment
↓
运行时 / Runtime
↓
事件捕获 / Incident Capture
↓
Bug 分类 / Bug Triage
↓
Bug 修复提示词 / Bug Fix Prompt
↓
RUNPROMPT
↓
发布验证 / Release Verification

此循环允许系统持续演进，同时保持对开发任务的结构化控制。 / This loop allows the system to continuously evolve while maintaining structured control over development tasks.

---

## 关键原则 / Key Principles

1. 提示词代表工程任务。 / Prompts represent engineering tasks.
2. 技能代表可重用的系统能力。 / Skills represent reusable system capabilities.
3. Agent 专精于不同的工程角色。 / Agents specialize in different engineering roles.
4. 文件命名约定代表流水线状态。 / File naming conventions represent pipeline state.
5. 所有执行都可通过执行报告追溯。 / All execution is traceable through execution reports.

---

## 结果 / Result

此架构形成了一个提示词驱动的 AI DevOps 系统，具备以下能力: / This architecture forms a Prompt-Driven AI DevOps System capable of:

- 结构化开发 / structured development
- 受控发布 / controlled releases
- 自动化 Bug 分类 / automated bug triage
- 持续改进 / continuous improvement
- AI 辅助工程工作流 / AI-assisted engineering workflows
