---
name: dev-inspector
executor: Claude Code
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/05_task_convention.md
version: 1.0.0
---

# 开发检查器技能 / Dev Inspector Skill

**规则约束**: 本技能在生成任务时，必须遵循 `.claude/rules/05_task_convention.md` 中的提示词编号约定（00001-09999 功能、10101-19999 Bug、20101-29999 重构、30101-39999 测试）。

---

## 目的 / Purpose

开发检查器技能使 AI 代理（尤其是 Gemini）能够分析运行时错误、浏览器控制台日志、API 失败或开发过程中的意外 UI 行为，并将它们转换为结构化的开发任务。/ The Dev Inspector skill enables AI agents (especially Gemini) to analyze runtime errors, browser console logs, API failures, or unexpected UI behavior during development and convert them into structured development tasks.

此技能作为 AI DevOps 管道的**第一诊断层**工作。/ This skill works as the **first diagnostic layer** of the AI DevOps pipeline.

它在调试期间观察问题，并确定是否应触发 bug 调查提示词或功能改进提示词。/ It observes problems during debugging and determines whether they should trigger a bug investigation prompt or a feature improvement prompt.

此技能本身不直接修改代码。相反，它分析问题，然后调用**自动任务生成器技能**来创建正确的开发提示词。/ The skill itself does not directly modify code. Instead, it analyzes the issue and then invokes the **Auto Task Generator skill** to create the correct development prompt.

---

# AI 开发管道中的位置 / Position in AI Development Pipeline

开发检查器技能在自动化开发工作流的开始处运行。

The Dev Inspector skill operates at the beginning of the automated development workflow.

典型流程：

Typical flow:

浏览器调试 / Browser Debugging
↓
Dev Inspector 检测问题 / Dev Inspector detects issue
↓
问题分析 / Problem Analysis
↓
自动任务生成器生成提示词 / Auto Task Generator generates prompt
↓
RUNPROMPT 执行提示词 / RUNPROMPT executes prompt
↓
Codex / Gemini 实现解决方案 / Codex / Gemini implement solution

---

# 何时使用此技能 / When to Use This Skill

在开发过程中遇到以下情况时使用开发检查器：

Use Dev Inspector whenever one of the following situations occurs during development:

### 运行时错误 / Runtime errors

示例：

Examples:

- API 返回 500 / API returns 500
- API 返回意外数据 / API returns unexpected data
- 网络请求失败 / network request fails
- 数据库查询失败 / database query fails

### 浏览器控制台错误 / Browser console errors

示例：

Examples:

- Vue 运行时错误 / Vue runtime errors
- JavaScript 异常 / JavaScript exceptions
- 缺少模块导入 / missing module imports
- 组件渲染失败 / component render failures

### UI 异常 / UI anomalies

示例：

Examples:

- 有效数据但表格为空 / empty tables with valid data
- 组件渲染错误 / incorrect component rendering
- 布局破坏 / layout breaking
- 加载状态卡住 / loading states stuck

### 工作流不一致 / Workflow inconsistencies

示例：

Examples:

- 订单状态不更新 / order status not updating
- 工作流步骤跳过 / workflow step skipped
- 操作日志缺失 / operation log missing
- 通知未记录 / notification not recorded

---

# 要检查的数据源 / Data Sources to Inspect

在生成任务之前，开发检查器应检查以下来源。

Dev Inspector should examine the following sources before generating a task.

### 浏览器控制台 / Browser Console

查找：

Look for:

- JavaScript 错误 / JavaScript errors
- 堆栈跟踪 / stack traces
- 失败的模块加载 / failed module loads
- 运行时异常 / runtime exceptions

### 网络请求 / Network Requests

检查：

Check:

- 请求 URL / request URL
- 请求方法 / request method
- 响应状态码 / response status code
- 响应体 / response body
- 请求头 / headers

示例信号：

Example signals:

200 但返回 HTML 而非 JSON / 200 but HTML returned instead of JSON
500 内部服务器错误 / 500 internal server error
404 缺少 API 路由 / 404 missing API route

### UI 状态 / UI State

观察：

Observe:

- 组件状态 / component state
- 加载指示器 / loading indicators
- 空表格 / empty tables
- 缺失数据 / missing data

### 后端行为（如果可见）/ Backend Behavior (if visible)

查找：

Look for:

- API 端点不匹配 / API endpoint mismatch
- 代理路由错误 / incorrect proxy routing
- 请求参数不匹配 / request parameters mismatch
- 缺少后端路由 / missing backend route

---

# 问题分类 / Problem Classification

检查环境后，技能必须将问题分类到以下类别之一。

After inspecting the environment, the skill must classify the issue into one of the following categories.

## Bug

示例：

Examples:

- API 返回错误响应 / API returning wrong response
- Vue 组件崩溃 / Vue component crash
- 数据不加载 / data not loading
- 路由错误 / incorrect routing
- 缺少代理配置 / missing proxy configuration

Bug 任务必须在范围内生成：

Bug tasks must be generated in range:

10101–19999

执行器：

Executor:

| 问题位置 | 执行器 |
|---------|--------|
| 前端 bug / Frontend bug | Gemini (设计), Codex (实现) |
| 后端 bug / Backend bug | Codex |

---

## 功能缺口 / Feature Gap

示例：

Examples:

