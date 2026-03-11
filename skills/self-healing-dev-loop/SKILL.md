# 自愈开发循环技能 / Self Healing Dev Loop Skill

---

## 目的 / Purpose

自愈开发循环技能使系统能够自动检测开发问题、生成结构化的开发提示词、执行修复并更新项目任务管道。

The Self-Healing Dev Loop skill enables the system to automatically detect development issues, generate structured development prompts, execute fixes, and update the project task pipeline.

此技能集成了以下子系统：

This skill integrates the following subsystems:

- Dev Inspector / 开发检查器
- Auto Task Generator / 自动任务生成器
- RUNPROMPT / 运行提示词
- pipeline-dashboard / 流水线仪表盘

目标是创建一个半自主开发循环，其中检测到的问题可以通过标准化提示词进行诊断和解决。

The goal is to create a semi-autonomous development loop where detected issues can be diagnosed and resolved through standardized prompts.

---

# 开发管道中的位置 / Position in Development Pipeline

此技能协调自动化开发工作流。

This skill orchestrates the automated development workflow.

标准执行流程：

Standard execution flow:

检测到运行时问题 / Runtime Issue Detected
↓
Dev Inspector 分析问题 / Dev Inspector analyzes problem
↓
Auto Task Generator 生成提示词 / Auto Task Generator generates prompt
↓
pipeline-dashboard 注册新任务 / pipeline-dashboard registers new task
↓
RUNPROMPT 执行提示词 / RUNPROMPT executes prompt
↓
执行器代理（Gemini / Codex）执行实现 / Executor agent (Gemini / Codex) performs implementation
↓
pipeline-dashboard 更新任务状态 / pipeline-dashboard updates task status

---

# 何时使用此技能 / When to Use This Skill

在以下情况下使用此技能：

Use this skill when:

- 检测到运行时错误 / a runtime error is detected
- 出现控制台错误 / a console error appears
- 在测试期间发现缺失功能 / a missing feature is discovered during testing
- 发现 UI 问题 / a UI issue is found
- 发生 API 失败 / an API failure occurs
- 出现工作流不一致 / a workflow inconsistency appears

典型触发条件包括：

Typical triggers include:

- 浏览器控制台错误 / browser console errors
- API 响应失败 / API response failures
- 意外的 UI 状态 / unexpected UI states
- 工作流破坏 / broken workflows
- 数据库操作失败 / failed database operations

---

# 技能组件 / Skill Components

此技能协调四个子系统。

This skill coordinates four subsystems.

## Dev Inspector

负责：

Responsible for:

- 观察浏览器和运行时环境 / observing browser and runtime environment
- 分析控制台错误 / analyzing console errors
- 分析 API 失败 / analyzing API failures
- 识别可能的根本原因层 / identifying probable root cause layer

可能的层：

Possible layers:

- 前端 / frontend
- 网络 / network
- 后端 / backend
- 数据库 / database

Dev Inspector 不修改代码。

Dev Inspector does NOT modify code.

它只执行诊断。

It only performs diagnosis.

---

## Auto Task Generator

负责：

Responsible for:

- 将检查的问题转换为结构化提示词 / converting inspected issues into structured prompts
- 分配提示词编号 / assigning prompt numbers
- 选择正确的执行器代理 / selecting the correct executor agent
- 生成符合项目规则的提示词 / generating prompts compliant with project rules

提示词编号：

Prompt numbering:

功能提示词：

Feature prompts:

000–099

Bug 提示词：

Bug prompts:

100–199

执行器规则：

Executor rules:

Gemini → 前端 / frontend
Codex → 后端 / backend
Claude Code → 架构 / architecture

---

## pipeline-dashboard 集成 / pipeline-dashboard Integration

每个生成的任务必须注册到 pipeline-dashboard。

Every generated task must be registered with pipeline-dashboard.

必需的管道更新操作：

Required pipeline update actions:

1. 注册新任务 / register new task
2. 分配执行器 / assign executor
3. 标记任务为待处理 / mark task as pending

示例管道条目：

Example pipeline entry:

Task: 104_bug_order_api_response_error
Executor: Codex
Status: Pending

RUNPROMPT 完成后，pipeline-dashboard 必须更新：

When RUNPROMPT finishes execution, pipeline-dashboard must update:

