# 提示词生成器 / Prompt Generator Skill

**规则约束**: 本技能生成提示词时，根据任务类型调用相应规则：
- 功能开发/重构/测试 → `.claude/rules/01_workflow.md` (ADP 四阶段开发协议)
- Bug 修复/回归问题 → `.claude/rules/02_debug.md` (8D 问题解决协议)
- 生产环境紧急修复 → `.claude/rules/03_hotfix.md` (热修复 SOP)
- 编号约定 → `.claude/rules/05_task_convention.md`

## 目的 / Purpose

本技能使 AI 代理（特别是 Gemini）能够生成符合项目 AI 驱动开发工作流的标准化开发提示词。

This skill enables AI agents (especially Gemini) to generate standardized development prompts that comply with the project's AI-driven development workflow.

生成的提示词必须遵循项目的提示词规范，并且必须可以直接在 `promptsRec/active/` 目录中使用。

The generated prompts must follow the project's prompt specification and must be directly usable inside the `promptsRec/active/` directory.

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

# 开发协议与流程规范 / Development Protocols

根据任务类型和紧急程度，选择合适的开发协议：

## 协议选择指南 / Protocol Selection Guide

| 任务类型 | 适用协议 | 规则文件 |
|----------|---------|----------|
| 功能开发 (00001-09999) | ADP Protocol | `.claude/rules/01_workflow.md` |
| UI 改进 / 前端设计 | ADP Protocol | `.claude/rules/01_workflow.md` |
| 架构重构 (20101-29999) | ADP Protocol | `.claude/rules/01_workflow.md` |
| 测试任务 (30101-39999) | ADP Protocol | `.claude/rules/01_workflow.md` |
| Bug 修复 (10101-19999) | 8D Protocol | `.claude/rules/02_debug.md` |
| 回归问题 | 8D Protocol | `.claude/rules/02_debug.md` |
| 生产环境紧急修复 | HOTFIX SOP | `.claude/rules/03_hotfix.md` |

## 1. ADP Protocol - 标准功能开发协议（常规任务）

适用于：新功能实现、UI 改进、架构重构、测试任务

**规则文件**: `.claude/rules/01_workflow.md`

进入首席架构师与全栈开发专家角色。在开发工装出入库管理系统新功能时，请严格按照以下四个阶段（PRD -> Data -> Architecture -> Execution）进行连贯的思考与实施。

### Phase 1: 业务需求与场景 (PRD & Context)

- 【业务场景】：[填入业务场景，如：工人需要在指定时间内完成订单的工装出入库操作]
- 【目标用户】：[填入目标用户，如：班组长、保管员、管理员]
- 【核心痛点】：[填入当前遇到的问题，如：订单状态无法跟踪，或工装搜索结果不准确]
- 【业务目标】：[填入期望实现的功能，如：实现工装出入库的完整工作流]

### Phase 2: 数据流转与深度穿透防御 (Data Flow & Deep Penetration Defense)

在动手写任何代码前，必须强制审视底层数据 Schema 与框架生命周期！

- 【数据来源】：
  - 后端：`database.py` (SQL Server)
  - 前端：`frontend/src/api/` (API 调用)
- 【主键穿透校验 (PK Consistency)】：
  - 如果涉及数据的修改/合并/删除，后端逻辑 **必须严格基于 UUID/ID 进行比对和落盘**。
  - 绝对禁止使用 Label/名称进行业务匹配，防范静默失效！
- 【缓存与状态防御 (Lifecycle Trap)】：
  1. 涉及 Vue 前端状态管理（Pinia store）的重构，必须确保状态持久化与组件卸载后的清理。
  2. 交互组件（如 `el-table`、`el-select`）操作时，是否会引发页面刷新导致"搜索状态/上下文丢失"？若有，必须引入预筛选（Pre-filter）或 `sessionStorage` 代理机制。
  3. Flask 后端确保使用连接池管理 SQL Server 连接，避免连接泄漏。
- 【强制前置动作】：请先执行语法检查确认代码无错误：
  ```powershell
  python -m py_compile web_server.py database.py backend/services/tool_io_service.py config/settings.py
  ```

### Phase 3: 架构设计与约束 (Architecture Design & Constraints)

- 【交互链路】：
  - 前端：`Vue 3 + Element Plus` -> `API 调用` -> `Flask REST API` -> `SQL Server`
  - 完整链路：前端组件动作 -> API 请求 -> 后端路由 -> Service 层 -> Repository 层 -> 数据库 -> 响应回传 -> 前端状态更新
