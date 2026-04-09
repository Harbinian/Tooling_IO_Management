---
name: auto-task-generator
executor: Claude Code
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/05_task_convention.md
version: 1.0.0
---

# 自动任务生成器技能 / Auto Task Generator Skill

**规则约束**: 本技能受 `.claude/rules/05_task_convention.md` 约束，必须遵循提示词编号约定和执行者分配规则。

## 目的 / Purpose

本技能使 AI 代理能够自动将发现的问题、开发需求或改进机会转换为标准化的开发提示词。/ This skill enables AI agents to automatically convert discovered problems, development needs, or improvement opportunities into standardized development prompts.

---

# 核心能力 / Core Capability

此技能自动执行以下工作流：

问题检测 / Problem Detection
↓
问题分析 / Problem Analysis
↓
任务分类 / Task Classification（按编号区间）
↓
提示词编号分配 / Prompt Number Assignment（从 `.sequence` 读取）
↓
提示词生成 / Prompt Generation
↓
可立即运行的 RUNPROMPT 任务 / Ready-to-run RUNPROMPT task

---

# 何时使用此技能 / When to Use This Skill

在以下情况下使用此技能：

- 观察到运行时错误 / A runtime error is observed
- 发现 UI 问题 / A UI issue is discovered
- 识别到缺失功能 / A missing feature is identified
- 发现后端工作流缺口 / A backend workflow gap is discovered
- 出现系统架构改进机会 / A system architecture improvement opportunity appears

---

# 任务分类 / Task Classification

**任务类型必须按编号区间判断，不按文件名片段。**

| 范围 | 类别 | 调用规则 |
|------|------|----------|
| 00001–09999 | 功能开发 / Feature Development | `.claude/rules/01_workflow.md` (ADP) |
| 10101–19999 | Bug 修复 / Bug Fix | `.claude/rules/02_debug.md` (8D) |
| 20101–29999 | 重构 / Refactoring | `.claude/rules/01_workflow.md` (ADP) |
| 30101–39999 | 测试 / Testing | `.claude/rules/01_workflow.md` (ADP) |

**执行器分配**（来自 `.claude/rules/05_task_convention.md`）：

| 任务类型 | 条件 | 执行者 |
|---------|------|--------|
| 重构任务 (20101-29999) | 始终 | Codex |
| 测试任务 (30101-39999) | 始终 | Claude Code |
| Bug 修复 (P0/P1 恶性) | 始终 | Claude Code |
| 简化任务 | 始终 | Claude Code |
| 功能任务 (00001-09999) | 前端设计大改 | Claude Code |
| 功能任务 (00001-09999) | 后端/前端实现 | Codex |
| Bug 修复 (普通) | 不涉及架构变更 | Codex |

**简化任务判定标准**（来自 `.claude/rules/05_task_convention.md`）：
- 参数类型不匹配修复
- API 调用参数提取错误
- 简单函数签名修正
- docstring 更新
- 文档同步
- 单文件/单函数修改

**恶性 Bug 判定**：
- P0：系统无法运行、数据损坏风险
- P1：核心功能损坏、API 不可用、工作流阻塞

---

# 自动提示词编号 / Automatic Prompt Numbering

系统必须根据任务类型选择正确的编号范围（必须使用5位格式）：

| 任务类型 / Task Type | 编号范围 / Number Range |
|---------------------|----------------------|
| 功能开发 / Feature Development | 00001–09999 |
| Bug 修复 / Bug Fix | 10101–19999 |
| 重构 / Refactoring | 20101–29999 |
| 测试 / Testing | 30101–39999 |

**编号分配规则**：

为避免频繁扫描 archive 目录，系统使用 `promptsRec/.sequence` 文件维护编号计数器。

1. **读取计数器**: 读取 `promptsRec/.sequence` 文件，根据任务类型获取对应的计数器值：
   - 功能开发 → `feature_next`
   - Bug 修复 → `bugfix_next`
   - 重构 → `refactor_next`
   - 测试 → `test_next`
2. **分配编号**: 使用当前计数器值作为新提示词的编号
3. **更新计数器**: 使用 replace_all 模式原子递增 `.sequence` 中的计数器

**注意**: `.sequence` 文件是编号的唯一真实来源，严禁扫描 archive 或 active 目录来确定编号。

---

# 提示词生成标准 / Prompt Generation Standard

生成的提示词必须遵循确切的项目规范。

Generated prompts must follow the exact project specification.

### 生成前校验 / Pre-Generation Validation

**生成前必须校验以下内容**：

1. 目标文档是否真实存在（`docs/*.md`）
2. 引用规则文件是否真实存在（`.claude/rules/*.md`）
3. 目标代码文件是否真实存在（`backend/`、`frontend/` 路径）
4. 编号是否来自 `.sequence`
5. 执行器是否与 `.claude/rules/05_task_convention.md` 一致
6. 如果是简化任务，是否根本不该生成 prompt
7. 代码片段引用是否遵循 `05_task_convention.md` 指引（不得内嵌、路径可定位）