Status → Completed

---

## RUNPROMPT 执行 / RUNPROMPT Execution

管道注册后，执行生成的提示词。

After pipeline registration, the generated prompt is executed.

执行流程：

Execution flow:

RUNPROMPT 从 promptsRec 读取提示词 / RUNPROMPT reads prompt from promptsRec
↓
创建 .lock 文件 / Creates .lock file
↓
分配的代理执行实现 / Assigned agent performs implementation
↓
生成执行报告 / Execution report generated
↓
提示词归档 / Prompt archived

---

# 根本原因分析规则 / Root Cause Analysis Rules

在生成任务之前，Dev Inspector 必须尝试根本原因分析。

Before generating a task, Dev Inspector must attempt root cause analysis.

可能的问题层包括：

Possible issue layers include:

前端层 / Frontend Layer

- Vue 运行时错误 / Vue runtime errors
- 错误的组件状态 / incorrect component state
- 错误的 API 调用 / incorrect API calls

网络层 / Network Layer

- 错误的基础 URL / incorrect base URL
- 缺少代理配置 / missing proxy configuration
- 请求头不匹配 / request header mismatch

后端层 / Backend Layer

- 缺少 API 路由 / missing API route
- 服务逻辑错误 / service logic error
- 未处理的异常 / unhandled exception

数据库层 / Database Layer

- 架构不匹配 / schema mismatch
- 缺少表 / missing table
- SQL 查询错误 / SQL query error

识别的层决定执行器。

The identified layer determines the executor.

---

# 提示词生成规则 / Prompt Generation Rules

生成的提示词必须遵循项目标准。

Generated prompts must follow project standards.

提示词头部格式：

Prompt header format:

Primary Executor / 主要执行者
Task Type / 任务类型
Stage / 阶段
Goal / 目标
Execution: RUNPROMPT

必需的提示词章节：

Required prompt sections:

Context / 上下文
Required References / 必需参考
Core Task / 核心任务
Required Work / 必需工作
Constraints / 约束条件
Completion Criteria / 完成标准

---

# 任务生命周期 / Task Lifecycle

每个任务必须遵循此生命周期。

Each task must follow this lifecycle.

已检测 / Detected
↓
已注册 (pipeline-dashboard) / Registered (pipeline-dashboard)
↓
待处理 / Pending
↓
RUNPROMPT 执行 / RUNPROMPT Execution
↓
已完成 / Completed

如果执行失败：

If execution fails:

Status → 需要调查 / Investigation Required

---

# 安全约束 / Safety Constraints

此技能严禁：

This skill must NOT:

- 直接修改生产数据 / modify production data directly
- 绕过 RUNPROMPT 执行 / bypass RUNPROMPT execution
- 不经检查生成提示词 / generate prompts without inspection
- 自动重新设计稳定架构 / redesign stable architecture automatically
- 假设数据库架构 / assume database schema

所有修复必须通过提示词执行。

All fixes must be executed through prompts.

---

# 示例工作流 / Example Workflow

示例情况：

Example situation:

浏览器控制台：

Browser console:

GET /api/tool-io-orders → 500

Dev Inspector 结果：

Dev Inspector result:

Layer: Backend
Problem: API failure

Auto Task Generator 创建：

Auto Task Generator creates:

104_bug_order_api_endpoint_failure.md

pipeline-dashboard 注册：

pipeline-dashboard registers:

Task: 104_bug_order_api_endpoint_failure
Executor: Codex
Status: Pending

RUNPROMPT 执行任务。

RUNPROMPT executes task.

Codex 实现修复。

Codex implements fix.

pipeline-dashboard 更新：

pipeline-dashboard updates:

Status → Completed

---

# 完成标准 / Completion Criteria

当满足以下条件时，自愈开发循环被视为可运行：

Self-Healing Dev Loop is considered operational when:

1. 运行时问题触发 Dev Inspector / runtime issues trigger Dev Inspector
2. 任务自动生成 / tasks are generated automatically
3. pipeline-dashboard 注册任务 / pipeline-dashboard registers tasks
4. RUNPROMPT 执行任务 / RUNPROMPT executes tasks
5. pipeline-dashboard 更新任务状态 / pipeline-dashboard updates task status
6. 开发循环继续无需手动创建任务 / development loop continues without manual task creation
