---
name: prompt-generator
executor: Claude Code
auto_invoke: false
depends_on: []
triggers: []
rules_ref:
  - .claude/rules/01_workflow.md
  - .claude/rules/02_debug.md
  - .claude/rules/03_hotfix.md
  - .claude/rules/05_task_convention.md
version: 1.0.0
---

# 提示词生成器技能 / Prompt Generator Skill

**规则约束**: 本技能生成提示词时，根据任务类型调用相应规则：
- 功能开发/重构/测试 → `.claude/rules/01_workflow.md` (ADP 四阶段开发协议)
- Bug 修复/回归问题 → `.claude/rules/02_debug.md` (8D 问题解决协议)
- 生产环境紧急修复 → `.claude/rules/03_hotfix.md` (热修复 SOP)
- 编号约定 → `.claude/rules/05_task_convention.md`

## 目的 / Purpose

本技能使 AI 代理能够生成符合项目 AI 驱动开发工作流的标准化开发提示词。/ This skill enables AI agents to generate standardized development prompts that comply with the project's AI-driven development workflow.

生成的提示词必须遵循项目的提示词规范，并且必须可以直接在 `promptsRec/active/` 目录中使用。/ The generated prompts must follow the project's prompt specifications and must be directly usable in the `promptsRec/active/` directory.

---

# 何时使用此技能 / When to Use This Skill

在以下情况下使用此技能：

- 需要实现新功能 / A new feature needs to be implemented
- 在浏览器调试中发现 bug / A bug is discovered during browser debugging
- 需要改进 UI / A UI improvement is required
- 发现工作流改进需求 / A workflow improvement is identified
- 需要扩展后端能力 / A backend capability must be extended
- 需要调查运行时问题 / Runtime issues must be investigated

---

# 开发协议与流程规范 / Development Protocols

**所有协议正文见 `.claude/rules/` 目录，技能文件只引用不复制。**

| 任务类型 | 适用协议 | 规则文件 |
|----------|---------|----------|
| 功能开发 (00001-09999) | ADP Protocol | `.claude/rules/01_workflow.md` |
| UI 改进 / 前端设计 | ADP Protocol | `.claude/rules/01_workflow.md` |
| 架构重构 (20101-29999) | ADP Protocol | `.claude/rules/01_workflow.md` |
| 测试任务 (30101-39999) | ADP Protocol | `.claude/rules/01_workflow.md` |
| Bug 修复 (10101-19999) | 8D Protocol | `.claude/rules/02_debug.md` |
| 回归问题 | 8D Protocol | `.claude/rules/02_debug.md` |
| 生产环境紧急修复 | HOTFIX SOP | `.claude/rules/03_hotfix.md` |

---

# 提示词命名规则 / Prompt Naming Rules

| Range   | Category              | Example                                  |
|---------|-----------------------|------------------------------------------|
| 00001–09999 | Feature Development   | `00017_order_list_ui_migration.md`        |
| 10101–19999 | Bug Fix / Security Fix| `10101_bug_tool_search_request_routing.md` |
| 20101–29999 | Refactoring / Tech Debt| `20101_refactor_split_tool_io_service.md` |
| 30101–39999 | Testing / Quality     | `30101_workflow_state_machine_tests.md`    |

---

# 提示词输出格式 / Prompt Output Format

**AI 必须将生成的提示词实际写入 `promptsRec/active/` 目录，而不是仅输出内容摘要。**

输出必须始终包含：
1. 文件名 / File name (格式: `promptsRec/active/<5-digit-number>_<description>.md`)
2. 执行模型 / Executor model
3. 完整的提示词内容 / Full prompt content

---

# 提示词头部格式 / Prompt Header Format

每个生成的提示词必须以以下头部开头：

```
Primary Executor: <Agent>
Task Type: <Feature Development | Bug Fix | Refactoring | Testing>
Priority: <P0 | P1 | P2>
Stage: <5-digit Prompt Number>
Goal: <One-line description>
Dependencies: <"None" or list of prompt numbers that must complete first>
Execution: RUNPROMPT
```

---

# 必需提示词章节 / Required Prompt Sections

每个生成的提示词必须包含以下章节：

Context / 上下文
Required References / 必需参考
Code Snippet Reference / 代码片段引用
Core Task / 核心任务
Required Work / 必需工作
Constraints / 约束条件
Completion Criteria / 完成标准

---

# 问题分析要求 / Pre-Generation Analysis

在生成提示词之前，AI 必须：

1. 分析问题 / Analyze the problem thoroughly
2. 确定任务类别和编号范围（按编号区间，不按文件名片段）:
   - 功能开发 / Feature Development → feature_next (00001–09999)
   - Bug 修复 / Bug Fix / Security Fix → bugfix_next (10101–19999)
   - 重构/技术债 / Refactoring / Tech Debt → refactor_next (20101–29999)
   - 测试/质量 / Testing / Quality → test_next (30101–39999)

   **编号获取**: 从 `promptsRec/.sequence` 文件读取对应计数器