- 【零退化原则 (Zero-Regression)】：
  - 本次代码切入绝不允许破坏现有的 UI 规范（深色主题 Element Plus）
  - 不得破坏已实现的 8D 工作流闭环
  - 不得破坏底层的主键映射机制
- 【代码规范】：
  - 使用英文变量名和函数名（禁止拼音）
  - 4 空格缩进，`snake_case` 函数/变量
  - 配置集中在 `config/settings.py`

### Phase 4: 精确执行与集成验证 (Execution & E2E Verification)

请根据以上严密的架构分析，连贯执行代码修改：

- [ ] Step 1: 编写/升级后端核心数据处理逻辑（严格遵守主键穿透与清洗机制）。
- [ ] Step 2: 注入前端 Vue 代码（包含状态管理与 API 调用层）。
- [ ] Step 3: 复杂后端逻辑必须先辅以"无头测试 (Headless TDD)"，确保脱离 UI 也能正确执行数据库操作。
- [ ] Step 4: 执行端到端自测：
  - 后端：`python -m py_compile <相关文件>`
  - 前端：`cd frontend && npm run build`
  - 启动服务并验证功能

### Phase 5: UI 一致性验证 (UI Consistency Verification)

新增修改涉及前端 UI 时，必须验证以下一致性：

#### 确认对话框一致性检查 / Confirmation Dialog Consistency Check

如果修改涉及以下操作之一，必须检查所有相关页面：

| 操作 | 必须检查的页面 |
|------|--------------|
| 提交 / Submit | OrderList.vue, OrderDetail.vue |
| 取消 / Cancel | OrderDetail.vue |
| 最终确认 / Final Confirm | OrderDetail.vue |
| 删除 / Delete | OrderDetail.vue |

**验证方法**:
1. 搜索相关页面中的 `ElMessageBox.confirm` 调用
2. 确认消息格式与 `00_core.md` 中定义的模板一致
3. 确认按钮文本使用中文：`提交`、`取消`、`确认`、`删除`

#### CSS 变量使用检查 / CSS Variable Usage Check

1. 全局搜索禁止的硬编码颜色：`bg-white`, `bg-black`, `text-white`, `text-black`
2. 如果存在，记录到 `logs/codex_rectification/` 作为需要修复的技术债
3. 优先使用语义化 CSS 变量

#### 主题系统检查 / Theme System Check

如果修改涉及 `SettingsPage.vue` 或主题系统：
1. 确认初始加载逻辑正确检测系统偏好
2. 确认运行时监听 `window.matchMedia` 变化
3. 确认用户手动覆盖后不再响应系统变化

### 关键约束

1. **文档权威性**：代码不得偏离 `docs/PRD.md`、`docs/ARCHITECTURE.md`、`docs/API_SPEC.md`、`docs/DB_SCHEMA.md`
2. **事务处理**：订单提交、保管员确认、最终确认等关键操作必须使用数据库事务
3. **日志记录**：每个关键操作必须记录操作人、时间戳、订单ID、之前状态、下一状态
4. **通知处理**：飞书通知必须记录成功/失败状态，允许重试

执行完毕后，挂起并输出详细的"架构实施与全链路穿透报告"。

---

## 2. 8D 问题解决协议 - Bug/回归问题专用（调试任务）

适用于：浏览器调试发现的问题、生产环境回归问题

**规则文件**: `.claude/rules/02_debug.md`

**角色**：根本原因分析工程师 / Root Cause Analysis Engineer

**仅用于调试或回归问题** / Used only for debugging or regression issues

### 8D 步骤

| 步骤 | 名称 | 说明 |
|------|------|------|
| D1 | 团队组建 / Team formation | 组建问题解决团队 |
| D2 | 问题描述 / Problem description | 详细描述问题现象 |
| D3 | 遏制措施 / Containment | 临时解决方案防止扩散 |
| D4 | 根本原因分析 / Root cause analysis | 深入分析真正原因 |
| D5 | 永久解决方案 / Permanent solution | 制定永久修复方案 |
| D6 | 实施 / Implementation | 执行修复 |
| D7 | 预防 / Prevention | 防止再次发生 |
| D8 | 文档 / Documentation | 记录经验教训 |

### 8D 要求

每个 bug 修复必须包括：

- 根本原因解释 / root cause explanation
- 测试用例 / test case
- 回归预防 / regression prevention

**禁止使用临时补丁** / Temporary patches are forbidden.

### 强制审核机制

D3、D5、D6 阶段完成后**必须**触发 reviewer 评分审核：

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

**Bug 修复归档前必须验证**：D3/D5/D6 全部维度达标记录存在。

