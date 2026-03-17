# AI 系统说明 / README_AI_SYSTEM

---

## 目的 / Purpose

本文档解释本项目中使用的 AI 驱动开发系统。 / This document explains the AI-driven development system used in this project.

本项目使用**提示词驱动工程流水线**结合 AI 技能和多个 AI Agent。 / The project uses a **Prompt-Driven Engineering Pipeline** combined with AI Skills and multiple AI agents.

目标是支持结构化开发、受控发布和持续的 bug 解决。 / The goal is to support structured development, controlled releases, and continuous bug resolution.

---

# 核心概念 / Core Concepts

## 提示词 / Prompt

提示词文件代表**单个工程任务**。 / A prompt file represents a **single engineering task**.

位置: / Location:

`promptsRec/`

示例文件: / Example files:

```
001_architecture_phase.md
002_technical_design.md
003_backend_implementation.md
004_backend_review.md
005_frontend_design.md
006_frontend_implementation.md
```

Bug 任务也会出现在这里: / Bug tasks will also appear here:

`101_bug_missing_column.md`

提示词 = 任务。 / Prompt = Task.

---

## 技能 / Skill

技能是 AI Agent 使用的可重用能力。 / Skills are reusable capabilities used by the AI agents.

位置: / Location:

`skills/`

核心技能包括: / Core skills include:

```
prompt-task-runner
pipeline-dashboard
release-precheck
incident-monitor
incident-capture
bug-triage
```

技能 = 系统能力。 / Skill = System capability.

---

## Agent / Agents

三个 AI Agent 在系统中协作。 / Three AI agents collaborate in the system.

**Claude Code** / Claude Code
负责架构、文档、系统审查和流水线协调。 / Responsible for architecture, documentation, system review, and pipeline coordination.

**Codex** / Codex
负责后端实现、数据库修复、API 实现和 bug 修复。 / Responsible for backend implementation, database fixes, API implementation, and bug fixes.

**Gemini** / Gemini
负责前端设计和交互设计。 / Responsible for frontend design and interaction design.

---

# 核心工作流 / Core Workflow

标准开发流水线是: / The standard development pipeline is:

```
pipeline-dashboard
→ 确定下一个任务 / determine next task

RUNPROMPT
→ 执行任务 / execute the task

release-precheck
→ 验证系统一致性 / verify system consistency
```

发布后，系统继续进行运行时监控。 / After release the system continues with runtime monitoring.

---

# 提示词执行 / Prompt Execution

提示词执行使用 RUNPROMPT 命令执行。 / Prompt execution is performed using the RUNPROMPT command.

示例: / Example:

`RUNPROMPT promptsRec/003_backend_implementation.md`

RUNPROMPT 将: / RUNPROMPT will:

1. 发现待处理的提示词 / discover pending prompt
2. 创建锁文件 / create lock file
3. 执行任务 / execute the task
4. 编写执行报告 / write execution report
5. 归档提示词 / archive the prompt

归档的提示词重命名为: / Archived prompts are renamed as:

`✅_00003_003_backend_implementation_backend_done.md`

---

# 流水线监控 / Pipeline Monitoring

使用流水线仪表盘技能检查系统进度。 / Use the pipeline dashboard skill to inspect system progress.

pipeline-dashboard 将显示: / pipeline-dashboard will show:

- 已完成任务 / Completed tasks
- 运行中任务 / Running tasks
- 待处理任务 / Pending tasks
- 下一个推荐任务 / Next recommended task

---

# 发布验证 / Release Verification

发布前，运行: / Before release, run:

`release-precheck`

此技能验证: / This skill verifies:

- API 一致性 / API consistency
- 数据库 Schema 对齐 / database schema alignment
- 状态机有效性 / state machine validity
- 审计日志覆盖 / audit logging coverage
- 通知持久化 / notification persistence
- 前端和 API 映射 / frontend and API mapping

结果写入: / The result is written to:

`docs/RELEASE_PRECHECK_REPORT.md`

---

# 事件处理 / Incident Handling

运行时问题使用三个技能处理: / Runtime issues are processed using three skills:

```
incident-monitor
incident-capture
bug-triage
```

这些技能允许系统将运行时错误转换为结构化修复任务。 / These skills allow the system to convert runtime errors into structured repair tasks.

流程记录在: / The flow is documented in:

`docs/INCIDENT_RESPONSE_FLOW.md`

---

# 关键原则 / Key Principles

提示词文件代表工程任务。 / Prompt files represent engineering tasks.

技能代表可重用的系统能力。 / Skills represent reusable system capabilities.

Agent 专精于不同的工程角色。 / Agents specialize in different engineering roles.

文件命名约定代表流水线状态。 / File naming conventions represent pipeline state.

所有执行都产生可追溯的报告。 / All executions produce reports for traceability.

---

# 总结 / Summary

本项目实现了**提示词驱动 AI DevOps 系统**，具备以下能力: / This project implements a **Prompt-Driven AI DevOps system** capable of:

- 结构化开发 / structured development
- 受控发布 / controlled releases
- 事件监控 / incident monitoring
- 自动化 Bug 分类 / automated bug triage
- 持续改进 / continuous improvement