- 缺失 UI 元素 / missing UI element
- 缺失工作流能力 / missing workflow capability
- 不完整的仪表盘 / incomplete dashboard
- 缺失日志能力 / missing logging capability

功能任务必须在范围内生成（必须使用5位编号）：

Feature tasks must be generated in range (must use 5-digit numbering):

00001–09999

执行器由领域决定：

Executor determined by domain:

| 领域 | 执行器 |
|------|--------|
| 前端设计 / Frontend Design | Gemini |
| 后端实现 / Backend Implementation | Codex |

---

## 重构需求 / Refactoring Need

示例：

Examples:

- 代码重复度过高 / High code duplication
- 服务层职责过多 / Service layer has too many responsibilities
- 难以维护的代码结构 / Hard to maintain code structure
- 需要优化架构 / Architecture needs optimization

重构任务必须在范围内生成（必须使用5位编号）：

Refactoring tasks must be generated in range (must use 5-digit numbering):

20101–29999

执行器：

Executor:

| 执行器 | 职责范围 |
|--------|---------|
| Claude Code | 所有重构任务、测试任务 / All Refactoring tasks, Testing tasks |

---

## 测试需求 / Testing Need

示例：

Examples:

- 关键路径缺少测试 / Critical paths lack tests
- 需要增加测试覆盖率 / Need to increase test coverage
- 回归测试套件不完整 / Regression test suite incomplete

测试任务必须在范围内生成（必须使用5位编号）：

Testing tasks must be generated in range (must use 5-digit numbering):

30101–39999

执行器：

Executor:

| 执行器 | 职责范围 |
|--------|---------|
| Claude Code | 测试任务 / Testing tasks |

---

# 根本原因分析要求 / Root Cause Analysis Requirement

在生成任务之前，开发检查器必须尝试识别根本原因。

Before generating a task, Dev Inspector must attempt to identify the root cause.

可能的根本原因层包括：

Possible root cause layers include:

### 前端层 / Frontend layer

- API 路径错误 / incorrect API path
- 缺少组件导入 / missing component import
- 状态管理错误 / state management error
- 渲染逻辑错误 / rendering logic mistake

### 网络层 / Network layer

- 缺少 Vite 代理 / missing Vite proxy
- 基础 URL 错误 / incorrect base URL
- 请求头错误 / incorrect request headers

### 后端层 / Backend layer

- 缺少路由 / missing route
- 参数不匹配 / parameter mismatch
- SQL 错误 / SQL error
- 未处理的异常 / unhandled exception

### 数据库层 / Database layer

- 表不匹配 / table mismatch
- 缺少数据 / missing data
- 错误的架构假设 / incorrect schema assumption

技能必须识别最可能的层。

The skill must identify the most likely layer.

---

# 与自动任务生成器的集成 / Integration with Auto Task Generator

问题分类和分析完成后，开发检查器必须调用自动任务生成器技能。

Once the issue is classified and analyzed, Dev Inspector must invoke the Auto Task Generator skill.

传递给生成器的信息必须包括：

Information passed to the generator must include:

- 检测到的问题描述 / detected problem description
- 错误日志 / error logs
- 受影响的模块 / affected module
- 怀疑的根本原因层 / suspected root cause layer
- 推荐的执行器（Gemini 或 Codex）/ recommended executor (Gemini or Codex)

然后自动任务生成器将生成标准化的提示词。

The Auto Task Generator will then produce a standardized prompt.

---

# 示例检查场景 / Example Inspection Scenario

示例情况：

Example situation:

浏览器控制台显示：

Browser console shows:

GET /api/tool-io-orders 500

网络响应：

Network response:

Internal Server Error

开发检查器分析：

Dev Inspector analysis:

- 请求路径有效 / request path valid
- 后端返回 500 / backend returned 500
- 问题可能在后端服务层 / problem likely in backend service layer

分类：

Classification:

Bug

执行器：

Executor:

Codex

下一步：

Next step:

调用自动任务生成器创建 bug 提示词。

Invoke Auto Task Generator to create a bug prompt.

---

# 输出要求 / Output Requirement

开发检查器不直接生成开发提示词。

Dev Inspector does not directly generate development prompts.

相反，它生成**检查报告**然后触发自动任务生成器。

Instead it produces an **inspection report** and then triggers Auto Task Generator.

示例输出：

Example output:

Issue Type: Bug
Layer: Backend
Affected Module: tool_io_order API
Detected Error: HTTP 500

Next Step:

Invoke Auto Task Generator

---

# 约束 / Constraints

开发检查器严禁：

Dev Inspector must NOT:

- 修改源代码 / modify source code
- 生成不完整的提示词 / generate incomplete prompts
- 猜测数据库架构 / guess database schema
- 跳过根本原因分析 / skip root cause analysis
- 重新设计系统架构 / redesign system architecture

其职责仅是**诊断和任务触发**。

Its responsibility is **diagnosis and task triggering only**.

---

# 完成标准 / Completion Criteria

当满足以下条件时，开发检查器成功：

Dev Inspector succeeds when:

1. 检测到运行时问题 / a runtime problem is detected
2. 正确分类问题 / the issue is classified correctly
3. 识别出可能的根本原因层 / the probable root cause layer is identified
4. 触发了自动任务生成器 / Auto Task Generator is triggered
5. 为 RUNPROMPT 创建了开发提示词 / a development prompt is created for RUNPROMPT