---

## 3. HOTFIX SOP - 热修复标准操作流程（紧急修复）

适用于：生产环境紧急问题需要快速修复

**规则文件**: `.claude/rules/03_hotfix.md`

**角色**：网站可靠性工程师 / Site Reliability Engineer

### HOTFIX 原则

1. 最小影响范围 / Minimal blast radius
2. 原子性变更 / Atomic changes
3. 立即验证 / Immediate verification

### HOTFIX 步骤

| 步骤 | 名称 | 说明 |
|------|------|------|
| 1 | 识别受影响的模块 / Identify affected modules | 确定影响范围 |
| 2 | 创建 RFC 计划 / Create RFC plan | 制定最小变更计划 |
| 3 | 应用最小补丁 / Apply minimal patch | 执行精确修复 |
| 4 | 运行验证 / Run verification | 立即测试验证 |
| 5 | 提交并部署 / Commit and deploy | 完成部署 |

### HOTFIX 与 8D 的区别

- **HOTFIX**：用于紧急修复，强调速度和最小变更
- **8D**：用于系统性解决问题，强调根本原因分析和预防

---

# 提示词命名规则 / Prompt Naming Rules

提示词编号是严格定义的。

Prompt numbering is strictly defined.

| Range   | Category              | Example                                  |
|---------|-----------------------|------------------------------------------|
| 00001–09999 | Feature Development   | `00017_order_list_ui_migration.md`        |
| 10101–19999 | Bug Fix / Security Fix| `10101_bug_tool_search_request_routing.md` |
| 20101–29999 | Refactoring / Tech Debt| `20101_refactor_split_tool_io_service.md` |
| 30101–39999 | Testing / Quality     | `30101_workflow_state_machine_tests.md`    |

---

# 提示词输出格式 / Prompt Output Format

输出必须始终包含：
**AI 必须将生成的提示词实际写入 `promptsRec/active/` 目录，而不是仅输出内容摘要。**

The output must always contain:
**The AI MUST actually write the generated prompt to the `promptsRec/active/` directory, not just output a content summary.**

1. 文件名 / File name (格式: `promptsRec/active/<number>_<description>.md`)
2. 执行模型 / Executor model
3. 完整的提示词内容 / Full prompt content

示例输出格式：

Example output format:

文件名：promptsRec/active/017_order_list_ui_migration.md
执行模型：Gemini

文件名：promptsRec/active/017_order_list_ui_migration.md
执行模型：Gemini

Then output the full prompt content.

---

# 提示词头部格式 / Prompt Header Format

每个生成的提示词必须以以下头部开头：

Every generated prompt must begin with the following header:

Primary Executor: <Agent>
Task Type: <Feature Development | Bug Fix | Refactoring | Testing>
Priority: <P0 | P1 | P2>
Stage: <Prompt Number>
Goal: <One-line description>
Dependencies: <"None" or list of prompt numbers that must complete first>
Execution: RUNPROMPT

示例：

Example:

Primary Executor: Gemini
Task Type: Feature Development
Priority: P1
Stage: 017
Goal: Migrate order list page UI to Mist component style
Dependencies: None
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

# 问题分析要求 / Pre-Generation Analysis

在生成提示词之前，AI 必须：

Before generating a prompt, the AI must:

1. 分析问题 / Analyze the problem thoroughly
2. 确定任务类别和编号范围: / Determine the task category and numbering range:
   - 功能开发 / Feature Development → feature_next (00001–09999)
   - Bug 修复 / Bug Fix / Security Fix → bugfix_next (10101–19999)
   - 重构/技术债 / Refactoring / Tech Debt → refactor_next (20101–29999)
   - 测试/质量 / Testing / Quality → test_next (30101–39999)

   **编号获取**: 从 `promptsRec/.sequence` 文件读取对应计数器，详见 `.claude/rules/05_task_convention.md`

3. 确定正确的执行器 / Determine the correct executor
4. 识别依赖关系 / Identify dependencies on other prompts
5. 分配优先级 / Assign priority:
   - P0: Security gaps, permission vulnerabilities, data integrity risks
   - P1: Core logic correctness, missing tests for critical paths
   - P2: Code quality, refactoring, UX improvements

执行器规则：

Executor rules:

| Executor     | Scope                                                        |
|--------------|--------------------------------------------------------------|
| Gemini       | Frontend tasks: UI, UX, component styling, page layout       |
| Codex        | Backend tasks: API, service logic, database queries           |
| Claude Code  | Architecture tasks: refactoring, cross-cutting concerns, RBAC design, workflow redesign, multi-file structural changes |