3. 确定正确的执行器（来自 `.claude/rules/05_task_convention.md`）
4. 识别依赖关系 / Identify dependencies on other prompts
5. 分配优先级 / Assign priority:
   - P0: 安全漏洞、权限漏洞、数据完整性风险
   - P1: 核心逻辑正确性、关键路径测试缺失
   - P2: 代码质量、重构、用户体验改进

**执行器规则**（来自 `.claude/rules/05_task_convention.md`）：

| Executor     | Scope                                                        |
|--------------|--------------------------------------------------------------|
| Gemini       | Frontend tasks: UI, UX, component styling, page layout       |
| Codex        | Backend tasks: API, service logic, database queries           |
| Claude Code  | Architecture tasks: refactoring, cross-cutting concerns, RBAC design, workflow redesign, multi-file structural changes |

---

## 生成前校验 / Pre-Generation Validation

**生成前必须校验以下内容**：

1. 目标文档是否真实存在（`docs/*.md`）
2. 引用规则文件是否真实存在（`.claude/rules/*.md`）
3. 目标代码文件是否真实存在（`backend/`、`frontend/` 路径）
4. 编号是否来自 `.sequence`
5. 执行器是否与 `.claude/rules/05_task_convention.md` 一致
6. 是否属于不应生成 prompt 的简化任务
7. 代码片段引用是否遵循 `05_task_convention.md` 指引（不得内嵌、路径可定位）

**如果校验失败，拒绝生成 prompt 并说明原因。**

---

# Bug 提示词规则 / Bug Prompt Rules (10101–19999)

如果问题是 bug：

- 提示词编号必须在 10101–19999 范围内
- 修改前必须进行调查
- 提示词必须指示代理检查真实代码库和数据库架构
- 提示词必须包含优先级 (P0/P1/P2)

提示词不得假设：
- 数据库字段名
- 后端 API 结构
- 工作流状态

提示词中的代码引用仅限于 Schema 定义和字段常量，
不得包含具体业务逻辑实现代码。

---

# 功能提示词规则 / Feature Prompt Rules (00001–09999)

如果任务是功能：

- 提示词编号必须在 00001-09999 范围内
- 提示词必须与现有架构集成
- 提示词不得重新设计稳定的子系统
- 提示词必须包含优先级 (P0/P1/P2)

提示词中的代码引用仅限于架构约束和模式骨架，
不得包含具体业务逻辑实现代码。

---

# 重构提示词规则 / Refactoring Prompt Rules (20101–29999)

如果任务是重构：

- 提示词编号必须在 20101-29999 范围内
- 必须保留所有现有行为 (无功能变更)
- 必须包含重构前后的结构描述
- 提示词必须包含优先级 (P0/P1/P2)

---

# 测试提示词规则 / Testing Prompt Rules (30101–39999)

如果任务是测试：

- 提示词编号必须在 30101-39999 范围内
- 必须指定测试框架和断言策略
- 必须定义覆盖率目标
- 提示词必须包含优先级 (P0/P1/P2)
- 必须包含 Test Scope、Test Strategy、Test Cases、Pass Criteria 章节

---

# 约束条件 / Constraints

AI 不得：

- 仅输出提示词内容而不生成实际文件
- 生成不完整的提示词
- 跳过必需章节

---

## 与相邻技能的边界 / Boundary with Adjacent Skills

| 维度 | 本技能 | auto-task-generator |
|------|--------|-------------------|
| 输入 | 自由文本需求描述或问题分析 | 结构化问题检测 |
| 输出 | 单个提示词文件 | 批量任务队列/自动编号 |
| 使用场景 | 单次临时任务、用户触发 | 自动检测触发、流水线集成 |
| 触发方式 | 手动调用 | 自动检测 + 手动调用 |
- 无正当理由重新设计稳定架构
- 假设数据库架构
- 不检查就假设后端 API
- 生成引用不存在的文档或代码文件的提示词
- 违反编号规则
- 跳过优先级声明 (P0/P1/P2)
- 跳过依赖声明 (当有依赖时)

---

# 完成标准 / Completion Criteria

生成的提示词只有在以下情况下才被视为有效：

1. 遵循提示词格式 / It follows the prompt format
2. 遵守编号规则:
   - 00001–09999 = Feature Development
   - 10101–19999 = Bug Fix / Security Fix
   - 20101–29999 = Refactoring / Tech Debt
   - 30101–39999 = Testing / Quality
3. 包含所有必需章节:
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
4. 包含具体的验收测试 (非模糊)
5. 正确声明依赖关系
6. 可以由 RUNPROMPT 直接执行
