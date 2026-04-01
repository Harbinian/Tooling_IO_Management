# 自动任务生成器 / Auto Task Generator Skill

## 目的 / Purpose

本技能使 AI 代理能够自动将发现的问题、开发需求或改进机会转换为标准化的开发提示词。

This skill enables AI agents to automatically convert discovered problems, development needs, or improvement opportunities into standardized development prompts.

它作为 AI 开发管道的智能任务生成器运行。

It functions as an intelligent task generator for the AI development pipeline.

这允许 Gemini 在浏览器调试和系统探索期间表现得像 autonomous development assistant。

This allows Gemini to behave like an autonomous development assistant during browser debugging and system exploration.

---

# 核心能力 / Core Capability

此技能自动执行以下工作流：

This skill performs the following workflow automatically:

问题检测 / Problem Detection
↓
问题分析 / Problem Analysis
↓
任务分类 / Task Classification
↓
提示词编号分配 / Prompt Number Assignment
↓
提示词生成 / Prompt Generation
↓
可立即运行的 RUNPROMPT 任务 / Ready-to-run RUNPROMPT task

---

# 何时使用此技能 / When to Use This Skill

在以下情况下使用此技能：

Use this skill when:

- 观察到运行时错误 / A runtime error is observed
- 发现 UI 问题 / A UI issue is discovered
- 识别到缺失功能 / A missing feature is identified
- 发现后端工作流缺口 / A backend workflow gap is discovered
- 出现系统架构改进机会 / A system architecture improvement opportunity appears

典型触发条件包括：

Typical triggers include:

- 浏览器控制台错误 / Browser console errors
- API 失败 / API failures
- UI 不一致 / UI inconsistencies
- 缺失工作流步骤 / Missing workflow steps
- 意外系统行为 / Unexpected system behavior

---

# 任务分类 / Task Classification

系统必须将检测到的问题分类到以下类别之一。

The system must classify the detected issue into one of the following categories.

## 功能开发 / Feature Development

示例：

Examples:

- 新 UI 页面 / New UI page
- 新后端 API / New backend API
- 工作流扩展 / Workflow extension
- 仪表盘改进 / Dashboard improvement
- 组件迁移 / Component migration

提示词编号范围（必须使用5位）：

Prompt numbering range (must use 5 digits):

| 范围 | 类别 |
|------|------|
| 00001–09999 | 功能开发 / Feature Development |
| 10101–19999 | Bug 修复 / Bug Fix |
| 20101–29999 | 重构 / Refactoring |
| 30101–39999 | 测试 / Testing |

执行器：

Executor:

| 执行器 | 职责范围 |
|--------|---------|
| Gemini | 前端设计 / Frontend Design |
| Codex | 后端实现 / Backend Implementation |
| Claude Code | 架构任务 / Architecture Tasks |

---

## Bug 修复 / Bug Fix

示例：

Examples:

- API 500 错误 / API 500 errors
- 控制台错误 / Console errors
- 工作流行为异常 / Broken workflow behavior
- UI 渲染错误 / Incorrect UI rendering
- 数据加载失败 / Data loading failures

提示词编号范围（必须使用5位）：

Prompt numbering range (must use 5 digits):

| 范围 | 类别 |
|------|------|
| 10101–19999 | Bug 修复 / Bug Fix |

执行器取决于问题位置：

Executor depends on the problem location.

| 问题位置 | 执行器 |
|---------|--------|
| 前端问题 / Frontend issue | Gemini (设计), Codex (实现) |
| 后端问题 / Backend issue | Codex |
| 数据库问题 / Database issue | Codex |

---

## 重构 / Refactoring

示例：

Examples:

- 代码结构优化 / Code structure optimization
- 服务层拆分 / Service layer splitting
- 重复代码提取 / Duplicate code extraction
- 技术债务清理 / Tech debt cleanup

提示词编号范围（必须使用5位）：

Prompt numbering range (must use 5 digits):

| 范围 | 类别 |
|------|------|
| 20101–29999 | 重构 / Refactoring |

执行器：

Executor:

| 执行器 | 职责范围 |
|--------|---------|
| Claude Code | 架构变更、重构任务 / Architecture changes, Refactoring tasks |

---

## 测试 / Testing

示例：

Examples:

- 单元测试编写 / Unit test writing
- 集成测试添加 / Integration test addition
- 端到端测试覆盖 / E2E test coverage
- 回归测试套件 / Regression test suite

提示词编号范围（必须使用5位）：

Prompt numbering range (must use 5 digits):

| 范围 | 类别 |
|------|------|
| 30101–39999 | 测试 / Testing |

执行器：

Executor:

| 执行器 | 职责范围 |
|--------|---------|
| Codex | 测试任务 / Testing tasks |

---

## 统一执行规则 / Unified Execution Rule

除非任务涉及以下情况，否则统一由 Claude Code 执行：

| 任务类型 | 例外条件 | 执行者 |
|---------|---------|--------|
| 功能任务 (00001-09999) | 前端设计大改 | Claude Code |
| Bug 修复 (10101-19999) | P0/P1 恶性bug、架构级bug | Claude Code |
| 重构任务 (20101-29999) | 始终由 Claude Code 执行 | Claude Code |
| 测试任务 (30101-39999) | 始终由 Claude Code 执行 | Claude Code |

### 简化任务判定标准 / Simple Task Criteria