**如果校验失败，拒绝生成 prompt 并说明原因。**

---

提示词头部（必须使用5位编号）：

Prompt Header (must use 5-digit numbering):

Primary Executor: <Agent>
Task Type: <Feature Development | Bug Fix | Refactoring | Testing>
Priority: <P0 | P1 | P2>
Stage: <5-digit Prompt Number>
Goal: <One-line description>
Dependencies: <"None" or list of prompt numbers that must complete first>
Execution: RUNPROMPT

---

### 类型特定章节要求 / Type-Specific Section Requirements

#### Bug 修复 (10101-19999) — 必须使用 8D 章节

| 章节 | 内容 | 审核 |
|------|------|------|
| D1 | 团队分工 (Reviewer, Coder, Architect) | - |
| D2 | 问题描述 (5W2H) | - |
| D3 | 临时遏制措施 (Containment) | **→ 评分审核** |
| D4 | 根因分析 (5 Whys) | - |
| D5 | 永久对策 + 防退化宣誓 | **→ 评分审核** |
| D6 | 实施验证 (Implementation) | **→ 评分审核** |
| D7 | 预防复发 (Prevention) | - |
| D8 | 归档复盘 (Documentation) | - |

> **D3/D5/D6 必须由 reviewer 评分审核，评分维度与门槛见 `.claude/rules/02_debug.md`。**

#### 功能开发 (00001-09999) / 重构 (20101-29999) — 必须使用 ADP 章节

| 阶段 | 内容 | 审核 |
|------|------|------|
| Phase 1 | PRD 业务需求分析 | - |
| Phase 2 | Data 数据流转审视 | - |
| Phase 3 | Architecture 架构设计 | - |
| Phase 4 | Execution 精确执行 + tester E2E 验证 | **→ tester 验证** |

> **Phase 4 完成后必须通知 `tester` 执行 E2E 验证。**

#### 测试任务 (30101-39999) — 必须使用测试章节

| 章节 | 内容 |
|------|------|
| Test Scope | 测试范围和目标 |
| Test Strategy | 测试策略（单元/集成/E2E） |
| Test Cases | 测试用例列表 |
| Pass Criteria | 通过标准 |
| Test Artifacts | 测试产物（报告、覆盖率） |

---

### 通用章节（所有类型必须包含）

| 章节 | 内容 |
|------|------|
| Context / 上下文 | 任务背景和动机 |
| Required References / 必需参考 | 代码文件、文档、API 契约 |
| Code Snippet Reference / 代码片段引用 | 目标代码文件路径（不得内嵌，详见 `05_task_convention.md`） |
| Constraints / 约束条件 | 限制和边界条件 |
| Completion Criteria / 完成标准 | 可验收的完成标准 |

---

优先级定义 / Priority Definitions:

- P0: 安全漏洞、权限漏洞、数据完整性风险
- P1: 核心逻辑正确性、关键路径测试缺失
- P2: 代码质量、重构、用户体验改进

---

# Bug 调查规则 / Bug Investigation Rule

如果任务是 bug 修复，生成的提示词必须要求代理：

1. 检查后端日志 / Inspect backend logs
2. 检查相关源代码模块 / Inspect relevant source code modules
3. 检查真实数据库架构 / Inspect real database schema
4. 在修改代码前确定根本原因 / Identify the root cause before modifying code

代码片段引用仅限于 Schema 定义和字段常量，
具体业务逻辑实现代码应让执行者直接读源码理解。

---

# 功能集成规则 / Feature Integration Rule

如果任务是功能：

- 与当前架构集成 / Integrate with the current architecture
- 尽可能重用现有组件 / Reuse existing components whenever possible
- 避免不必要的重新设计 / Avoid unnecessary redesign

---

# 输出格式 / Output Format

输出必须始终结构化为：

文件名：promptsRec/active/<prompt_name>.md
执行模型：<Agent>

Then output the full prompt content.

---

---

## 与相邻技能的边界 / Boundary with Adjacent Skills

| 维度 | 本技能 | prompt-generator |
|------|--------|-------------------|
| 输入 | 结构化问题检测（错误日志、UI 问题等） | 自由文本需求描述 |
| 输出 | 自动编号的批量任务队列 | 单个提示词文件 |
| 使用场景 | 自动检测触发、流水线集成 | 单次临时任务、用户触发 |
| 触发方式 | 自动检测 + 手动调用 | 手动调用 |

---

# 重要约束条件 / Important Constraints

系统不得：

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
- 生成引用不存在的文档或代码文件的提示词

---

# 完成标准 / Completion Criteria

在以下情况下技能被视为成功：

1. 检测到的问题被转换为标准化提示词 / A detected problem is converted into a standardized prompt
2. 提示词遵循项目开发规则 / The prompt follows project development rules
3. 提示词可以立即由 RUNPROMPT 执行 / The prompt can be executed immediately by RUNPROMPT
4. 提示词执行后开发管道可以自动继续 / The development pipeline can continue automatically after prompt execution
