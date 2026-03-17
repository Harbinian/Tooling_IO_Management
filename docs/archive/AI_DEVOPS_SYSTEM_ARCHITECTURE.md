# AI DevOps 系统架构 / AI DevOps System Architecture

## 概述 / Overview

本项目使用 AI 驱动的开发工作流，多个 AI 代理协作进行系统设计、实现、测试和维护。

This project uses an AI-driven development workflow where multiple AI agents collaborate to design, implement, test, and maintain the system.

开发管道围绕**基于提示词的任务执行**和一组专门的 AI 技能构建。

The development pipeline is built around **prompt-based task execution** and a set of specialized AI skills.

目标是创建一个结构化的 AI DevOps 环境，其中：

The goal is to create a structured AI DevOps environment where:

- 开发任务标准化 / development tasks are standardized
- 执行可追踪 / execution is traceable
- 调试自动化 / debugging is automated
- AI 代理通过提示词协作 / AI agents collaborate through prompts

---

# 核心概念 / Core Concepts

## 提示词驱动开发 / Prompt-Driven Development

所有开发工作都表示为存储在以下位置的提示词：

All development work is represented as prompts stored in:

promptsRec/

每个提示词代表一个开发任务。

Each prompt represents a development task.

示例：

Example:

017_order_list_ui_migration.md

提示词由 RUNPROMPT 系统执行。

Prompts are executed by the RUNPROMPT system.

---

## 任务生命周期 / Task Lifecycle

提示词经历以下生命周期。

A prompt goes through the following lifecycle.

待处理 / Pending

↓

运行中（创建 .lock 文件） / Running (.lock file created)

↓

已完成（使用 ✅_ 前缀归档） / Completed (archived with ✅_ prefix)

示例：

Example:

017_order_list_ui_migration.md
↓

017_order_list_ui_migration.lock
↓

✅_00012_017_order_list_ui_migration.md

---

# AI 代理 / AI Agents

系统使用多个 AI 代理。

The system uses multiple AI agents.

### Claude Code

职责：

Responsibilities:

- 系统架构 / system architecture
- 技术规划 / technical planning
- 设计审查 / design review
- 发布预检 / release precheck

---

### Codex

职责：

Responsibilities:

- 后端实现 / backend implementation
- 数据库集成 / database integration
- API 开发 / API development
- 后端调试 / backend debugging

---

### Gemini

职责：

Responsibilities:

- 前端设计 / frontend design
- UI 组件 / UI components
- 交互设计 / interaction design
- 浏览器调试分析 / browser debugging analysis

---

# 技能系统 / Skill System

AI DevOps 环境围绕模块化技能构建。

The AI DevOps environment is built around modular skills.

每个技能在开发管道中扮演特定角色。

Each skill performs a specific role in the development pipeline.

---

## 核心技能 / Core Skills

### RUNPROMPT

执行提示词任务。

Executes prompt task.

工作流：

Workflow:

提示词 → 锁文件 → 实现 → 归档。 / Prompt → lock file → implementation → archive.

---

### Pipeline Dashboard

监控管道。

Monitors the pipeline.

职责：

Responsibilities:

- 扫描 promptsRec/ / scan promptsRec/
- 跟踪任务状态 / track task status
- 推荐下一个任务 / recommend next task

---

### Dev Inspector

观察运行时行为。

Observes runtime behavior.

职责：

Responsibilities:

- 检查浏览器控制台错误 / inspect browser console errors
- 检查 API 失败 / inspect API failures
- 分类问题 / classify problems
- 触发任务生成 / trigger task generation

---

### Auto Task Generator

将检测到的问题转换为开发提示词。

Transforms detected issues into development prompts.

职责：

Responsibilities:

- 分配提示词编号 / assign prompt number
- 确定执行器 / determine executor
- 生成标准化提示词 / generate standardized prompts

---

### Prompt Generator

创建符合项目开发标准的提示词。

Creates prompts that comply with project development standards.

确保提示词格式的一致性。

Ensures consistency of prompt format.

---

### Self-Healing Dev Loop

协调自动化开发。

Coordinates automated development.

工作流：

Workflow:

检测到问题 → 生成提示词 → 执行提示词 → 应用修复。 / issue detected → prompt generated → prompt executed → fix applied.

---

# 开发工作流 / Development Workflow

完整的开发循环：

The complete development loop:

浏览器调试 / Browser debugging

↓

Dev Inspector 分析问题 / Dev Inspector analyzes issue

↓

Auto Task Generator 创建提示词 / Auto Task Generator creates prompt

↓

Pipeline Dashboard 调度任务 / Pipeline Dashboard schedules task

↓

RUNPROMPT 执行任务 / RUNPROMPT executes task

↓

Codex / Gemini 实现解决方案 / Codex / Gemini implement solution

↓

提示词归档 / Prompt archived

---

## ⚠️ 已废弃 / DEPRECATED

**编号规则已迁移至 `.claude/rules/70_prompt_task_convention.md`**

旧的3位编号体系（000-099功能, 101-199 Bug, 201-299重构, 301-399测试）已升级为5位编号体系。所有已归档文件已按新规则重命名。

请勿在本文件中修改编号规则，修改请至上述规则文件。

---

# Bug 工作流 / Bug Workflow

Bug 提示词遵循严格规则。

Bug prompts follow strict rules.

编号范围：

Number range:

100–199

模式：

Pattern:

*_bug_*.md

示例：

Example:

101_bug_tool_search_request_routing.md

---

## 一个 Bug 一个提示词规则 / One-Bug-One-Prompt Rule

每个 bug 必须对应一个提示词。

Each bug must correspond to a single prompt.

后续修复必须引用相同的 bug 工作流。

Follow-up fixes must reference the same bug workflow.

---

# 功能工作流 / Feature Workflow

功能提示词使用范围：

Feature prompts use range:

000–099

示例：

Examples:

017_order_list_ui_migration.md
021_structured_message_preview_ui.md

---

# 管道调度 / Pipeline Scheduling

管道使用简单的调度逻辑。

The pipeline uses simple scheduling logic.

优先级：

Priority:

1. 运行中的任务阻止新执行 / running tasks block new execution
2. Bug 提示词具有最高优先级 / bug prompts have highest priority
3. 功能提示词按升序执行 / feature prompts execute in ascending order

---

# 系统优势 / System Benefits

AI DevOps 系统提供：

The AI DevOps system provides:

- 结构化开发工作流 / structured development workflow
- 可复现的 AI 执行 / reproducible AI execution
- 自动化调试支持 / automated debugging support
- 可追踪的任务历史 / traceable task history
- 多代理协作 / multi-agent collaboration

---

# 长期愿景 / Long-Term Vision

系统旨在演变为**自愈 AI 开发环境**，其中：

The system aims to evolve into a **self-healing AI development environment** where:

- 运行时问题自动生成任务 / runtime issues automatically generate tasks
- AI 代理自主修复问题 / AI agents fix problems autonomously
- 开发管道保持稳定和可观察 / development pipelines remain stable and observable

此架构代表了一种新的协作式 AI 辅助软件开发模型。

This architecture represents a new model of collaborative AI-assisted software development.