以下情况视为"简化任务"，由 Claude Code 直接执行：

- 参数类型不匹配修复
- API 调用参数提取错误
- 简单函数签名修正
- docstring 更新
- 文档同步
- 单文件/单函数修改
- 不涉及架构变更的 bug 修复

### 恶性 Bug 定义 / Malignant Bug Definition

以下情况视为"恶性 Bug"：

- P0 级别：系统无法运行、数据损坏风险
- P1 级别：核心功能损坏、API 不可用、工作流阻塞

### Claude Code 执行优势

- 无需跨模型协调
- 直接执行减少流程开销
- 保持上下文连贯性

---

# 自动提示词编号 / Automatic Prompt Numbering

系统必须根据任务类型选择正确的编号范围（必须使用5位格式）：

The system must select the correct numbering range based on task type (must use 5-digit format):

| 任务类型 / Task Type | 编号范围 / Number Range |
|---------------------|----------------------|
| 功能开发 / Feature Development | 00001–09999 |
| Bug 修复 / Bug Fix | 10101–19999 |
| 重构 / Refactoring | 20101–29999 |
| 测试 / Testing | 30101–39999 |

编号分配规则 / Number Assignment Rules:

1. 检查 `promptsRec/active/` 中对应范围的现有提示词 / Inspect existing prompts in the corresponding range in `promptsRec/active/`
2. 确定该范围内使用的最高编号 / Determine the highest used number in that range
3. 分配下一个有效的可用编号 / Assign the next available valid number

示例：

Example:

最新功能提示词：00017 / Latest feature prompt: 00017
下一个功能提示词：00018 / Next feature prompt: 00018

最新 Bug 提示词：10101 / Latest bug prompt: 10101
下一个 Bug 提示词：10102 / Next bug prompt: 10102

---

# 提示词生成标准 / Prompt Generation Standard

生成的提示词必须遵循确切的项目规范。

Generated prompts must follow the exact project specification.

提示词头部（必须使用5位编号）：

Prompt Header (must use 5-digit numbering):

Primary Executor: <Agent>
Task Type: <Feature Development | Bug Fix | Refactoring | Testing>
Priority: <P0 | P1 | P2>
Stage: <5-digit Prompt Number>
Goal: <One-line description>
Dependencies: <"None" or list of prompt numbers that must complete first>
Execution: RUNPROMPT

示例：

Example:

Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 00017
Goal: Migrate order list page UI to Element Plus
Dependencies: None
Execution: RUNPROMPT

必需章节：

Required Sections:

Context / 上下文
Required References / 必需参考
Core Task / 核心任务
Required Work / 必需工作
Constraints / 约束条件
Completion Criteria / 完成标准

优先级定义 / Priority Definitions:

- P0: 安全漏洞、权限漏洞、数据完整性风险 / Security gaps, permission vulnerabilities, data integrity risks
- P1: 核心逻辑正确性、关键路径测试缺失 / Core logic correctness, missing tests for critical paths
- P2: 代码质量、重构、用户体验改进 / Code quality, refactoring, UX improvements

---

# Bug 调查规则 / Bug Investigation Rule

如果任务是 bug 修复，生成的提示词必须要求代理：

If the task is a bug fix, the generated prompt must require the agent to:

1. 检查后端日志 / Inspect backend logs
2. 检查相关源代码模块 / Inspect relevant source code modules
3. 检查真实数据库架构 / Inspect real database schema
4. 在修改代码前确定根本原因 / Identify the root cause before modifying code

不允许盲目猜测。

Blind guessing is not allowed.

---

# 功能集成规则 / Feature Integration Rule

如果任务是功能：

If the task is a feature:

提示词必须：

The prompt must:

- 与当前架构集成 / Integrate with the current architecture
- 尽可能重用现有组件 / Reuse existing components whenever possible
- 避免不必要的重新设计 / Avoid unnecessary redesign

---

# 输出格式 / Output Format

输出必须始终结构化为：

The output must always be structured as:

文件名：promptsRec/active/<prompt_name>.md
执行模型：<Agent>

文件名：promptsRec/active/<prompt_name>.md
执行模型：<Agent>

Then output the full prompt content.

---

# 重要约束条件 / Important Constraints

系统不得：

The system must NOT:

- 不经分析就生成提示词 / Generate prompts without analysis
- 违反编号规则 / Break numbering rules:
  - 00001–09999 = Feature Development
  - 10101–19999 = Bug Fix
  - 20101–29999 = Refactoring
  - 30101–39999 = Testing
- 跳过必需的提示词章节 / Skip required prompt sections
- 跳过优先级声明 (P0/P1/P2) / Skip priority declaration (P0/P1/P2)
- 假设数据库架构 / Assume database schema
- 假设后端 API / Assume backend APIs
- 无正当理由重新设计稳定架构 / Redesign stable architecture without justification

---

# 完成标准 / Completion Criteria

在以下情况下技能被视为成功：

The skill is considered successful when:

1. 检测到的问题被转换为标准化提示词 / A detected problem is converted into a standardized prompt
2. 提示词遵循项目开发规则 / The prompt follows project development rules
3. 提示词可以立即由 RUNPROMPT 执行 / The prompt can be executed immediately by RUNPROMPT
4. 提示词执行后开发管道可以自动继续 / The development pipeline can continue automatically after prompt execution