如果一个任务跨越前端+后端，创建具有明确依赖声明的单独提示词。

If a task spans frontend + backend, create **separate prompts** for each executor with explicit dependency declarations.

---

# Bug 提示词规则 / Bug Prompt Rules (10101–19999)

如果问题是 bug：

If the problem is a bug:

- 提示词编号必须在 10101–19999 范围内 / The prompt number must be in the 10101–19999 range
- 修改前必须进行调查 / Investigation must occur before modification
- 提示词必须指示代理检查真实代码库 / The prompt must instruct the agent to inspect the real codebase
- 提示词必须指示代理检查真实数据库架构 / The prompt must instruct the agent to inspect the real database schema
- 提示词必须包含优先级 (P0/P1/P2) / The prompt must include priority (P0/P1/P2)

提示词不得假设：

The prompt must NOT assume:

- 数据库字段名 / Database field names
- 后端 API 结构 / Backend API structure
- 工作流状态 / Workflow states

---

# 功能提示词规则 / Feature Prompt Rules (00001–09999)

如果任务是功能：

If the task is a feature:

- 提示词编号必须在 00001–09999 范围内 / The prompt number must be in the 00001–09999 range
- 提示词必须与现有架构集成 / The prompt must integrate with existing architecture
- 提示词不得重新设计稳定的子系统 / The prompt must not redesign stable subsystems
- 提示词必须包含优先级 (P0/P1/P2) / The prompt must include priority (P0/P1/P2)

---

# 重构提示词规则 / Refactoring Prompt Rules (20101–29999)

如果任务是重构：

If the task is refactoring:

- 提示词编号必须在 20101–29999 范围内 / The prompt number must be in the 20101–29999 range
- 必须保留所有现有行为 (无功能变更) / Must preserve all existing behavior (no functional changes)
- 必须包含重构前后的结构描述 / Must include before/after structure description
- 提示词必须包含优先级 (P0/P1/P2) / The prompt must include priority (P0/P1/P2)

---

# 测试提示词规则 / Testing Prompt Rules (30101–39999)

**规则文件**: `.claude/rules/06_testing.md`

如果任务是测试：

If the task is testing:

- 提示词编号必须在 30101–39999 范围内 / The prompt number must be in the 30101–39999 range
- 必须指定测试框架和断言策略 / Must specify test framework and assertion strategy
- 必须定义覆盖率目标 / Must define coverage targets
- 提示词必须包含优先级 (P0/P1/P2) / The prompt must include priority (P0/P1/P2)
- 必须包含 Test Scope、Test Strategy、Test Cases、Pass Criteria 章节

---

# 约束条件 / Constraints

AI 不得：

The AI must NOT:

- 仅输出提示词内容而不生成实际文件 / Output prompt content without generating actual files
- 生成不完整的提示词 / Generate partial prompts
- 跳过必需章节 / Skip required sections
- 无正当理由重新设计稳定架构 / Redesign stable architecture without justification
- 假设数据库架构 / Assume database schema
- 不检查就假设后端 API / Assume backend APIs without inspection
- 生成超出编号规则的提示词 / Generate prompts outside numbering rules:
  - 00001–09999 = Feature Development
  - 10101–19999 = Bug Fix / Security Fix
  - 20101–29999 = Refactoring / Tech Debt
  - 30101–39999 = Testing / Quality
- 跳过优先级声明 / Skip priority declaration (P0/P1/P2)
- 跳过依赖声明 (当有依赖时) / Skip dependency declaration (when dependencies exist)

---

# 完成标准 / Completion Criteria

生成的提示词只有在以下情况下才被视为有效：

A generated prompt is considered valid only if:

1. 遵循提示词格式 / It follows the prompt format
2. 遵守编号规则 / It respects numbering rules:
   - 00001–09999 = Feature Development
   - 10101–19999 = Bug Fix / Security Fix
   - 20101–29999 = Refactoring / Tech Debt
   - 30101–39999 = Testing / Quality
3. 包含所有必需章节 / It contains all required sections:
   - Primary Executor
   - Task Type
   - Priority (P0/P1/P2)
   - Stage
   - Goal
   - Dependencies
   - Context
   - Required References
   - Core Task
   - Required Work
   - Constraints
   - Completion Criteria
4. 包含具体的验收测试 (非模糊) / Contains concrete Acceptance Tests (not vague)
5. 正确声明依赖关系 / Correctly declares dependencies
6. 可以由 RUNPROMPT 直接执行 / It can be executed directly by RUNPROMPT
