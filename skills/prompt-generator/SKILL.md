# 提示词生成器 / Prompt Generator Skill

## 目的 / Purpose

本技能使 AI 代理（特别是 Gemini）能够生成符合项目 AI 驱动开发工作流的标准化开发提示词。

This skill enables AI agents (especially Gemini) to generate standardized development prompts that comply with the project's AI-driven development workflow.

生成的提示词必须遵循项目的提示词规范，并且必须可以直接在 `promptsRec/` 目录中使用。

The generated prompts must follow the project's prompt specification and must be directly usable inside the `promptsRec/` directory.

本技能确保在调试、功能开发或 UI 改进过程中创建的提示词保持与项目标准一致。

This skill ensures that prompts created during debugging, feature development, or UI improvements remain consistent with project standards.

---

# 何时使用此技能 / When to Use This Skill

在以下情况下使用此技能：

Use this skill when:

- 需要实现新功能 / A new feature needs to be implemented
- 在浏览器调试中发现 bug / A bug is discovered during browser debugging
- 需要改进 UI / A UI improvement is required
- 发现工作流改进需求 / A workflow improvement is identified
- 需要扩展后端能力 / A backend capability must be extended
- 需要调查运行时问题 / Runtime issues must be investigated

典型场景包括：

Typical scenarios include:

- 在 Trae 浏览器中发现调试问题 / debugging issues discovered in Trae browser
- 改进前端 UX / improving frontend UX
- 实现新的后端工作流逻辑 / implementing new backend workflow logic
- 稳定现有功能 / stabilizing existing functionality

---

# 提示词命名规则 / Prompt Naming Rules

提示词编号是严格定义的。

Prompt numbering is strictly defined.

功能提示词：

Feature prompts:

000–099

Bug 修复提示词：

Bug fix prompts:

100–199

示例：

Examples:

017_order_list_ui_migration.md
021_structured_message_preview_ui.md
101_bug_tool_search_request_routing.md
103_bug_order_list_api_500.md

---

# 提示词输出格式 / Prompt Output Format

输出必须始终包含：

The output must always contain:

1. 文件名 / File name
2. 执行模型 / Executor model
3. 完整的提示词内容 / Full prompt content

示例输出格式：

Example output format:

文件名：promptsRec/017_order_list_ui_migration.md
执行模型：Gemini

文件名：promptsRec/017_order_list_ui_migration.md
执行模型：Gemini

Then output the full prompt content.

---

# 提示词头部格式 / Prompt Header Format

每个生成的提示词必须以以下头部开头：

Every generated prompt must begin with the following header:

Primary Executor: <Agent>
Task Type: <Task Category>
Stage: <Stage Number>
Goal: <Short Description>
Execution: RUNPROMPT

示例：

Example:

Primary Executor: Gemini
Task Type: Frontend Implementation
Stage: 017
Goal: Migrate order list page UI to Mist component style
Execution: RUNPROMPT

---

# 必需提示词章节 / Required Prompt Sections

每个生成的提示词必须包含以下章节：

Every generated prompt must contain the following sections:

Context / 上下文
Required References / 必需参考
Core Task / 核心任务
Required Work / 必需工作
Constraints / 约束条件
Completion Criteria / 完成标准

这些章节必须出现在提示词中。

These sections must appear in the prompt.

---

# 问题分析要求 / Problem Analysis Requirement

在生成提示词之前，AI 必须：

Before generating a prompt, the AI must:

1. 分析问题 / Analyze the problem
2. 确定任务类别： / Determine the task category:
   - 功能开发 / Feature Development
   - Bug 修复 / Bug Fix
   - UI 改进 / UI Improvement
   - 架构改进 / Architecture Improvement
3. 选择正确的编号范围 / Select the correct numbering range
4. 确定正确的执行器 / Determine the correct executor

执行器规则：

Executor rules:

Gemini → 前端任务 / frontend tasks
Codex → 后端任务 / backend tasks
Claude Code → 架构任务 / architecture tasks

---

# Bug 提示词规则 / Bug Prompt Rules

如果问题是 bug：

If the problem is a bug:

- 提示词编号必须在 100–199 范围内 / The prompt number must be in the 100–199 range
- 修改前必须进行调查 / Investigation must occur before modification
- 提示词必须指示代理检查真实代码库 / The prompt must instruct the agent to inspect the real codebase
- 提示词必须指示代理检查真实数据库架构 / The prompt must instruct the agent to inspect the real database schema

提示词不得假设：

The prompt must NOT assume:

- 数据库字段名 / Database field names
- 后端 API 结构 / Backend API structure
- 工作流状态 / Workflow states

---

# 功能提示词规则 / Feature Prompt Rules

如果任务是功能：

If the task is a feature:

- 提示词编号必须在 000–099 范围内 / The prompt number must be in the 000–099 range
- 提示词必须与现有架构集成 / The prompt must integrate with existing architecture
- 提示词不得重新设计稳定的子系统 / The prompt must not redesign stable subsystems

---

# 约束条件 / Constraints

AI 不得：

The AI must NOT:

- 生成不完整的提示词 / Generate partial prompts
- 跳过必需章节 / Skip required sections
- 无正当理由重新设计稳定架构 / Redesign stable architecture without justification
- 假设数据库架构 / Assume database schema
- 不检查就假设后端 API / Assume backend APIs without inspection
- 生成超出编号规则的提示词 / Generate prompts outside numbering rules

---

# 完成标准 / Completion Criteria

生成的提示词只有在以下情况下才被视为有效：

A generated prompt is considered valid only if:

1. 遵循提示词格式 / It follows the prompt format
2. 遵守编号规则 / It respects numbering rules
3. 包含所有必需章节 / It contains all required sections
4. 可以由 RUNPROMPT 直接执行 / It can be executed directly by RUNPROMPT
