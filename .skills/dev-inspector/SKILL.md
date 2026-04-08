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

**触发此技能时，如果发现控制台报错（Vue 运行时错误、JavaScript 异常等），必须先向用户询问以下信息，不得擅自假设或跳过：**

| 必问项 | 说明 |
|--------|------|
| 报告人账号 | 出现问题的用户名、角色、组织 |
| 哪一步操作时出现错误 | 从初始状态到 bug 出现的每一步操作序列 |
| 控制台错误信息/截图 | 完整的错误日志或截图附件 |

**模板**：
```
【Dev Inspector】检测到控制台错误，需要补充以下信息：

1. 报告人账号：[username] / 角色：[role] / 组织：[org]
2. 哪一步操作时出现错误：
   Step 1: ...
   Step 2: ...
   Step 3: ...
3. 控制台错误信息或截图：[附件]

收到以上信息前，禁止进入问题分析和任务生成。
```

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

**重要**：本章节严格遵循 `.claude/rules/02_debug.md` 中 D2 问题解决阶段的要求。

---

## D2 阶段：证据驱动的诊断（禁止根因推测）

Dev Inspector 在 D2 阶段的任务是**忠实记录现象，不解释原因**。

In D2, the task is to **faithfully record what happened, not why it happened**.

### 第一步：收集证据清单 / Evidence Collection

在分析之前，必须收集以下证据（至少三项）：

| 证据类型 | 说明 | 来源 |
|----------|------|------|
| 错误日志 | 完整的 error/exception 输出 | 服务器日志、控制台 |
| 堆栈跟踪 | 异常堆栈或调用链路 | Stack trace、Debug 日志 |
| 复现步骤 | 从初始状态到 bug 出现的完整操作序列 | 测试记录、用户报告 |
| 影响范围 | 受影响的用户数、功能模块、订单范围 | 监控、用户反馈 |
| 对比基准 | 正常行为 vs 异常行为的差异点 | 测试环境、Prod 对比 |

**证据不足的处理**：

If evidence is insufficient, you MUST ask the user before proceeding:

```
【Dev Inspector】D2 信息缺口 - 以下证据未提供，请补充：

1. 报告人账号：[username] / 角色：[role] / 组织：[org]
2. 触发操作的完整步骤：
   Step 1: ...
   Step 2: ...
   Step 3: ...
3. 错误日志/控制台截图：[附件]

在收到以上信息前，禁止进入问题分析和任务生成。
```

**唯一可跳过追问的情况**：
- 证据链已完整（≥3项证据齐全）
- 复现路径清晰、可在测试环境独立验证

---

## 第二步：描述事实（What），不解释原因（Why）

基于收集的证据，描述**观察到的现象**，格式如下：

**描述模板**：
```
## D2 问题描述 / D2 Problem Description

### What（是什么）
[具体描述发生了什么 - 使用证据链中的事实]

### Where（在哪里）
[受影响的模块/页面/功能]

### When（何时发生）
[首次发现时间、复现频率、订单号/用户账号等]

### Impact（影响范围）
[受影响的用户数、功能范围、数据异常程度]
```

**D2 阶段禁止出现的内容**：
- ❌ "可能是 XXX 导致的"
- ❌ "根据经验判断是 YYY"
- ❌ "根因是 ZZZ"

---

## 第三步：定位可疑层（基于证据，不推测）

仅基于已收集的证据，标记可疑的层（不是根因，只是待验证的怀疑方向）：

| 可疑层 | 证据表现 | 排查方向 |
|--------|----------|----------|
| 前端层 | 控制台报错、组件渲染异常、API请求发出但格式错误 | 检查前端代码、状态管理、API调用 |
| 网络层 | 请求未发出、代理404、跨域错误、CORS报错 | 检查 Vite proxy、网络请求配置 |
| 后端层 | API返回5xx、路由不存在、参数验证失败 | 检查后端路由、服务层逻辑 |
| 数据库层 | SQL执行报错、数据查询结果异常、连接失败 | 检查SQL、schema、数据存在性 |

**注意**：定位可疑层是"在哪里查"，不是"为什么坏"。Why 是 D4 阶段的产物。

---

## 示例修正对比 / Example Correction

### 错误示例（违反 D2）

```
Browser console shows HTTP 500.
Problem likely in backend service layer.  ← 这是 Why 推测，违反 D2
Root cause is missing parameter validation.  ← 根因推测，违反 D2
```

### 正确示例（符合 D2）

```
## D2 问题描述

### What
浏览器控制台显示 GET /api/tool-io-orders 返回 HTTP 500，
响应体为 "Internal Server Error"。

### Where
订单列表页面 /api/tool-io-orders API 调用

### When
2026-04-08 14:30，首次发现，操作人员报告

### Impact
订单列表页面无法加载，影响所有用户

### 可疑层
后端层 / Backend layer
（基于 HTTP 500 响应，无前端报错）
```

---

技能必须识别最可能的层，但必须基于证据。

The skill must identify the most likely layer, but based on evidence only.

---

# 与自动任务生成器的集成 / Integration with Auto Task Generator

问题分类和分析完成后，开发检查器必须调用自动任务生成器技能。

Once the issue is classified and analyzed, Dev Inspector must invoke the Auto Task Generator skill.

传递给生成器的信息必须包括：

Information passed to the generator must include:

- D2 问题描述 / D2 Problem Description（What/Where/When/Impact）
- 证据清单 / evidence list
- 可疑层 / suspected layer（基于证据，非根因推测）
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
- 可疑层：后端层 / Backend layer（基于 HTTP 500 响应，无前端报错）

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

```
## Dev Inspector 检查报告

### 问题分类
Issue Type: Bug

### D2 问题描述
What: GET /api/tool-io-orders 返回 HTTP 500，响应体 "Internal Server Error"
Where: 订单列表页面 /api/tool-io-orders API
When: 2026-04-08 14:30，操作人员首次报告
Impact: 订单列表页面无法加载，影响所有用户

### 证据清单
- [x] 错误日志: HTTP 500 Internal Server Error
- [x] 堆栈跟踪: Flask exception stack in server log
- [x] 复现步骤: 打开订单列表页面 → API 返回 500

### 可疑层
Backend layer（基于 HTTP 500 响应，无前端控制台报错）

### 触发
Invoke Auto Task Generator (Bug, 10101-19999, Codex)
```

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
